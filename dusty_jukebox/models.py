from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable

from django.conf import settings
from django.db import models


class GuitarTuning(models.Model):
    DIFFICULTY_BEGINNER = "beginner"
    DIFFICULTY_INTERMEDIATE = "intermediate"
    DIFFICULTY_ADVANCED = "advanced"

    DIFFICULTY_CHOICES = [
        (DIFFICULTY_BEGINNER, "Beginner"),
        (DIFFICULTY_INTERMEDIATE, "Intermediate"),
        (DIFFICULTY_ADVANCED, "Advanced"),
    ]

    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    string_notes = models.JSONField(help_text="JSON array of open string notes")
    is_standard = models.BooleanField(default=False)
    difficulty_level = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default=DIFFICULTY_INTERMEDIATE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.display_name

    @classmethod
    def create_default_tunings(cls) -> None:
        """Seed some useful tunings; used by populate_defaults."""
        defaults = [
            {
                "name": "standard",
                "display_name": "Standard (E A D G B E)",
                "string_notes": ["E2", "A2", "D3", "G3", "B3", "E4"],
                "is_standard": True,
                "difficulty_level": cls.DIFFICULTY_BEGINNER,
            },
            {
                "name": "drop_d",
                "display_name": "Drop D (D A D G B E)",
                "string_notes": ["D2", "A2", "D3", "G3", "B3", "E4"],
                "is_standard": False,
                "difficulty_level": cls.DIFFICULTY_BEGINNER,
            },
            {
                "name": "drop_c",
                "display_name": "Drop C (C G C F A D)",
                "string_notes": ["C2", "G2", "C3", "F3", "A3", "D4"],
                "is_standard": False,
                "difficulty_level": cls.DIFFICULTY_INTERMEDIATE,
            },
            {
                "name": "open_g",
                "display_name": "Open G (D G D G B D)",
                "string_notes": ["D2", "G2", "D3", "G3", "B3", "D4"],
                "is_standard": False,
                "difficulty_level": cls.DIFFICULTY_INTERMEDIATE,
            },
            {
                "name": "open_d",
                "display_name": "Open D (D A D F# A D)",
                "string_notes": ["D2", "A2", "D3", "F#3", "A3", "D4"],
                "is_standard": False,
                "difficulty_level": cls.DIFFICULTY_INTERMEDIATE,
            },
            {
                "name": "open_c",
                "display_name": "Open C (C G C E G C)",
                "string_notes": ["C2", "G2", "C3", "E3", "G3", "C4"],
                "is_standard": False,
                "difficulty_level": cls.DIFFICULTY_ADVANCED,
            },
        ]

        for item in defaults:
            cls.objects.update_or_create(
                name=item["name"],
                defaults={
                    "display_name": item["display_name"],
                    "string_notes": item["string_notes"],
                    "is_standard": item["is_standard"],
                    "difficulty_level": item["difficulty_level"],
                },
            )


