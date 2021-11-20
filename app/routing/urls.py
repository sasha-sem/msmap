from django.urls import path
from .views import RouteStreetsView
urlpatterns = [
    path('streets/', RouteStreetsView.as_view()),
]