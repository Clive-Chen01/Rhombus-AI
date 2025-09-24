from django.urls import path
from .views import upload_file, transform_data, llm_preview


urlpatterns = [
    path("upload", upload_file, name="upload"),
    path("transform", transform_data, name="transform"),
    path("llm-preview", llm_preview, name="llm-preview")
]