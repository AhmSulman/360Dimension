from django.urls import path
from . import views

app_name = 'about'

urlpatterns = [
    path('', views.index, name='index'),
    path('member/<int:pk>/', views.team_member_detail, name='team_member_detail'),
    path('skills/', views.skills, name='skills'),
    path('experience/', views.experience, name='experience'),
]
