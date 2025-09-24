from rest_framework import serializers


class UploadResponse(serializers.Serializer):
    columns = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField()
    filename = serializers.CharField()


class TransformRequest(serializers.Serializer):
    natural_language = serializers.CharField()
    replacement = serializers.CharField()
    columns = serializers.ListField(child=serializers.CharField(), required=False)
    # extras
    apply_phone_normalization = serializers.BooleanField(required=False, default=False)
    apply_date_normalization = serializers.BooleanField(required=False, default=False)


class TransformResponse(serializers.Serializer):
    pattern = serializers.CharField()
    explanation = serializers.CharField(allow_null=True)
    columns = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField()