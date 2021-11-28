from django.urls import path
from .views import DijkRouteStreetsView, AStarRouteStreetsView, RouteStatisticView
urlpatterns = [
    path('dijkstra/streets/', DijkRouteStreetsView.as_view()),
    path('astar/streets/', AStarRouteStreetsView.as_view()),
    path('stat/streets/', RouteStatisticView.as_view()),
]