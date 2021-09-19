from django.shortcuts import render
from rest_framework import generics, status
from .models import Street
from .serializers import StreetsSerializer


class StreetsDetail(generics.RetrieveAPIView):
    queryset = Street.objects.all()
    serializer_class = StreetsSerializer


class StreetsList(generics.ListAPIView):
    queryset = Street.objects.all()
    serializer_class = StreetsSerializer
