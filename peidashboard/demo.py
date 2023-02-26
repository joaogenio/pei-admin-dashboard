import numpy as np
import cv2
import dlib
import math
import json
import onnxruntime as rt
import sys
import os
from time import sleep
from os.path import basename
#from peidashboard import settings as sett
#from django.core.management import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE","peidashboard.settings")
import django 
django.setup()
from dashboard.models import *
#from peidashboard.dashboard import setup
#setup()

# Confidence threshold for Face Recognition
RECOGNITION_CONFIDENCE = 0.6

# Maximum angle of face rotation for estimating attention since dlib can't keep detecting the face after a certain point 
MAX_ANGLE = 30

# Emotions
EMOTION_CLASSES = {0: "Neutral", 1: "Happiness", 2: "Surprise", 3: "Sadness", 4: "Anger", 5: "Disgust", 6: "Fear", 7: "Contempt"}

# Converts dlib format to numpy format
def shape_to_np(shape):
	landmarks = np.zeros((68,2), dtype = int)
	for i in range(0,68):
		landmarks[i] = (shape.part(i).x, shape.part(i).y)

	return landmarks


# Converts dlib format to opencv format
def rect_to_bb(rect):
	x = rect.left()
	y = rect.top()
	w = rect.right() - x
	h = rect.bottom() - y
	
	return (x, y, w, h)


# Face Detection
def detect_face(image, detector, predictor):
	gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	rects = detector(gray_image, 1)
	shape = []
	bb = []
	raw_shape = []

	for (z, rect) in enumerate(rects):
		if rect is not None and rect.top() >= 0 and rect.right() < gray_image.shape[1] and rect.bottom() < gray_image.shape[0] and rect.left() >= 0:
			predicted = predictor(gray_image, rect)
			shape.append(shape_to_np(predicted))
			(x, y, w, h) = rect_to_bb(rect)
			bb.append((x, y, x+w, y+h))
			raw_shape.append(predicted)

	return shape, bb, raw_shape

# Initializes a new dictionary for each ID
def init_dict(ids, key, candidate_descriptor):
	ids[key] = {}
	ids[key]['Descriptor'] = candidate_descriptor
	ids[key]['Attention'] = 0
	ids[key]['Emotions'] = {}
	for i in EMOTION_CLASSES:
		ids[key]['Emotions'][EMOTION_CLASSES[i]] = 0
	ids[key]['Frames'] = 1

# Face Recognition
# Stores descriptors to a dictionary everytime a new person appears 
def face_recognition(frame, shape, ids, facerec):
	candidate = dlib.get_face_chip(frame, shape)   
	candidate = facerec.compute_face_descriptor(candidate)
	candidate_descriptor = np.asarray(candidate)
	jsonString = json.dumps(candidate_descriptor.tolist())

	if len(ids) == 0:
		db_person = Person(descriptor=jsonString)
		db_person.save()
		person = 'ID ' + str(db_person.id)
		init_dict(ids, person, candidate_descriptor)
		print("    pessoa nova:", person)
		return person

	else:
		d_values = {}
		for reference in ids:
			dist = np.linalg.norm(ids[reference]['Descriptor'] - candidate_descriptor)
			d_values[reference] = dist

		best_comparison = min(d_values, key = d_values.get)
		confidence = d_values[best_comparison]

		if confidence < RECOGNITION_CONFIDENCE:
			print("    pessoa existe")
			ids[best_comparison]['Frames'] += 1
			return best_comparison
		else:
			db_person = Person(descriptor=jsonString)
			db_person.save()
			person = 'ID ' + str(db_person.id)
			init_dict(ids, person, candidate_descriptor)
			print("    pessoa nova:", person)
			return person


