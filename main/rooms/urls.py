from django.urls import path

from . import views

app_name = 'rooms'

urlpatterns = [
    path('create/<str:username>/<str:room_name>', views.create_room, name='index'),
    path('delete/<str:room_code>', views.delete_room, name='delete'),
    path('room/all/<str:username>', views.get_all_rooms, name='all'),
    path('room/<str:room_code>', views.get_room, name='get'),
    path('participant/create/<str:room_code>', views.add_participant, name='create'),
    path('participant/delete/<str:room_code>/<str:name>', views.delete_participant, name='delete'),
    path('partcipant/all/<str:room_code>', views.get_all_participants, name='all'),
    path('pairings/create/<str:room_code>', views.create_pairings, name='create_pairing'),
    path('pairings/all/<str:room_code>', views.get_all_pairings, name='all_pairings'),
    path('pairings/<str:room_code>/<str:name>', views.get_pairings, name='get_pairings'),
    # path('DONT-USE-THIS-ENDPOINT-PLEASE', views.delete_all_rooms)
]