#!/bin/bash

LOGIN_URL=http://dashboard.pei/api-auth/login/?next=/api/
YOUR_USER='genix'
YOUR_PASS='genix'
COOKIES=cookies.txt
CURL_BIN="curl -c $COOKIES -b $COOKIES -e http://dashboard.pei/"

echo "Django Auth: get csrftoken ..."
$CURL_BIN $LOGIN_URL > /dev/null
TOKEN="$(grep csrftoken $COOKIES | sed 's/^.*csrftoken\s*//')"
DJANGO_TOKEN="csrfmiddlewaretoken=$TOKEN"
#&sessionid=$(grep sessionid $COOKIES | sed 's/^.*sessionid\s*//')"

CSRFTOKEN="csrftoken=$TOKEN"
#SESSIONID="$(grep sessionid $COOKIES | sed 's/^.*sessionid\s*//')"
echo $CSRFTOKEN
echo $TOKEN

echo " perform login ..."
$CURL_BIN \
    -d "$DJANGO_TOKEN&username=$YOUR_USER&password=$YOUR_PASS" \
    -X POST $LOGIN_URL

echo " do something while logged in ..."
echo $DJANGO_TOKEN
$CURL_BIN \
    -H "X-CSRFToken: $TOKEN" \
    -H "Cookie: csrftoken=$TOKEN" \
    -u genix:genix \
    -F "cropfile=@/home/genix/Downloads/exceptions.s" \
    -F "content='nuggets.png'" \
    -X POST http://dashboard.pei/api/crops/
    # -F $DJANGO_TOKEN 

    # -d "$DJANGO_TOKEN&..." \
    # -X POST https://yourdjangowebsite.com/whatever/

echo ""
echo " logout"
rm $COOKIES
