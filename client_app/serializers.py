from rest_framework import serializers


class OuterFileSerializer(serializers.Serializer):
    name = serializers.CharField()
    size = serializers.IntegerField()
    file_hash = serializers.CharField()
    url = serializers.IPAddressField(required=False)
