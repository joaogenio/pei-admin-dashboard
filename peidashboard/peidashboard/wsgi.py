"""
WSGI config for peidashboard project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

import sys

import time 
import traceback 
import signal 

#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

sys.path.append('/var/www/vhosts/peidashboard') 
# adjust the Python version in the line below as needed 
sys.path.append('/home/genix/.virtualenvs/myenv/lib/python3.6/site-packages') 
 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peidashboard.settings')
 
try: 
    application = get_wsgi_application() 
except Exception: 
    # Error loading applications 
    if 'mod_wsgi' in sys.modules: 
        traceback.print_exc() 
        os.kill(os.getpid(), signal.SIGINT) 
        time.sleep(2.5) 