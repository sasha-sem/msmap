from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from streets.serializers import StreetsSerializer
from streets.models import Street
from django.db import connection
from rest_framework_gis.fields import GeoJsonDict
from collections import OrderedDict



# Create your views here.
class RouteStreetsView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        try:
            from_lon = float(request.query_params.get('from_lon'))
            from_lat = float(self.request.query_params.get('from_lat'))
            to_lon = float(self.request.query_params.get('to_lon'))
            to_lat = float(self.request.query_params.get('to_lat'))
        except ValueError:
            return Response(data={"message": "one or more longitudes or latitudes are not correct floats"}, status=status.HTTP_400_BAD_REQUEST)

        route = Street.objects.raw('''
            SELECT id, street_type_id, street_surface_id, user_score, source,  target, geom::bytea
                  FROM
                    streets_street
                    JOIN (
                      SELECT
                        *
                      FROM
                        pgr_dijkstra(
                          'SELECT streets_street.id as id, source, target, st_length(geom)*(10/rating) AS cost FROM streets_street
                        JOIN (SELECT * FROM streets_surfacetype) AS surface ON surface.id = streets_street.street_surface_id',
                      (SELECT id 
                FROM streets_street_vertices_pgr
                ORDER BY ST_Distance(
                    the_geom,
                    ST_SetSRID(ST_MakePoint(%s,
                          %s), 4326),
                    true
                ) 
                LIMIT 1),
                          (SELECT id 
                FROM streets_street_vertices_pgr
                ORDER BY ST_Distance(
                    the_geom,
                    ST_SetSRID(ST_MakePoint(%s,
                          %s), 4326),
                    true
                )
                LIMIT 1),false
                        )
                    ) AS route ON streets_street.id = route.edge''', [from_lon, from_lat, to_lon, to_lat])
        serializer = StreetsSerializer(route, many=True)

        startPath = getShortestPath([from_lon, from_lat], -1)
        endPath = getShortestPath([to_lon, to_lat], -2)
        serializer.data['features'].insert(0, startPath)
        serializer.data['features'].append(endPath)
        return Response(serializer.data, status=status.HTTP_200_OK)

def getShortestPath(coordinates, id):
    with connection.cursor() as cursor:
        cursor.execute('''
        SELECT ST_AsGeoJSON(st_multi(ST_MakeLine(ST_SetSRID(ST_MakePoint(%s,
                          %s), 4326), (SELECT the_geom 
                FROM streets_street_vertices_pgr
                ORDER BY ST_Distance(
                    the_geom,
                    ST_SetSRID(ST_MakePoint(%s,
                          %s), 4326),
                    true
                ) 
                LIMIT 1))))''', [coordinates[0], coordinates[1], coordinates[0], coordinates[1]])
        row = cursor.fetchone()

    feature = OrderedDict([('id', id), ('type', 'Feature'), ('geometry', GeoJsonDict(row[0])), ('properties', OrderedDict([('street_type', OrderedDict([('id', 0), ('name', 'unknown'), ('cars_allowed', False)])), ('surface_type', OrderedDict([('id', 0), ('name', 'Неизвестно'), ('rating', 0)])), ('street_surface_rating', 0)]))])
    return feature

