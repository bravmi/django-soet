from django.urls import path

from . import views

app_name = 'soet'
urlpatterns = [
    path('', views.index, name='index')
]
