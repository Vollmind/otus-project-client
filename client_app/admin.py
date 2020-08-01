from django.contrib import admin

# Register your models here.
from client_app.models import File, Storage, Settings

admin.site.register(File)
admin.site.register(Storage)
admin.site.register(Settings)
