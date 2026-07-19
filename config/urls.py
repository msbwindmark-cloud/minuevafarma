from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from farmacia.views.pwa_views import service_worker, manifest_json

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sw.js', service_worker, name='service_worker'),
    path('manifest.json', manifest_json, name='manifest_json'),
    path('', include('farmacia.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
