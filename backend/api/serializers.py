from rest_framework import serializers


class UploadResponse(serializers.Serializer):
    columns = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField()
    filename = serializers.CharField()