# Estimates head pose by transforming the 2D facial landmarks into 3D world coordinates and calculating the Euler angles
def head_pose(size, features):
	image_points = np.array([
							features[30],     # Nose 
							features[36],     # Left eye 
							features[45],     # Right eye
							features[48],     # Left Mouth corner
							features[54],     # Right mouth corner
							features[8]		  # Chin
							], dtype="double")

	# 3D model points.
	model_points = np.array([
							(0.0, 0.0, 0.0),             # Nose
							(-165.0, 170.0, -135.0),     # Left eye
							(165.0, 170.0, -135.0),      # Right eye 
							(-150.0, -150.0, -125.0),    # Left Mouth corner
							(150.0, -150.0, -125.0),     # Right mouth corner
							(0.0, -330.0, -65.0)		 # Chin
							])

	# Camera internals
	focal_length = size[1]
	center = (size[1]/2, size[0]/2)
	camera_matrix = np.array(
							[[focal_length, 0, center[0]],
							[0, focal_length, center[1]],
							[0, 0, 1]], dtype = "double"
							)

	dist_coeffs = np.zeros((4,1)) # Assuming no lens distortion
	(success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)

	rv_matrix = cv2.Rodrigues(rotation_vector)[0]

	proj_matrix = np.hstack((rv_matrix, translation_vector))
	eulerAngles = cv2.decomposeProjectionMatrix(proj_matrix)[6] 

	pitch, yaw, roll = [math.radians(x) for x in eulerAngles]
	pitch = math.degrees(math.asin(math.sin(pitch)))
	roll = -math.degrees(math.asin(math.sin(roll)))
	yaw = math.degrees(math.asin(math.sin(yaw)))

	return (pitch, roll, yaw)


# Assumes that frontal faces are paying attention using the pitch and yaw
def calculate_attention(ids, key, eulerAngles, crop):
	angle_average = min((abs(eulerAngles[0]) + abs(eulerAngles[2]))/2, MAX_ANGLE) # Only pitch and yaw matter

	current_attention = (MAX_ANGLE - angle_average)/MAX_ANGLE # Normalization: [0, MAX_ANGLE] -> [0,1]
	ids[key]['Attention'] +=  current_attention
	id=key.split()
	content=crop.content
	doc = Document.objects.all().filter(docname=content).first()
	stat = Stats.objects.all().filter(person=id[-1]).filter(content=doc).filter(agent=crop.agentid).first()
	if stat is not None:
		print("    stat existe: " + str(stat.id))
		stat.attention += current_attention
	else:
		person = Person.objects.get(pk = id[-1])
		stat = Stats(person=person,content=doc,agent=crop.agentid,attention=current_attention)
		print("    novo stat: " + str(stat.id))
	stat.save()


# Performs emotion recognition
def emotion_recognition(face, ids, key, sess, input_name, output_name, crop):
	input_shape = (1, 1, 64, 64)
	img = cv2.resize(face, (64,64), cv2.INTER_AREA)
	img_data = np.array(img, dtype=np.float32)
	img_data = np.resize(img_data, input_shape)
	res = sess.run([output_name], {input_name: img_data})
	prediction = int(np.argmax(np.array(res).squeeze(), axis=0))
	emotion = EMOTION_CLASSES[prediction]
	ids[key]['Emotions'][emotion] += 1
	id=key.split()
	content=crop.content
	doc = Document.objects.all().filter(docname=content).first()
	stat = Stats.objects.all().filter(person=id[-1]).filter(content=doc).filter(agent=crop.agentid).first()
	if stat is not None:
		if emotion=="Neutral":
			stat.neutral+=1
		elif emotion=="Happiness":
			stat.happiness+=1
		elif emotion=="Surprise":
			stat.suprise+=1
		elif emotion=="Sadness":
			stat.sadness+=1
		elif emotion=="Anger":
			stat.anger+=1
		elif emotion=="Disgust":
			stat.disgust+=1
		elif emotion=="Fear":
			stat.fear+=1
		elif emotion=="Contempt":
			stat.contempt+=1
		stat.frames+=1
		stat.save()
	return emotion


