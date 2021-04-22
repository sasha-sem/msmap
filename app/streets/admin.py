from django.contrib import admin
from .models import *
from django.contrib.gis import admin as gisadmin


@admin.register(StreetType)
class StreetTypeAdmin(admin.ModelAdmin):
    list_display = ( "id" ,"name", "cars_allowed")

@admin.register(SurfaceType)
class SurfaceTypeAdmin(admin.ModelAdmin):
    list_display = ( "id" ,"name", "rating")

@admin.register(Street)
class StreetAdmin(gisadmin.OSMGeoAdmin):
    list_display = ( "id" ,"street_type", "street_surface")

