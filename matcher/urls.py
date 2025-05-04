from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('analyse/genai', views.genai, name='genai'),
    path('about/', views.about, name='about'),
]
