from django.contrib import admin
from .models import (
    AudioMetadata, AudioFile, GuitarTuning,
    MusicalScale, UserSession
)

@admin.register(AudioMetadata)
class AudioMetadataAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'bpm', 'key', 'is_minor', 'analysis_date']
    list_filter = ['is_minor', 'analysis_date']
    search_fields = ['file_name', 'key']
    readonly_fields = ['file_hash', 'last_modified']

@admin.register(AudioFile)
class AudioFileAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'user', 'file_size', 'status', 'uploaded_at']
    list_filter = ['status', 'uploaded_at', 'user']
    search_fields = ['file_name', 'user__username']
    readonly_fields = ['file_size', 'uploaded_at']

@admin.register(GuitarTuning)
class GuitarTuningAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'is_standard', 'difficulty_level']
    list_filter = ['is_standard', 'difficulty_level']
    search_fields = ['name', 'display_name']

@admin.register(MusicalScale)
class MusicalScaleAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'tonality', 'is_diatonic']
    list_filter = ['tonality', 'is_diatonic']
    search_fields = ['name', 'display_name']

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'current_tuning', 'last_activity']
    list_filter = ['last_activity']
    search_fields = ['user__username', 'session_key']
    readonly_fields = ['session_key', 'last_activity']