class MusicalScale(models.Model):
    TONALITY_MAJOR = "major"
    TONALITY_MINOR = "minor"
    TONALITY_MODAL = "modal"
    TONALITY_OTHER = "other"

    TONALITY_CHOICES = [
        (TONALITY_MAJOR, "Major"),
        (TONALITY_MINOR, "Minor"),
        (TONALITY_MODAL, "Modal"),
        (TONALITY_OTHER, "Other"),
    ]

    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    notes = models.JSONField(help_text="JSON array of scale notes")
    intervals = models.JSONField(help_text="JSON array of interval steps")
    is_diatonic = models.BooleanField(default=True)
    tonality = models.CharField(
        max_length=20, choices=TONALITY_CHOICES, default=TONALITY_MAJOR
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.display_name

    @classmethod
    def create_default_scales(cls) -> None:
        """Seed a few core scales; used by populate_defaults."""
        defaults = [
            {
                "name": "major",
                "display_name": "Major (Ionian)",
                "notes": ["1", "2", "3", "4", "5", "6", "7"],
                "intervals": [2, 2, 1, 2, 2, 2, 1],
                "is_diatonic": True,
                "tonality": cls.TONALITY_MAJOR,
            },
            {
                "name": "natural_minor",
                "display_name": "Natural Minor (Aeolian)",
                "notes": ["1", "2", "b3", "4", "5", "b6", "b7"],
                "intervals": [2, 1, 2, 2, 1, 2, 2],
                "is_diatonic": True,
                "tonality": cls.TONALITY_MINOR,
            },
            {
                "name": "dorian",
                "display_name": "Dorian",
                "notes": ["1", "2", "b3", "4", "5", "6", "b7"],
                "intervals": [2, 1, 2, 2, 2, 1, 2],
                "is_diatonic": True,
                "tonality": cls.TONALITY_MODAL,
            },
            {
                "name": "phrygian",
                "display_name": "Phrygian",
                "notes": ["1", "b2", "b3", "4", "5", "b6", "b7"],
                "intervals": [1, 2, 2, 2, 1, 2, 2],
                "is_diatonic": True,
                "tonality": cls.TONALITY_MODAL,
            },
            {
                "name": "lydian",
                "display_name": "Lydian",
                "notes": ["1", "2", "3", "#4", "5", "6", "7"],
                "intervals": [2, 2, 2, 1, 2, 2, 1],
                "is_diatonic": True,
                "tonality": cls.TONALITY_MODAL,
            },
            {
                "name": "mixolydian",
                "display_name": "Mixolydian",
                "notes": ["1", "2", "3", "4", "5", "6", "b7"],
                "intervals": [2, 2, 1, 2, 2, 1, 2],
                "is_diatonic": True,
                "tonality": cls.TONALITY_MODAL,
            },
            {
                "name": "locrian",
                "display_name": "Locrian",
                "notes": ["1", "b2", "b3", "4", "b5", "b6", "b7"],
                "intervals": [1, 2, 2, 1, 2, 2, 2],
                "is_diatonic": True,
                "tonality": cls.TONALITY_MODAL,
            },
        ]

        for item in defaults:
            cls.objects.update_or_create(
                name=item["name"],
                defaults={
                    "display_name": item["display_name"],
                    "notes": item["notes"],
                    "intervals": item["intervals"],
                    "is_diatonic": item["is_diatonic"],
                    "tonality": item["tonality"],
                },
            )


class AudioMetadata(models.Model):
    file_path = models.CharField(max_length=500, unique=True)
    file_hash = models.CharField(max_length=64, unique=True)
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    last_modified = models.DateTimeField()

    bpm = models.FloatField(null=True, blank=True)
    key = models.CharField(max_length=20, null=True, blank=True)
    is_minor = models.BooleanField(default=False)

    duration = models.FloatField(null=True, blank=True)
    sample_rate = models.IntegerField(null=True, blank=True)
    channels = models.IntegerField(null=True, blank=True)

    waveform_data = models.TextField(
        blank=True, help_text="JSON array of waveform samples"
    )
    analysis_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-analysis_date"]
        indexes = [
            models.Index(fields=["file_path"], name="dusty_jukeb_file_pa_1f819e_idx"),
            models.Index(fields=["file_hash"], name="dusty_jukeb_file_ha_a78c32_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.file_name} ({self.bpm or '--'} BPM)"

    @staticmethod
    def compute_hash(*parts: str) -> str:
        h = hashlib.sha256()
        for p in parts:
            h.update(p.encode("utf-8", errors="ignore"))
            h.update(b"\0")
        return h.hexdigest()

    def set_waveform_samples(self, samples: Iterable[int] | list[int]) -> None:
        self.waveform_data = json.dumps(list(samples))

    def get_waveform_samples(self) -> list[int]:
        if not self.waveform_data:
            return []
        try:
            data: Any = json.loads(self.waveform_data)
            if isinstance(data, list):
                return [int(x) for x in data]
        except Exception:
            return []
        return []


class UserSession(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    volume_level = models.FloatField(default=0.5)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    current_scale = models.ForeignKey(
        MusicalScale, on_delete=models.SET_NULL, null=True
    )
    current_tuning = models.ForeignKey(
        GuitarTuning, on_delete=models.SET_NULL, null=True
    )

    class Meta:
        ordering = ["-last_activity"]

    def __str__(self) -> str:
        return self.session_key


class AudioFile(models.Model):
    STATUS_UPLOADED = "uploaded"
    STATUS_ANALYZING = "analyzing"
    STATUS_ANALYZED = "analyzed"
    STATUS_ERROR = "error"

    STATUS_CHOICES = [
        (STATUS_UPLOADED, "Uploaded"),
        (STATUS_ANALYZING, "Analyzing"),
        (STATUS_ANALYZED, "Analyzed"),
        (STATUS_ERROR, "Error"),
    ]

    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField()
    mime_type = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_UPLOADED
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    metadata = models.OneToOneField(
        AudioMetadata,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(
                fields=["user", "-uploaded_at"],
                name="dusty_jukeb_user_id_979e14_idx",
            ),
            models.Index(fields=["status"], name="dusty_jukeb_status_af2c37_idx"),
        ]

    def __str__(self) -> str:
        return self.file_name