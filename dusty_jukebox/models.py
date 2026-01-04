from django.db import models
from django.contrib.auth.models import User
import json
import hashlib
from pathlib import Path


class AudioMetadata(models.Model):
    """Metadata for audio files including BPM and key analysis"""
    file_path = models.CharField(max_length=500, unique=True)
    file_hash = models.CharField(max_length=64, unique=True)
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    last_modified = models.DateTimeField()

    # Analysis results
    bpm = models.FloatField(null=True, blank=True)
    key = models.CharField(max_length=20, null=True, blank=True)
    is_minor = models.BooleanField(default=False)

    # Additional metadata
    duration = models.FloatField(null=True, blank=True)  # in seconds
    sample_rate = models.IntegerField(null=True, blank=True)
    channels = models.IntegerField(null=True, blank=True)

    # Cache management
    waveform_data = models.TextField(blank=True, help_text='JSON array of waveform samples')
    analysis_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-analysis_date']
        indexes = [
            models.Index(fields=['file_path']),
            models.Index(fields=['file_hash']),
        ]

    def __str__(self):
        return f"{self.file_name} - BPM: {self.bpm or 'Unknown'}, Key: {self.key or 'Unknown'}"

    def get_waveform_samples(self):
        """Get waveform data as list of integers"""
        if self.waveform_data:
            try:
                return json.loads(self.waveform_data)
            except json.JSONDecodeError:
                return []
        return []

    def set_waveform_samples(self, samples):
        """Set waveform data from list of integers"""
        self.waveform_data = json.dumps(samples)

    def is_analysis_complete(self):
        """Check if analysis is complete"""
        return self.bpm is not None and self.key is not None

    @staticmethod
    def get_file_hash(file_path):
        """Generate SHA256 hash for file"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return None


class AudioFile(models.Model):
    """Uploaded audio files"""
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('analyzing', 'Analyzing'),
        ('analyzed', 'Analyzed'),
        ('error', 'Error'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField()
    mime_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')

    # Upload metadata
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)

    # Link to metadata
    metadata = models.OneToOneField(AudioMetadata, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['user', '-uploaded_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.file_name} ({self.get_file_size_display()})"

    def get_file_size_display(self):
        """Return human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def get_absolute_path(self):
        """Get the absolute file path"""
        return Path(self.file_path)

    def file_exists(self):
        """Check if the file still exists on disk"""
        return self.get_absolute_path().exists()


class GuitarTuning(models.Model):
    """Guitar tunings configuration"""
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    string_notes = models.JSONField(help_text='JSON array of open string notes')

    # Metadata
    is_standard = models.BooleanField(default=False)
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], default='intermediate')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.display_name

    def get_string_notes(self):
        """Get string notes as list"""
        return self.string_notes if isinstance(self.string_notes, list) else []

    @classmethod
    def create_default_tunings(cls):
        """Create default guitar tunings"""
        tunings_data = [
            {
                'name': 'standard',
                'display_name': 'Standard (EADGBE)',
                'string_notes': ['E', 'A', 'D', 'G', 'B', 'E'],
                'is_standard': True,
                'difficulty_level': 'beginner'
            },
            {
                'name': 'drop_d',
                'display_name': 'Drop D (DADGBE)',
                'string_notes': ['D', 'A', 'D', 'G', 'B', 'E'],
                'is_standard': False,
                'difficulty_level': 'intermediate'
            },
            {
                'name': 'open_g',
                'display_name': 'Open G (DGDGBD)',
                'string_notes': ['D', 'G', 'D', 'G', 'B', 'D'],
                'is_standard': False,
                'difficulty_level': 'intermediate'
            },
            {
                'name': 'd_standard',
                'display_name': 'D Standard (DGCFAD)',
                'string_notes': ['D', 'G', 'C', 'F', 'A', 'D'],
                'is_standard': False,
                'difficulty_level': 'advanced'
            },
            {
                'name': 'c_standard',
                'display_name': 'C Standard (CFBbEbGC)',
                'string_notes': ['C', 'F', 'Bb', 'Eb', 'G', 'C'],
                'is_standard': False,
                'difficulty_level': 'advanced'
            }
        ]

        for tuning_data in tunings_data:
            cls.objects.get_or_create(
                name=tuning_data['name'],
                defaults=tuning_data
            )


class MusicalScale(models.Model):
    """Musical scales and modes"""
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    notes = models.JSONField(help_text='JSON array of scale notes')
    intervals = models.JSONField(help_text='JSON array of interval steps')

    # Scale properties
    is_diatonic = models.BooleanField(default=True)
    tonality = models.CharField(max_length=20, choices=[
        ('major', 'Major'),
        ('minor', 'Minor'),
        ('modal', 'Modal'),
        ('other', 'Other'),
    ], default='major')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.display_name

    def get_notes(self):
        """Get scale notes as list"""
        return self.notes if isinstance(self.notes, list) else []

    @classmethod
    def create_default_scales(cls):
        """Create default musical scales"""
        scales_data = [
            {
                'name': 'c_major',
                'display_name': 'C Major',
                'notes': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
                'intervals': [2, 2, 1, 2, 2, 2, 1],
                'is_diatonic': True,
                'tonality': 'major'
            },
            {
                'name': 'a_minor',
                'display_name': 'A Minor',
                'notes': ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
                'intervals': [2, 1, 2, 2, 1, 2, 2],
                'is_diatonic': True,
                'tonality': 'minor'
            },
            {
                'name': 'g_major',
                'display_name': 'G Major',
                'notes': ['G', 'A', 'B', 'C', 'D', 'E', 'F#'],
                'intervals': [2, 2, 1, 2, 2, 1, 2],
                'is_diatonic': True,
                'tonality': 'major'
            },
            {
                'name': 'e_minor',
                'display_name': 'E Minor',
                'notes': ['E', 'F#', 'G', 'A', 'B', 'C', 'D'],
                'intervals': [1, 2, 2, 1, 2, 2, 1],
                'is_diatonic': True,
                'tonality': 'minor'
            }
        ]

        for scale_data in scales_data:
            cls.objects.get_or_create(
                name=scale_data['name'],
                defaults=scale_data
            )


class UserSession(models.Model):
    """User session data for the music applications"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, unique=True)

    # Current state
    current_tuning = models.ForeignKey(GuitarTuning, on_delete=models.SET_NULL, null=True)
    current_scale = models.ForeignKey(MusicalScale, on_delete=models.SET_NULL, null=True)
    volume_level = models.FloatField(default=0.5)

    # Session data
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_activity']

    def __str__(self):
        user_name = self.user.username if self.user else 'Anonymous'
        return f"Session {self.session_key[:8]} - {user_name}"
