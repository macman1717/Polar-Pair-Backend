from django.apps import AppConfig


class PromptsConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "prompts"
