from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf import settings
from gloauth import views



urlpatterns = [
    url(r'^auth/update_coordinates/', views.AuthView.as_view(), name='auth-view'),
    url(r'^auth/post_note/', views.PostNoteView.as_view(), name='post-note-view'),
    url(r'^auth/get_notes/', views.GetNotesView.as_view(), name='get-notes-view'),
    url(r'^auth/get_note/', views.GetSingleNoteView.as_view(), name='get-single-note-view'),
    url(r'^auth/users/register', views.RegisterUser.as_view(), name='register-user-view'),


]


if settings.DEBUG:
    urlpatterns.append(url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}))


urlpatterns = format_suffix_patterns(urlpatterns)


