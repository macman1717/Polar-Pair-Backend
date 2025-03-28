from django.apps import AppConfig


class RoomsConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "rooms"
