from django.urls import path
from . import views

app_name = 'dusty_jukebox'

urlpatterns = [
    # GuitarBud (Fretboard) URLs
    path('guitar/', views.guitar_bud_view, name='guitar_bud'),
    path('api/fretboard/', views.get_fretboard_data, name='fretboard_data'),
    path('fretboard/', views.fretboard_view, name='fretboard'),
    path('api/play_melody/', views.play_melody, name='play_melody'),
    path('api/auto_compose/', views.auto_compose, name='auto_compose'),

    # DustyJukebox (Audio Player) URLs
    path('', views.dusty_jukebox_view, name='dusty_jukebox'),
    path('api/files/', views.get_audio_files, name='audio_files'),
    path('api/upload/', views.upload_audio, name='upload_audio'),
    path('api/analyze/', views.analyze_audio, name='analyze_audio'),
    path('api/load_track/', views.load_track, name='load_track'),
    path('api/play/', views.play_audio, name='play_audio'),
    path('api/volume/', views.set_volume, name='set_volume'),

    # Utility URLs
    path('api/scales/', views.get_scales, name='get_scales'),
    path('api/tunings/', views.get_tunings, name='get_tunings'),

    path('analyzer/', views.audio_analyzer_view, name='audio_analyzer'),


]
