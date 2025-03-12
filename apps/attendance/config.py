from django.apps import AppConfig

class AttendanceConfig(AppConfig):
    name = 'apps.attendance'
    label = 'apps_attendance'  # Use a unique label for the app
    default_auto_field = 'django.db.models.BigAutoField'