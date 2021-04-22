from rest_framework import serializers
from .models import Street, StreetType, SurfaceType
from rest_framework_gis.serializers import GeoFeatureModelSerializer


class StreetSurfaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurfaceType
        fields = '__all__'


class StreetsSerializer(GeoFeatureModelSerializer):
    street_surface_rating = serializers.SlugRelatedField(
        source='street_surface',
        many=False,
        read_only=True,
        slug_field='rating'
    )

    class Meta:
        model = Street
        geo_field = "geom"
        fields = ('id',
                  'street_surface',
                  'street_type',
                  'street_surface_rating'
                  )
