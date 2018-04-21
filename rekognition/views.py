# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Third Party App Imports
from rest_framework.views import APIView
from rest_framework.response import Response

from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
from StringIO import *
import requests
import way2sms       # Import this module to send free text message

# Clarifai API Initialization
app = ClarifaiApp(api_key='aa53cdc859b84d4d95190962e8613c9a')
model = app.models.get('general-v1.3')

# Way2SMS settings
message = way2sms.sms('8983050329', 'betheone')  # way2sms credentials
mobile_number = '9011041156'
# Recipient's Mobile number to which the alert message will be sent


class PredictImageObject(APIView):
    # This will send the alert message to the number specified
    def alert(self):
        try:
            message = way2sms.sms('8983050329', 'betheone')
            message.send(mobile_number, 'There is a storage box in the room')
            sent_count = message.msgSentToday()
            print 'Message Sent Count =', sent_count
            # 100 messages are free/day
            message.logout()
        except:
            print 'Message sending Failed!'

    def post(self, request):
        # this is a post request to post the alert button status and
        # will be responded with the calculated parameters
        analysis = []
        # resp = requests.get('http://127.0.0.1:5000/video_feed')
        # Get the image snapshot of video from the Webcam
        # img_bytes = resp.content   # Get the image content (bytes/raw image)
        # image = ClImage(file_obj=StringIO(img_bytes))
        # response = model.predict([image])
        image_path = "./webcam_server/snapshot.jpg"
        response = model.predict_by_filename(filename=image_path)
        concepts = response['outputs'][0]['data']['concepts']
        # Declaring variables to remember that the box or room was detected
        box = 0
        room = 0
        for concept in concepts:
            if (concept['name'] == 'box' or concept['name'] == 'cardboard' or
               concept['name'] == 'container') and request.data['alert'] == 'true':
                self.alert()  # send alert message

            if concept['name'] == 'people' and concept['value'] > 0.95:
                analysis.append({
                    'label': 'person',
                    'confidence': str(concept['value'] * 100)[:5]
                })

            if concept['name'] == 'box' or concept['name'] == 'cardboard' or concept['name'] == 'container':
                box = 1
                box_value = str(concept['value'] * 100)[:5]
                continue

            if concept['name'] == 'room' or concept['name'] == 'indoors':
                room = 1
                room_value = str(concept['value'] * 100)[:5]
                continue

        if box == 1:  # If box or cardboard or container was detected
            analysis.append({
                'label': 'storage box',
                'confidence': box_value
            })

        if room == 1:  # If room or indoors was detected make it as one to room
            analysis.append({
                'label': 'room',
                'confidence': room_value
            })

        # Logic to remove previous data from the table
        while len(analysis) < 6:
            analysis.append({
                'label': '',
                'confidence': ''
            })
        return Response(analysis)


def page_load(request):  # Loads the Object detection site
    if request.method == 'GET':
        return render(request, "home_page.html")
