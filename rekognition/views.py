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

app = ClarifaiApp(api_key='aa53cdc859b84d4d95190962e8613c9a')
model = app.models.get('general-v1.3')

import way2sms                  # Importing module to send the alert text messages
message = way2sms.sms('8983050329', 'betheone')  # way2sms credentials
mobile_number = '9011041156'  # Mobile number to which the alert message will be sent


class PredictImageObject(APIView):

    def alert(self):        # This will send the alert message to the number specified
        try:
            message = way2sms.sms('8983050329', 'betheone')
            message.send(mobile_number, 'There is a storage box in the room')
            sent_count = message.msgSentToday()
            print 'Message Sent Count =', sent_count  # 100 messages are free/day
            message.logout()
        except:
            print 'Message sending Failed!'

    def post(self, request):    # this is a post request to post the alert button status and will be responsed with the calculated parameters
        analysis = []
        resp = requests.get('http://192.168.0.102:8080/shot.jpg')
        imgbytes = resp.content
        image = ClImage(file_obj=StringIO(imgbytes))
        response = model.predict([image])
        concepts = response['outputs'][0]['data']['concepts']

        box = 0
        room = 0
        for concept in concepts:
            print concept['name']
            if (concept['name'] == 'box' or concept['name'] == 'cardboard' or concept['name'] == 'container') and request.data['alert'] == 'true':   # send alert message
                self.alert()

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

        if box == 1:
            analysis.append({
                'label': 'storage box',
                'confidence': box_value
            })

        if room == 1:
            analysis.append({
                'label': 'room',
                'confidence': room_value
            })

        while(len(analysis) < 6):
            analysis.append({
                'label': '',
                'confidence': ''
            })

        return Response(analysis)


def PageLoad(request):  # Loads the Object detection site
    if request.method == 'GET':
        return render(request, "video_response.html")
