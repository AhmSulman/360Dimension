from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods

from .audio_analyser import AudioAnalyser
from .models import AudioFile, AudioMetadata, GuitarTuning, MusicalScale

CHROMATIC_SHARPS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
SHARP_TO_FLAT = {"C#": "Db", "D#": "Eb", "F#": "Gb", "G#": "Ab", "A#": "Bb"}


def _note_name_flat(name: str) -> str:
    return SHARP_TO_FLAT.get(name, name)


def _note_to_index(note: str) -> int:
    note = note.strip()
    if not note:
        raise ValueError("Empty note")

    letter = note[0].upper()
    rest = note[1:]

    accidental = ""
    if rest and rest[0] in ["#", "b"]:
        accidental = rest[0]
        rest = rest[1:]

    octave = int(rest)

    base = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}[letter]
    if accidental == "#":
        base += 1
    elif accidental == "b":
        base -= 1

    pitch = (base % 12 + 12) % 12
    midi = (octave + 1) * 12 + pitch
    return midi


def _index_to_note_flat(midi: int) -> str:
    pitch = midi % 12
    octave = midi // 12 - 1
    note = _note_name_flat(CHROMATIC_SHARPS[pitch])
    return f"{note}{octave}"


def _media_root() -> Path:
    mr = getattr(settings, "MEDIA_ROOT", None)
    if mr:
        return Path(mr)
    return Path.cwd() / "media"


@ensure_csrf_cookie
@require_GET
def dusty_jukebox_view(request: HttpRequest) -> HttpResponse:
    return render(request, "dusty_jukebox/dusty_jukebox.html")


@ensure_csrf_cookie
@require_GET
def guitar_bud_view(request: HttpRequest) -> HttpResponse:
    tunings = list(GuitarTuning.objects.all().order_by("display_name"))
    current = None

    requested = request.GET.get("tuning")
    if requested:
        current = GuitarTuning.objects.filter(name=requested).first()

    if current is None:
        current = GuitarTuning.objects.filter(is_standard=True).first()

    if current is None and tunings:
        current = tunings[0]

    return render(
        request,
        "dusty_jukebox/guitar_bud.html",
        {"available_tunings": tunings, "current_tuning": current},
    )


@ensure_csrf_cookie
@require_GET
def piano_view(request: HttpRequest) -> HttpResponse:
    return render(request, "dusty_jukebox/piano.html")


@require_GET
def get_tunings(request: HttpRequest) -> JsonResponse:
    tunings = GuitarTuning.objects.all().order_by("display_name")
    return JsonResponse(
        {
            "success": True,
            "tunings": [
                {
                    "name": t.name,
                    "display_name": t.display_name,
                    "string_notes": t.string_notes,
                    "is_standard": t.is_standard,
                    "difficulty_level": t.difficulty_level,
                }
                for t in tunings
            ],
        }
    )


@require_GET
def get_scales(request: HttpRequest) -> JsonResponse:
    scales = MusicalScale.objects.all().order_by("display_name")
    return JsonResponse(
        {
            "success": True,
            "scales": [
                {
                    "name": s.name,
                    "display_name": s.display_name,
                    "notes": s.notes,
                    "intervals": s.intervals,
                    "tonality": s.tonality,
                }
                for s in scales
            ],
        }
    )


@require_GET
def get_fretboard_data(request: HttpRequest) -> JsonResponse:
    tuning_name = request.GET.get("tuning")

    tuning = None
    if tuning_name:
        tuning = GuitarTuning.objects.filter(name=tuning_name).first()
        if tuning is None:
            tuning = GuitarTuning.objects.filter(display_name=tuning_name).first()

    if tuning is None:
        tuning = GuitarTuning.objects.filter(is_standard=True).first()

    if tuning is None:
        tuning = GuitarTuning.objects.first()

    if tuning is None:
        return JsonResponse(
            {
                "success": False,
                "error": "No tunings found. Run: python manage.py populate_defaults",
            },
            status=400,
        )

    frets = int(request.GET.get("frets", 16))
    strings = []

    # Reverse the strings so that the highest string is at the top of the fretboard UI.
    for open_note in reversed(tuning.string_notes):
        base_midi = _note_to_index(open_note)
        frets_out = []
        for fret in range(frets + 1):
            frets_out.append(
                {"fret": fret, "note": _index_to_note_flat(base_midi + fret)}
            )
        strings.append({"open_note": open_note, "frets": frets_out})

    return JsonResponse(
        {
            "success": True,
            "tuning": tuning.display_name,
            "tuning_name": tuning.name,
            "frets": frets,
            "strings": strings,
        }
    )


