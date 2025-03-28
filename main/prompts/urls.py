from django.urls import path

from . import views

app_name = 'gestures'

urlpatterns = [
    path('hello-world/<str:interest1>/<str:interest2>', views.hello_world, name='hello_world'),
    path('test/', views.test, name='test'),
]