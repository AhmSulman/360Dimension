from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json
import os
import random
from pathlib import Path
import subprocess
import hashlib
# import pdb

# pdb.set_trace()  # Commented out debugging code
# Try to import pygame, but make it optional


try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    pygame = None
    PYGAME_AVAILABLE = False

from .models import (
    AudioMetadata, AudioFile, GuitarTuning, MusicalScale, UserSession
)


# Initialize pygame mixer if available
if PYGAME_AVAILABLE and pygame:
    pygame.mixer.init()

# GuitarBud Views
def guitar_bud_view(request):
    """Main GuitarBud fretboard view"""
    # Get or create user session
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    user_session, created = UserSession.objects.get_or_create(
        session_key=session_key,
        defaults={'user': request.user if request.user.is_authenticated else None}
    )

    # Ensure default tunings exist
    if GuitarTuning.objects.count() == 0:
        GuitarTuning.create_default_tunings()

    # Ensure default scales exist
    if MusicalScale.objects.count() == 0:
        MusicalScale.create_default_scales()

    context = {
        'current_tuning': user_session.current_tuning or GuitarTuning.objects.filter(name='standard').first(),
        'available_tunings': GuitarTuning.objects.all(),
        'available_scales': MusicalScale.objects.all(),
    }

    return render(request, 'dusty_jukebox/guitar_bud.html', context)


