import os
from django.http import HttpResponse
from django.conf import settings


def service_worker(request):
    sw_path = os.path.join(settings.BASE_DIR, "static", "pwa", "sw.js")
    try:
        with open(sw_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        content = ""
    response = HttpResponse(content, content_type="application/javascript")
    response["Service-Worker-Allowed"] = "/"
    response["Cache-Control"] = "no-cache"
    return response


def manifest_json(request):
    man_path = os.path.join(settings.BASE_DIR, "static", "pwa", "manifest.json")
    try:
        with open(man_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        content = "{}"
    return HttpResponse(content, content_type="application/manifest+json")
