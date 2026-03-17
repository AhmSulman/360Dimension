# Learning Django Through 360Dimension

Welcome! This tutorial will teach you the fundamentals of Django by looking at how the **360Dimension** project and its apps (`dusty_jukebox`, `chatbot`, `blog`, etc.) are constructed. 

Django uses an architectural pattern known as MTV (**Model-Template-View**). This separates your data (Model), your logic (View), and your user interface (Template).

## Architecture Flowchart

Below is a Mermaid flowchart demonstrating how a user's request travels through a Django App (for example, generating a Chatbot response or calculating BPM in the Dusty Jukebox).

```mermaid
flowchart TD
    User([User (Browser)]) -->|1. HTTP Request (e.g., POST /analyze/)| URLs[urls.py (Url Dispatcher)]
    URLs -->|2. Routes to appropriate View| Views[views.py (Logic)]
    Views -->|3. Queries / Updates Data| Models[(models.py (Database))]
    Models -->|4. Returns Data| Views
    Views -->|5. Processes logic (e.g., HuggingFace API, librosa)| Views
    Views -->|6. Passes context data| Templates[templates/ (HTML/CSS/JS)]
    Templates -->|7. Renders final page / JSON| Views
    Views -->|8. HTTP Response / JSON Response| User
```

## 1. Models (`models.py`)
Models tell Django how your database tables should look. Django handles the SQL for you underneath (an ORM - Object-Relational Mapper).

**Example from `chatbot/models.py`**:
```python
class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[('user', 'User'), ('assistant', 'Assistant')])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```
- `models.Model`: Every model inherits from this.
- `CharField`, `TextField`: Represent SQL columns.
- `ForeignKey`: Links this message to a specific Conversation (One-to-Many relationship).

## 2. Views (`views.py`)
Views act as the middleman. They receive the request, fetch data from Models, perform business logic, and send a response (either an HTML page or JSON).

**Example from `dusty_jukebox/views.py`**:
```python
@require_POST
def analyze_audio(request):
    audio_file = request.FILES['file']
    # Business logic: save file temporarily, run analyzer, get BPM
    bpm = calculate_bpm(audio_file)
    
    # Return JSON to the frontend
    return JsonResponse({'success': True, 'bpm': bpm})
```
In standard views, instead of `JsonResponse`, you might use `render(request, 'template.html', context_data)`.

## 3. Templates (`templates/*.html`)
Templates are standard HTML files but with a special syntax called Django Template Language (DTL) that allows you to inject Python variables. 

**Example from `portfolio/templates/index.html`**:
```html
<div class="project-list">
    <!-- Looping through projects sent by the view -->
    {% for project in projects %}
        <div class="card">
            <h2>{{ project.title }}</h2>
            <p>{{ project.description }}</p>
        </div>
    {% empty %}
        <p>No projects available.</p>
    {% endfor %}
</div>
```
- `{% ... %}`: Logic tags (loops, ifs).
- `{{ ... }}`: Variable injection.

## 4. URLs (`urls.py`)
URLs connect specific web addresses to the precise View function that handles them.

**Example**:
```python
from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_audio, name='analyze_audio'),
    path('chat/', views.chatbot_view, name='chat'),
]
```

## The Debugging Methodology Used in This Project

When your apps (`dusty_jukebox` and `chatbot`) were failing, here is the thought process applied to fix them—an excellent lesson in Django App Architecture!

### Fix 1: The Chatbot App API Setup
**Problem:** The app attempted to download a massive 15GB AI model straight to your local PC utilizing `mistral_inference`, causing timeouts and crashes.
**Solution (in `views.py` & `models.py`):**
Instead of loading AI into the Django Server's memory, we re-wrote the service to act as a **client**. We used Python's `requests` library to send an HTTP POST to the Hugging Face API containing the prompt and the provided hardcoded token. We then saved the returned text using `Message.objects.create(...)`.

### Fix 2: The Dusty Jukebox App File Flow
**Problem:** The app expected files to be permanently uploaded (`models.AudioFile`) before doing anything, and it expected a Python library (`pygame`) to magically play audio on the *server side* rather than the *user's browser*.
**Solution:**
1. **Templates:** Modified `dusty_jukebox.html` to use the standard HTML5 `<audio>` tag and JavaScript (`URL.createObjectURL(file)`). This allowed immediate playback on the user side.
2. **Views (`views.py`):** Rewrote the `analyze_audio` function. It now accepts the file dynamically via Javascript `FormData()`, saves it to the operating system's temporary directory (`tempfile.gettempdir()`), runs the Librosa analysis script (`audio_analyser.py`), yields the BPM/Key, deletes the temp file, and responds with a fast JSON array. No need for complex JSON database structures!

## Conclusion
By keeping your data structured in **Models**, putting the heavy lifting/API calls in **Views**, sending clean variables to **Templates**, and bridging them with **URLs**, Django lets you scale applications massively while keeping your code cleanly separated.
