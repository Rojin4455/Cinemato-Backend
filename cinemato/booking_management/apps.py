from django.apps import AppConfig


class BookingManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'booking_management'


    def ready(self):
        import booking_management.signals
        