@require_GET
def get_fretboard_data(request):
    """API endpoint to get fretboard data for a tuning"""
    tuning_name = request.GET.get('tuning', 'standard')

    try:
        tuning = GuitarTuning.objects.get(name=tuning_name)
        string_notes = tuning.get_string_notes()

        # Build fretboard data
        fretboard_data = {
            'tuning': tuning.display_name,
            'tuning_name': tuning.name,
            'strings': [],
            'notes': {}
        }

        chromatic = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        frets = 22

        for string_index, open_note in enumerate(string_notes):
            string_data = {
                'open_note': open_note,
                'frets': []
            }

            for fret in range(frets + 1):
                if open_note not in chromatic:
                    note_name = "?"
                else:
                    start_index = chromatic.index(open_note)
                    chromatic_index = (start_index + fret) % 12
                    octave = 4 + ((start_index + fret) // 12)
                    note_name = f"{chromatic[chromatic_index]}{octave}"

                string_data['frets'].append({
                    'fret': fret,
                    'note': note_name,
                    'has_audio': True  # Simplified - in real implementation check if audio file exists
                })

                # Store note positions for reverse lookup
                if note_name not in fretboard_data['notes']:
                    fretboard_data['notes'][note_name] = []
                fretboard_data['notes'][note_name].append({
                    'string': string_index,
                    'fret': fret
                })

            fretboard_data['strings'].append(string_data)

        return JsonResponse(fretboard_data)

    except GuitarTuning.DoesNotExist:
        return JsonResponse({'error': 'Tuning not found'}, status=404)


@require_POST
@csrf_exempt
def play_melody(request):
    """API endpoint to play a melody"""
    try:
        data = json.loads(request.body)
        melody_text = data.get('melody', '')

        if not melody_text:
            return JsonResponse({'success': False, 'error': 'No melody provided'})

        # Parse melody (simplified implementation)
        notes = [note.strip() for note in melody_text.replace(',', ' ').split() if note.strip()]

        # In a real implementation, this would play actual audio files
        # For now, just return success with the parsed notes
        result = {
            'success': True,
            'melody': notes,
            'message': f'Would play {len(notes)} notes'
        }

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
@csrf_exempt
def auto_compose(request):
    """API endpoint for auto-composition"""
    try:
        data = json.loads(request.body)
        scale_name = data.get('scale', 'a_minor')

        # Get scale from database
        try:
            scale = MusicalScale.objects.get(name=scale_name.replace(' ', '_').lower())
            scale_notes = scale.get_notes()
        except MusicalScale.DoesNotExist:
            # Fallback to A minor
            scale_notes = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

        # Generate melody
        melody_length = 8
        melody = []

        for _ in range(melody_length):
            note = random.choice(scale_notes)
            octave = random.choice([3, 4, 5])
            melody.append(f"{note}{octave}")

        # Generate chord progression (simplified)
        chord_progression = ["Am", "Dm", "Em", "F", "G", "C", "Bdim"]

        result = {
            'success': True,
            'scale': scale_name,
            'melody': melody,
            'chords': chord_progression[:4],
            'tempo': 120,
            'note_duration': 0.5
        }

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# DustyJukebox (Audio Player) Views
def dusty_jukebox_view(request):
    """Main DustyJukebox audio player view"""
    try:
        # Get or create user session
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        user_session, created = UserSession.objects.get_or_create(
            session_key=session_key,
            defaults={'user': request.user if request.user.is_authenticated else None}
        )

        # Get user's uploaded files
        user_files = AudioFile.objects.filter(user=request.user) if request.user.is_authenticated else []

        context = {
            'user_files': user_files,
            'has_files': user_files.exists(),
        }

        return render(request, 'dusty_jukebox/dusty_jukebox.html', context)
    except Exception as e:
        # Fallback in case of any errors
        context = {
            'user_files': [],
            'has_files': False,
            'error': str(e),
        }
        return render(request, 'dusty_jukebox/dusty_jukebox.html', context)


@require_GET
def get_audio_files(request):
    """API endpoint to get list of audio files"""
    if request.user.is_authenticated:
        files = AudioFile.objects.filter(user=request.user)
    else:
        # For anonymous users, return empty list or demo files
        files = AudioFile.objects.none()

    files_data = []
    for file_obj in files:
        files_data.append({
            'id': file_obj.id,
            'name': file_obj.file_name,
            'path': file_obj.file_path,
            'size': file_obj.file_size,
            'uploaded_at': file_obj.uploaded_at.isoformat(),
            'metadata': {
                'bpm': file_obj.metadata.bpm if file_obj.metadata else None,
                'key': file_obj.metadata.key if file_obj.metadata else None,
                'is_minor': file_obj.metadata.is_minor if file_obj.metadata else False,
            } if file_obj.metadata else None
        })

    return JsonResponse({'files': files_data})


@require_POST
@csrf_exempt
def upload_audio(request):
    """API endpoint to upload audio files"""
    if 'files' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No files provided'})

    uploaded_files = []
    files = request.FILES.getlist('files')

    for file in files:
        if not file.name:
            continue

        # Validate file type
        allowed_extensions = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'}
        file_extension = Path(file.name).suffix.lower()

        if file_extension not in allowed_extensions:
            continue

        # Save file
        file_path = f"audio/{request.user.id if request.user.is_authenticated else 'anonymous'}/{file.name}"
        saved_path = default_storage.save(file_path, ContentFile(file.read()))

        # Create database record
        audio_file = AudioFile.objects.create(
            user=request.user if request.user.is_authenticated else None,
            file_name=file.name,
            file_path=saved_path,
            file_size=file.size,
            mime_type=file.content_type or 'audio/mpeg'
        )

        uploaded_files.append({
            'id': audio_file.id,
            'name': audio_file.file_name,
            'size': audio_file.get_file_size_display(),
            'path': audio_file.file_path
        })

    return JsonResponse({
        'success': len(uploaded_files) > 0,
        'files': uploaded_files
    })


@require_POST
@csrf_exempt
def analyze_audio(request):
    """API endpoint to analyze audio file for BPM and key"""
    try:
        data = json.loads(request.body)
        file_path = data.get('path', '')

        if not file_path:
            return JsonResponse({'success': False, 'error': 'No file path provided'})

        # Get or create metadata record
        file_hash = AudioMetadata.get_file_hash(file_path)
        if not file_hash:
            return JsonResponse({'success': False, 'error': 'Could not read file'})

        metadata, created = AudioMetadata.objects.get_or_create(
            file_hash=file_hash,
            defaults={
                'file_path': file_path,
                'file_name': Path(file_path).name,
                'file_size': Path(file_path).stat().st_size,
                'last_modified': timezone.now(),
            }
        )

        # If already analyzed and file hasn't changed, return cached results
        if not created and metadata.is_analysis_complete():
            return JsonResponse({
                'success': True,
                'bpm': metadata.bpm,
                'key': metadata.key,
                'is_minor': metadata.is_minor,
                'waveform': metadata.get_waveform_samples(),
                'cached': True
            })

        # Perform analysis using external script
        try:
            analyzer_script = Path(settings.BASE_DIR) / "dusty_jukebox" / "audio_analyser.py"
            if not analyzer_script.exists():
                return JsonResponse({'success': False, 'error': 'Audio analyzer not found'})

            result = subprocess.run([
                'python', str(analyzer_script), file_path
            ], capture_output=True, text=True, timeout=30, cwd=settings.BASE_DIR)

            if result.returncode == 0:
                # Parse output
                bpm = 0
                key = "Unknown"

                for line in result.stdout.split('\n'):
                    if line.startswith("BPM:"):
                        try:
                            bpm = float(line.replace("BPM:", "").strip())
                        except:
                            pass
                    elif line.startswith("KEY:"):
                        key = line.replace("KEY:", "").strip()

                # Update metadata
                metadata.bpm = bpm
                metadata.key = key
                metadata.is_minor = 'minor' in key.lower()
                metadata.analysis_date = timezone.now()

                # Generate simple waveform (placeholder)
                metadata.set_waveform_samples([random.randint(0, 255) for _ in range(200)])

                metadata.save()

                return JsonResponse({
                    'success': True,
                    'bpm': bpm,
                    'key': key,
                    'is_minor': metadata.is_minor,
                    'waveform': metadata.get_waveform_samples()
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result.stderr or 'Analysis failed'
                })

        except subprocess.TimeoutExpired:
            return JsonResponse({'success': False, 'error': 'Analysis timeout'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
@csrf_exempt
def load_track(request):
    """API endpoint to load an audio track"""
    try:
        data = json.loads(request.body)
        file_path = data.get('path', '')

        if not file_path:
            return JsonResponse({'success': False, 'error': 'No file path provided'})

        # In a real implementation, this would initialize pygame with the track
        # For now, just return success
        return JsonResponse({
            'success': True,
            'path': file_path,
            'message': 'Track loaded (pygame integration would go here)'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
@csrf_exempt
def play_audio(request):
    """API endpoint to play/pause audio"""
    try:
        data = json.loads(request.body)
        action = data.get('action', 'play')

        # In a real implementation, this would control pygame playback
        return JsonResponse({
            'success': True,
            'action': action,
            'message': f'Audio {action} (pygame integration would go here)'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
@csrf_exempt
def set_volume(request):
    """API endpoint to set volume"""
    try:
        data = json.loads(request.body)
        volume = float(data.get('volume', 0.5))

        volume = max(0.0, min(1.0, volume))

        # In a real implementation, this would set pygame volume
        return JsonResponse({
            'success': True,
            'volume': volume,
            'message': f'Volume set to {volume} (pygame integration would go here)'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Utility Views
@require_GET
def get_scales(request):
    """Get available musical scales"""
    scales = MusicalScale.objects.all()
    scales_data = [{'name': s.name, 'display_name': s.display_name} for s in scales]
    return JsonResponse({'scales': scales_data})


@require_GET
def get_tunings(request):
    """Get available guitar tunings"""
    tunings = GuitarTuning.objects.all()
    tunings_data = [{'name': t.name, 'display_name': t.display_name} for t in tunings]
    return JsonResponse({'tunings': tunings_data})


def audio_analyzer_view(request):
    """Simple audio analyzer interface"""
    return render(request, 'dusty_jukebox/audio_analyzer.html')
