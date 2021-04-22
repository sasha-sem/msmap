from django.urls import path
from .views import StreetsDetail, StreetsList

urlpatterns = [
    path('<int:pk>/', StreetsDetail.as_view()),
    path('', StreetsList.as_view()),
]