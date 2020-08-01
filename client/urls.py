from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include

from client import settings
from client_app.tasks import start_ping

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('', include('client_app.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

start_ping()