@require_http_methods(["POST"])
def play_melody(request: HttpRequest) -> JsonResponse:
    # With synth tones, browser plays sound; this endpoint is just an echo/validator.
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
        melody_raw = (payload.get("melody") or "").strip()
        if not melody_raw:
            return JsonResponse(
                {"success": False, "error": "No melody provided"}, status=400
            )
        notes = [n for n in melody_raw.replace(",", " ").split() if n]
        return JsonResponse({"success": True, "melody": notes})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


@require_http_methods(["POST"])
def auto_compose(request: HttpRequest) -> JsonResponse:
    # Keep a simple default; you can expand later.
    return JsonResponse(
        {
            "success": True,
            "scale": "A Minor",
            "melody": ["A3", "B3", "C4", "D4"],
            "chords": ["Am", "Dm", "Em", "F"],
        }
    )


@require_http_methods(["POST"])
def analyze_audio(request: HttpRequest) -> JsonResponse:
    up = request.FILES.get("file")
    if not up:
        return JsonResponse(
            {"success": False, "error": "Missing file field"}, status=400
        )

    upload_dir = _media_root() / "dusty_jukebox_uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_name = Path(up.name).name
    dest = (
        upload_dir
        / f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{safe_name}"
    )

    with dest.open("wb") as f:
        for chunk in up.chunks():
            f.write(chunk)

    stat = dest.stat()
    last_modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
    file_hash = AudioMetadata.compute_hash(
        str(dest), str(stat.st_size), str(stat.st_mtime)
    )

    metadata, _ = AudioMetadata.objects.update_or_create(
        file_path=str(dest),
        defaults={
            "file_hash": file_hash,
            "file_name": safe_name,
            "file_size": stat.st_size,
            "last_modified": last_modified,
        },
    )

    try:
        result = AudioAnalyser.analyze_file(
            str(dest), save_metadata=True, metadata_model=metadata
        )
        return JsonResponse(
            {
                "success": True,
                "bpm": result.get("bpm"),
                "key": result.get("key"),
                "is_minor": result.get("is_minor", False),
                "waveform": result.get("waveform_data", []),
                # optional if you want it later in UI:
                # "waveform_image": result.get("waveform_image"),
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_GET
def get_audio_files(request: HttpRequest) -> JsonResponse:
    files = AudioFile.objects.order_by("-uploaded_at")[:200]
    return JsonResponse(
        {
            "success": True,
            "files": [
                {
                    "id": f.id,
                    "file_name": f.file_name,
                    "status": f.status,
                    "uploaded_at": f.uploaded_at.isoformat(),
                    "metadata_id": f.metadata_id,
                }
                for f in files
            ],
        }
    )


@require_http_methods(["POST"])
def upload_audio(request: HttpRequest) -> JsonResponse:
    up = request.FILES.get("file")
    if not up:
        return JsonResponse(
            {"success": False, "error": "Missing file field"}, status=400
        )

    upload_dir = _media_root() / "dusty_jukebox_uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_name = Path(up.name).name
    dest = (
        upload_dir
        / f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{safe_name}"
    )

    with dest.open("wb") as f:
        for chunk in up.chunks():
            f.write(chunk)

    stat = dest.stat()

    audio_file = AudioFile.objects.create(
        file_name=safe_name,
        file_path=str(dest),
        file_size=stat.st_size,
        mime_type=getattr(up, "content_type", "") or "application/octet-stream",
        status=AudioFile.STATUS_UPLOADED,
        user=(
            request.user
            if getattr(request, "user", None) and request.user.is_authenticated
            else None
        ),
    )
    return JsonResponse({"success": True, "id": audio_file.id})


@require_http_methods(["POST"])
def load_track(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"success": True})


@require_http_methods(["POST"])
def play_audio(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"success": True})


@require_http_methods(["POST"])
def set_volume(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"success": True})


@require_GET
def audio_analyzer_view(request: HttpRequest) -> HttpResponse:
    return render(request, "dusty_jukebox/dusty_jukebox.html")
