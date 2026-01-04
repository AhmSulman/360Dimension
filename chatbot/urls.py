from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot, name='chatbot'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    path('config/', views.chatbot_config, name='chatbot_config'),
]
