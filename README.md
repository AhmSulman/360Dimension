# 360Dimension - Full-Stack Django Platform

## Overview

360Dimension is a comprehensive Django-based platform featuring multiple interconnected applications including an AI-powered chatbot, blog CMS, portfolio showcase, team management system, and an audio/music analysis platform called Dusty Jukebox.

## 🤔 Why the `/api/` Prefix in Dusty Jukebox URLs?

The Dusty Jukebox app uses the `/api/` prefix to clearly separate **HTML page views** from **JSON API endpoints**:

### HTML Views (No `/api/` prefix):
- `/jukebox/` → `dusty_jukebox_view()` → Returns HTML template for audio player
- `/jukebox/guitar/` → `guitar_bud_view()` → Returns HTML template for fretboard
- `/jukebox/analyzer/` → `audio_analyzer_view()` → Returns HTML template for analyzer

### JSON API Endpoints (`/api/` prefix):
- `/jukebox/api/files/` → `get_audio_files()` → Returns JSON list of audio files
- `/jukebox/api/upload/` → `upload_audio()` → Returns JSON upload status
- `/jukebox/api/analyze/` → `analyze_audio()` → Returns JSON with BPM/key data
- `/jukebox/api/fretboard/` → `get_fretboard_data()` → Returns JSON fretboard layout
- `/jukebox/api/play_melody/` → `play_melody()` → Returns JSON melody status
- `/jukebox/api/auto_compose/` → `auto_compose()` → Returns JSON generated composition

### Why This Design?

1. **Clear Separation**: HTML views vs API endpoints are immediately distinguishable
2. **Frontend Integration**: JavaScript can easily target `/api/*` endpoints for AJAX calls
3. **API Documentation**: All API endpoints are grouped under `/api/` for easy documentation
4. **Future-Proofing**: Easy to add API versioning later (e.g., `/api/v1/`, `/api/v2/`)

## 🚀 Platform Features

### 🤖 AI Chatbot (`/chatbot/`)
- Mistral AI integration with persistent conversations
- Real-time chat interface with session management

### 📝 Blog CMS (`/blog/`)
- Full content management with categories and tags
- SEO-optimized with rich metadata

### 🎨 Portfolio Showcase (`/portfolio/`)
- Project management with technologies and testimonials
- Gallery support and status tracking

### 👥 Team Management (`/about/`)
- Team member profiles with skills and experience
- Professional certifications tracking

### 🎸 Dusty Jukebox (`/jukebox/`)
- **Backend Audio Analysis**: Pure Python BPM/key detection using librosa (no JavaScript)
- **Interactive Guitar Fretboard**: Frontend fretboard with multiple tunings
- **Auto-composition**: Server-side melody generation using Python
- **Audio File Management**: Backend upload/playback with metadata storage
- **Session-based Preferences**: User settings stored in database

## 🏗️ Technical Architecture

### Core Technologies
- **Backend**: Django 5.0+ with Python 3.8+
- **AI**: Mistral AI models via HuggingFace
- **Audio**: librosa for analysis, pygame for playback
- **Database**: SQLite (dev) / PostgreSQL (prod)

### Dusty Jukebox Views

#### HTML Views:
```python
def dusty_jukebox_view(request):
    """Returns HTML template for audio player interface"""
    return render(request, 'dusty_jukebox/dusty_jukebox.html', context)

def guitar_bud_view(request):
    """Returns HTML template for guitar fretboard"""
    return render(request, 'dusty_jukebox/guitar_bud.html', context)
```

#### API Views (JSON):
```python
@require_GET
def get_audio_files(request):
    """Returns JSON list of user's audio files"""
    return JsonResponse({'files': files_data})

@require_POST
@csrf_exempt
def analyze_audio(request):
    """Returns JSON with BPM/key analysis results"""
    return JsonResponse({'success': True, 'bpm': bpm, 'key': key})
```

## 📁 Project Structure

```
360Dimension/
├── manage.py
├── settings.py
├── urls.py
├── db.sqlite3
├── dusty_jukebox/
│   ├── views.py          # HTML views + JSON API views
│   ├── urls.py           # URL patterns with /api/ prefix for APIs
│   ├── models.py         # AudioMetadata, GuitarTuning, etc.
│   ├── audio_analyser.py # Pure Python backend audio analysis (no JS)
│   └── templates/
│       ├── dusty_jukebox.html
│       └── guitar_bud.html
└── [other apps...]
```

## 🌐 URLs & Endpoints

### Dusty Jukebox URL Design

#### Main Interface:
- `/jukebox/` - Audio player (HTML)
- `/jukebox/guitar/` - Fretboard (HTML)
- `/jukebox/analyzer/` - Audio analyzer (HTML)

#### API Endpoints (all return JSON):
- `/jukebox/api/files/` - List audio files
- `/jukebox/api/upload/` - Upload files
- `/jukebox/api/analyze/` - Analyze audio
- `/jukebox/api/fretboard/` - Get fretboard data
- `/jukebox/api/play_melody/` - Play melody
- `/jukebox/api/auto_compose/` - Generate composition
- `/jukebox/api/scales/` - Get scales
- `/jukebox/api/tunings/` - Get tunings

## 🔧 Setup & Installation

```bash
# Install dependencies
pip install django librosa numpy pygame

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Start server
python manage.py runserver
```

## 🔄 Data Flow: JavaScript → Django → Python Script

### Audio Analysis Flow:
1. **JavaScript** sends AJAX request to `/jukebox/api/analyze/`
2. **Django view** (`analyze_audio`) calls `audio_analyser.py` as subprocess
3. **Python script** analyzes audio and prints results to stdout
4. **Django view** parses output and returns JSON to frontend

### API Usage Example:
```javascript
// Frontend JavaScript calls Django API
fetch('/jukebox/api/analyze/', {
  method: 'POST',
  body: JSON.stringify({path: "/audio/song.mp3"})
})
.then(response => response.json())
.then(data => {
  console.log(data); // {success: true, bpm: 128, key: "C Major"}
});
```

**Important**: `audio_analyser.py` is **pure Python backend code** - no JavaScript involved!

### Fretboard Data:
```javascript
// GET /jukebox/api/fretboard/?tuning=drop_d
// Returns: {"tuning": "Drop D", "strings": [...], "notes": {...}}
```

This design provides a clean, maintainable separation between user-facing HTML pages and programmatic API endpoints.
