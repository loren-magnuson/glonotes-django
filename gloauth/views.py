from django.shortcuts import render, redirect
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from gloauth.models import GloNote
from geopy.distance import vincenty
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from gloauth.models import User
from gloauth.serializers import UserSerializer
from rest_framework import status
import os
import time
AUTOMATIC_UPDATES = 'true'


def checkForNewNotes(request, coordinates):


    notes_found = {}
    note_count = 0
    gloNotes = GloNote.objects.all()
    for note in gloNotes:

        note_coordinates = (note.coordinates.split(',')[0], note.coordinates.split(',')[1])
        distance_between = vincenty(coordinates, note_coordinates).meters

        if distance_between < 3000:
            note_count += 1
            note_dict = {}
            note_dict['textMessage'] = note.textMessage
            note_dict['subject'] = note.subject
            note_dict['note_id'] = note.id
            note_dict['author'] = note.author.username
            note_dict['latitude'] = note.coordinates.split(',')[0]
            note_dict['longitude'] = note.coordinates.split(',')[1]
            if note.image_filename is None:
                note_dict['image_filename'] = "None"
            else:
                note_dict['image_filename'] = note.image_filename

            notes_found["note%s" % (note_count)] = note_dict

    if len(notes_found) > 0:
        return  notes_found

    else:
        return 'NO NEW MESSAGES'


class AuthView(APIView):

    """
    Authentication is needed for this methods
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):

        return Response({'detail': "AUTHENTICATED"})

    def post(self, request, format=None):

        if 'latitude' in request.POST and 'longitude' in request.POST:
            latitude = request.POST['latitude']
            longitude = request.POST['longitude']
            request.user.userprofile.last_known_coordinates = "%s,%s" % (latitude, longitude)
            request.user.userprofile.save()

            if AUTOMATIC_UPDATES == 'true':
                return redirect('/auth/get_notes/?latitude=%s&longitude=%s' % (latitude, longitude))
            else:
                return Response({'detail': 'CURRENT_LAT: %s CURRENT LONG: %s' % (latitude, longitude)})

        else: return Response({'detail':'COORDINATES MISSING'})



class PostNoteView(APIView):

    """
    Authentication is needed for this view
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser,)

 #   def get(self, request, format=None):
     #   return Response({'detail': "AUTHENTICATED"})

    def post(self, request, format=None):

        if 'latitude' in request.POST and 'longitude' in request.POST:

            if 'subject' in request.POST and 'textMessage' in request.POST:
                gloNote = GloNote()
                gloNote.subject = request.POST['subject']
                gloNote.textMessage = request.POST['textMessage']
                gloNote.author = request.user
                gloNote.coordinates = "%s,%s" % (request.POST['latitude'], request.POST['longitude'])

                if 'uploaded_image' in request.POST:
                    my_file = request.FILES['uploaded_image']

                    ## TODO works for linux
                  # filename = '%s/%s/glonote_photo_%s.jpg' % (settings.MEDIA_ROOT, request.user, timestamp)

                    ## TODO works for windows


                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                    filename = "glonote_photo_%s.jpg" % timestamp
                    #filepath = '%s\\media\\%s\\%s' % (os.getcwd(), request.user, filename)
                    filepath = '%s/%s/%s' % (settings.MEDIA_ROOT, request.user, filename)
                    with open(filepath, 'wb+') as temp_file:
                        for chunk in my_file.chunks():
                            temp_file.write(chunk)
                    gloNote.image_filename = filename

                gloNote.save()

                return Response({'detail':'NOTE POSTED'})



        else: return Response({'detail':'IMPROPERLY FORMATTED NOTE'})


class GetNotesView(APIView):

    """
    Authentication is needed for this view
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):

        if 'latitude' in request.GET and 'longitude' in request.GET:
            coordinates = (request.GET['latitude'], request.GET['longitude'])
            notes_found = checkForNewNotes(request, coordinates)
            return Response(notes_found, content_type='application/json')
           # return Response({'detail':notes_found})

        else:
            coordinates = request.user.userprofile.last_known_coordinates
            coordinates = (coordinates.split(',')[0], coordinates.split(',')[1])
            notes_found = checkForNewNotes(request, coordinates)
            return Response(notes_found, content_type='application/json')

           # return Response({'detail':notes_found})

class GetSingleNoteView(APIView):

    """
    Authentication is needed for this view
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        if 'note_id' in request.POST:
            try:
                note = GloNote.objects.get(id=request.POST['note_id'])
                note_json = {}
                note_json['subject'] = note.subject
                note_json['textMessage'] = note.textMessage
                note_json['author'] = note.author.username


                return Response(note_json, content_type='application/json')

            except:
                return Response("NO SUCH NOTE ID" % (request.POST['note_id']), content_type='application/json')

        else:
            return Response("NO NOTE ID RECEIVED" % (request.POST['note_id']), content_type='application/json')


class DeleteNoteView(APIView):

    """
    Authentication is needed for this view
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        if 'note_id' in request.POST:
            try:
                note = GloNote.objects.get(id=request.POST['note_id'])
                return Response(note_json, content_type='application/json')

            except:
                return Response("NO SUCH NOTE ID" % (request.POST['note_id']), content_type='application/json')

            note_json = {}
            note_json['subject'] = note.subject
            note_json['textMessage'] = note.textMessage
            note_json['author'] = note.author.username

        else:
            return Response("NO NOTE ID RECEIVED" % (request.POST['note_id']), content_type='application/json')


class RegisterUser(APIView):
    """
    API endpoint that allows users to be viewed or edited.
    """

    def post(self, request, format=None):
        serialized = UserSerializer(data=request.data)

        if serialized.is_valid():
            User.objects.create_user(
            serialized.data['username'],
            serialized.data['email'],
            serialized.data['password']
        )
            account_created_json = {}
            account_created_json["registration_status"] = "Account created!"
            return Response(account_created_json, status=status.HTTP_201_CREATED)
        else:
            return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)