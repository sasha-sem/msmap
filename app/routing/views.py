from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from streets.serializers import StreetsSerializer
from streets.models import Street
from django.db import connection
from rest_framework_gis.fields import GeoJsonDict
from collections import OrderedDict
from datetime import datetime, timedelta


# Create your views here.
class AStarRouteStreetsView(generics.ListAPIView):
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
                        pgr_astar(
                          'SELECT streets_street.id as id, source, target,  (st_length(geom::geography)/1000)/(5+(15*(rating/10))) as cost, x1, y1, x2, y2 FROM streets_street
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

class DijkRouteStreetsView(generics.ListAPIView):
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
                          'SELECT streets_street.id as id, source, target, (st_length(geom::geography)/1000)/(5+(15*(rating/10))) AS cost FROM streets_street
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


class RouteStatisticView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        try:
            from_lon = float(request.query_params.get('from_lon'))
            from_lat = float(self.request.query_params.get('from_lat'))
            to_lon = float(self.request.query_params.get('to_lon'))
            to_lat = float(self.request.query_params.get('to_lat'))
        except ValueError:
            return Response(data={"message": "one or more longitudes or latitudes are not correct floats"}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            start_time = datetime.now()
            cursor.execute('''
            SELECT st_length(geom::geography) as length, cost*60 as time, surface.rating as rating
                  FROM
                    streets_street
                    JOIN (
                      SELECT
                        *
                      FROM
                        pgr_dijkstra(
                        'SELECT streets_street.id as id, source, target,  (st_length(geom::geography)/1000)/(5+(15*(rating/10))) AS cost FROM streets_street
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
                    ) AS route ON streets_street.id = route.edge JOIN (SELECT * FROM streets_surfacetype) AS surface ON surface.id = street_surface_id''', [from_lon, from_lat, to_lon, to_lat])
            dijk = dictfetchall(cursor)
            end_time = datetime.now()
            dijk_delta = end_time - start_time
            route_length =  sum([it['length'] for it in dijk])
            route_time =  sum([it['time'] for it in dijk])
            average_speed = (route_length/1000)/(route_time/60)
            dijk_obj = {
                "time": dijk_delta,
                "path": dijk,
                "route_length": round(route_length/1000, 2),
                "route_time": int(round(route_time, 0)),
                "average_speed": round(average_speed, 2),
            }

        with connection.cursor() as cursor:
            start_time = datetime.now()
            cursor.execute('''
            SELECT st_length(geom::geography) as length, cost*60 as time, surface.rating as rating
                  FROM
                    streets_street
                    JOIN (
                      SELECT
                        *
                      FROM
                        pgr_astar(
                          'SELECT streets_street.id as id, source, target,  (st_length(geom::geography)/1000)/(5+(15*(rating/10))) as cost, x1, y1, x2, y2 FROM streets_street
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
                    ) AS route ON streets_street.id = route.edge JOIN (SELECT * FROM streets_surfacetype) AS surface ON surface.id = street_surface_id''', [from_lon, from_lat, to_lon, to_lat])
            astar = dictfetchall(cursor)
            end_time = datetime.now()
            astar_delta = end_time - start_time
            route_length =  sum([it['length'] for it in astar])
            route_time =  sum([it['time'] for it in astar])
            average_speed = (route_length/1000)/(route_time/60)
            astar_obj = {
                "time": astar_delta,
                "path": astar,
                "route_length": round(route_length/1000, 2),
                "route_time": int(round(route_time, 0)),
                "average_speed": round(average_speed, 2),
            }

        return Response({"dijkstra": dijk_obj, "astar": astar_obj}, status=status.HTTP_200_OK)

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]