# Displays bounding boxes, landmarks and the face recognition prediction on the frame
def display(key, bb, shape, emotion, frame):
	cv2.rectangle(frame, (bb[0], bb[1]), (bb[2], bb[3]), (0, 255, 0), 2)
	for (x, y) in shape:
		cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)

	pos_x = bb[0]-10 
	pos_y = bb[1]-10
	cv2.putText(frame, str(key), (pos_x, pos_y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), thickness=1, lineType=2)

	pos_x = bb[0]-10 
	pos_y = bb[3]+20
	cv2.putText(frame, emotion, (pos_x, pos_y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), thickness=1, lineType=2)


# Stores data for each id to a json file
def save_data(ids):
	save_dict = {}
	for person in ids:
		save_dict[person] = {}
		save_dict[person]['Attention'] = ids[person]['Attention'] / ids[person]['Frames']
		save_dict[person]['Emotions'] = ids[person]['Emotions']
		for i in EMOTION_CLASSES:
			save_dict[person]['Emotions'][EMOTION_CLASSES[i]] /= ids[person]['Frames']

	with open('/home/genix/Documents/pei-admin-dashboard/peidashboard/stats.json', 'w') as file:
		json.dump(save_dict, file,  indent=4)


def main():
	print("inicio da main")
	# load models
	detector = dlib.get_frontal_face_detector()
	predictor = dlib.shape_predictor('/home/genix/Documents/pei-admin-dashboard/peidashboard/shape_predictor_68_face_landmarks.dat')
	# CUDA is required to use this model for face recognition
	facerec = dlib.face_recognition_model_v1("/home/genix/Documents/pei-admin-dashboard/peidashboard/dlib_face_recognition_resnet_model_v1.dat")
	# Model for emotion recognition: Barsoum, Emad, et al. "Training deep networks for facial expression recognition with crowd-sourced label distribution."
	sess = rt.InferenceSession('/home/genix/Documents/pei-admin-dashboard/peidashboard/emotions.onnx')
	input_name = sess.get_inputs()[0].name
	output_name = sess.get_outputs()[0].name

	print("preencher dicionario")
	people = Person.objects.all()
	ids = {}
	for person in people:
		id = "ID "+str(person.id)
		aux = json.loads(person.descriptor)
		descriptor = np.asarray(aux)
		init_dict(ids,id, descriptor)
	print("acabou dicionario (" + str(len(ids)) + " pessoas)")

	while True:
		while Crop.objects.all().count() == 0:
			print(".", end="", flush=True)
			sleep(1)
		dir = "/home/genix/Documents/pei-admin-dashboard/peidashboard/media_cdn/"
		crops = Crop.objects.all()
		print("sacar crops")
		for crop in crops:
			print("\ncada crop")
			if crop.cropfile != "":
				print("  crop nao vazio:", crop.cropfile)
				frame = cv2.imread("/home/genix/Documents/pei-admin-dashboard/peidashboard/media_cdn/%s" %crop.cropfile) 
				dims = frame.shape # Replace dims for the image.shape sent from the raspberry (needed for head_pose())
				print("  face detection")
				shape, bb, raw_shape = detect_face(frame, detector, predictor) # Shape and cropped face comes from the raspberry

				for i in range(len(bb)):
					print("  face recognition")
					key = face_recognition(frame, raw_shape[i], ids, facerec)
					eulerAngles = head_pose(dims, shape[i])
					print("  attention")
					calculate_attention(ids, key, eulerAngles, crop)
					# This is the face sent from the raspberry, needs to be converted to grayscale for emotion recognition
					face = cv2.cvtColor(frame[bb[i][1]:bb[i][3], bb[i][0]:bb[i][2]], cv2.COLOR_BGR2GRAY)
					print("  emotions")
					emotion = emotion_recognition(face, ids, key, sess, input_name, output_name, crop)
					#display(key, bb[i], shape[i], emotion, frame) # this function is just for visualization and debugging, should be commented 

				save_data(ids)

				#cv2.imshow('Frame',frame)
				os.remove(os.path.join(dir,crop.cropfile.name))
				crop.delete()

if __name__ == "__main__":
	main()