from rest_framework import serializers
from geo.models import Address, Country, City, Region, PostalCode


class AddressCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('name', )


class AddressRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('name', )


class AddressCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('name', )


class AddressPostalCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostalCode
        fields = ('code', )

class AddressSerializer(serializers.ModelSerializer):
    country = AddressCountrySerializer()
    city = AddressCitySerializer()
    region = AddressRegionSerializer()
    postal_code = AddressPostalCodeSerializer()

    class Meta:
        model = Address
        fields = ('uuid', 'street', 'city', 'region', 'postal_code', 'country', )


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        exclude = ('location', )


class PostalCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostalCode
        exclude = ('location', )
