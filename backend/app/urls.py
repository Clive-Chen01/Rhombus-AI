from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include

def root(_request):
    return JsonResponse({
        "service": "regex-match-replace-backend",
        "status": "ok",
        "endpoints": ["/api/upload", "/api/transform", "/api/llm-preview"]
    })

urlpatterns = [
    path("", root),                 # ← 新增：根健康页
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]
