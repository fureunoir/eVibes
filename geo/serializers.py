from rest_framework import serializers

from geo.models import Address


class AddressAutocompleteInputSerializer(serializers.Serializer):
    q = serializers.CharField(
        required=True
    )
    limit = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=10,
        default=5
    )


class AddressSuggestionSerializer(serializers.Serializer):
    display_name = serializers.CharField()
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    address = serializers.DictField(child=serializers.CharField())


class AddressSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(source="location.y", read_only=True)
    longitude = serializers.FloatField(source="location.x", read_only=True)

    class Meta:
        model = Address
        fields = [
            "uuid",
            "street",
            "district",
            "city",
            "region",
            "postal_code",
            "country",
            "latitude",
            "longitude",
            "raw_data",
            "api_response",
            "user",
        ]
        read_only_fields = [
            "latitude",
            "longitude",
            "raw_data",
            "api_response",
        ]


class AddressCreateSerializer(serializers.ModelSerializer):
    raw_data = serializers.CharField(
        write_only=True,
        max_length=512,
    )

    class Meta:
        model = Address
        fields = ["raw_data", "user"]

    def create(self, validated_data):
        raw = validated_data.pop("raw_data")
        return Address.objects.create(raw_data=raw, **validated_data)
