from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.index, name='index'),
    path('project/<slug:slug>/', views.project_detail, name='project_detail'),
    path('category/<slug:slug>/', views.category_projects, name='category_projects'),
    path('technology/<slug:slug>/', views.technology_projects, name='technology_projects'),
]
