from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def salud(request):
    return JsonResponse({"status": "ok", "servicio": "bosphorus-zf-backend"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/salud/", salud),
    path("api/auth/", include("identidad.urls")),
]
