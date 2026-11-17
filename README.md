# 360Dimension - Full-Stack Django Platform

## Recent Updates & Fixes (Changelog)
- **Dusty Jukebox App Refactored**:
  - Replaced the failing local Pygame integration with a sleek Web Audio API frontend.
  - Users can now select and play local audio files directly in the browser without uploading them permanently.
  - Integrated `audio_analyser.py` via an API endpoint that handles intermediate temp files and correctly fetches BPM/Key analysis.
- **Chatbot App Refactored**:
  - Replaced the unoptimized local Mistral model loading (which struggled with memory constraints) with a fast, lightweight HTTP call to the Hugging Face Inference API. 
  - Reads the Hugging Face token from the `HF_API_TOKEN` environment variable, drastically improving response times and stability without needing heavy local models.
- **Application Validation**:
  - Verified migrations and template rendering for the `blog`, `portfolio`, `intro`, and `about` directories. All models are now cleanly accessible and will handle fallback data gracefully.

## Overview

360Dimension is a comprehensive Django-based platform featuring multiple interconnected applications including an AI-powered chatbot, blog CMS, portfolio showcase, and team management system. Built with modern web technologies and powered by Mistral AI models.

### 🤖 AI Chatbot
- **Mistral AI Integration**: Powered by Mistral 7B-Instruct-v0.3 model
- **Persistent Conversations**: Full database storage with session management
- **Tool Integration**: Function calling and custom AI tools support
- **Real-time Chat**: Modern AJAX-powered interface
- **Multi-Model Support**: Configurable for different Mistral versions

### 📝 Blog CMS
- **Full Content Management**: Posts, categories, tags, and comments
- **SEO Optimization**: Meta tags, slugs, and search engine friendly
- **Comment System**: Nested comments with approval workflow
- **Pagination**: Efficient content browsing
- **Rich Content**: Featured images, excerpts, and detailed posts

### 🎨 Portfolio Showcase
- **Project Management**: Complete project portfolios with technologies
- **Testimonials**: Client feedback and project validation
- **Technology Tracking**: Skills and tech stack management
- **Gallery Support**: Multiple project images and media
- **Status Tracking**: Project lifecycle management

### 👥 Team Management
- **Member Profiles**: Detailed team member information
- **Skills Tracking**: Proficiency levels and technology expertise
- **Experience Timeline**: Professional background and achievements
- **Certifications**: Professional credentials and validation
- **Social Integration**: LinkedIn, GitHub, and social media links

### 🎸 Dusty Jukebox
- **Audio Analysis**: BPM and key detection using librosa
- **Interactive Fretboard**: Guitar tuning visualization and note exploration
- **Music Composition**: Auto-composition and melody generation
- **Audio Playback**: File upload and playback with metadata display
- **Guitar Tools**: Multiple tunings and scale exploration

## 🏗️ Technical Architecture

### Core Technologies
- **Backend**: Django 5.0+ with Python 3.8+
- **Database**: SQLite (development) / PostgreSQL (production)
- **AI**: Mistral AI models with HuggingFace integration
- **Audio Analysis**: librosa, numpy for music analysis and BPM/key detection
- **Multimedia**: pygame for audio playback (optional)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **ORM**: Django Models with full relationships

## 📁 Project Structure

```
360Dimension/
├── _360Dimension/                    # Main Django project
│   ├── settings.py                   # Django settings & configuration
│   ├── urls.py                       # Main URL routing
│   └── wsgi.py                       # WSGI application entry point
├── intro/                           # Landing page application
│   ├── templates/intro/home.html    # Homepage with app navigation cards
│   ├── views.py                     # Homepage view logic
│   ├── urls.py                      # Intro URL routing
│   └── apps.py                      # Django app configuration
├── blog/                            # Full-featured blog CMS
│   ├── models.py                    # Post, Category, Tag, Comment models
│   ├── views.py                     # Blog views with pagination & filtering
│   ├── urls.py                      # Blog URL routing
│   ├── templates/blog/              # Blog templates (to be created)
│   ├── migrations/                  # Database migrations
│   └── apps.py                      # Django app configuration
├── portfolio/                       # Portfolio showcase application
│   ├── models.py                    # Project, Technology, Category models
│   ├── views.py                     # Portfolio views & project display
│   ├── urls.py                      # Portfolio URL routing
│   ├── templates/portfolio/         # Portfolio templates (to be created)
│   ├── migrations/                  # Database migrations
│   └── apps.py                      # Django app configuration
├── about/                           # Team & company information
│   ├── models.py                    # TeamMember, Skill, Experience models
│   ├── views.py                     # About page views
│   ├── urls.py                      # About URL routing
│   ├── templates/about/             # About templates (to be created)
│   ├── migrations/                  # Database migrations
│   └── apps.py                      # Django app configuration
├── chatbot/                         # AI-powered chatbot application
│   ├── models.py                    # Chatbot models & Mistral AI service
│   ├── views.py                     # Chat interface & API endpoints
│   ├── urls.py                      # Chatbot URL routing
│   ├── templates/chatbot/           # Chat interface templates
│   │   ├── chat.html               # Main chat interface
│   │   └── config.html             # Configuration dashboard
│   ├── migrations/                  # Database migrations
│   ├── management/commands/         # Django management commands
│   │   └── download_models.py      # Model download command
│   └── apps.py                      # Django app configuration
├── dusty_jukebox/                   # Audio analysis and guitar tools
│   ├── models.py                    # Audio metadata, tunings, scales models
│   ├── views.py                     # Audio player & fretboard views
│   ├── urls.py                      # Dusty Jukebox URL routing
│   ├── templates/dusty_jukebox/     # Audio player & fretboard templates
│   │   ├── dusty_jukebox.html      # Audio player interface
│   │   └── guitar_bud.html         # Guitar fretboard interface
│   ├── migrations/                  # Database migrations
│   ├── management/commands/         # Django management commands
│   │   └── populate_defaults.py    # Populate tunings & scales
│   ├── audio_analyser.py            # BPM/key detection script
│   └── apps.py                      # Django app configuration
├── db.sqlite3                       # SQLite database (development)
├── manage.py                        # Django management script
└── README.md                        # This documentation file
```

## 📱 Applications & Models

### 🤖 Chatbot Application

#### Core Models
- **ChatbotConfig**: AI model configuration and API settings
- **Conversation**: Chat sessions with unique identifiers
- **Message**: Individual chat messages (user/assistant/system)
- **Tool**: AI function calling capabilities

#### AI Service Layer
```python
class MistralChatService:
    # AI-powered conversation handling
    # Model downloads and initialization
    # Response generation with tool support
    # Database persistence for all interactions
```

### 📝 Blog CMS Application

#### Content Models
- **Post**: Blog articles with rich content and metadata
- **Category**: Hierarchical content organization
- **Tag**: Flexible content tagging system
- **Comment**: User engagement with nested replies

#### Key Features
- SEO-optimized URLs and meta tags
- Content approval workflow
- View tracking and analytics
- Related content suggestions

### 🎨 Portfolio Application

#### Project Models
- **Project**: Complete project showcases with media
- **Technology**: Tech stack tracking and proficiency
- **Category**: Project type classification
- **Testimonial**: Client feedback integration

#### Media Management
- Project galleries and image management
- Live demo and repository linking
- Technology showcase and filtering

### 👥 About/Team Application

#### Team Models
- **TeamMember**: Detailed team profiles and bios
- **Skill**: Technical and soft skills tracking
- **Experience**: Professional background and achievements
- **Education**: Academic credentials and certifications

#### Professional Features
- Social media integration
- Skills proficiency visualization
- Experience timeline display
- Certification management

### 🎸 Dusty Jukebox Application

#### Audio & Music Models
- **AudioMetadata**: BPM, key, and waveform analysis results
- **AudioFile**: Uploaded audio files with metadata links
- **GuitarTuning**: Guitar tunings with string configurations
- **MusicalScale**: Musical scales and modes for composition
- **UserSession**: User preferences and session data

#### Core Features
- Audio file upload and management
- BPM and key detection using librosa
- Interactive guitar fretboard visualization
- Auto-composition and melody generation
- Multiple guitar tunings support
- Waveform display and audio analysis

#### Audio Analysis Pipeline
```python
class AudioMetadata(models.Model):
    # File metadata and analysis results
    file_path, file_hash, bpm, key, is_minor
    waveform_data, analysis_date, duration

class AudioAnalyser:
    # BPM detection using librosa.beat.beat_track()
    # Key detection using chroma features
    # Waveform visualization and export
```

#### Guitar Tools Integration
```python
class GuitarTuning(models.Model):
    # Pre-defined and custom tunings
    name, display_name, string_notes, is_standard

class MusicalScale(models.Model):
    # Scales for composition and theory
    name, display_name, notes, intervals, tonality
```

## 📝 Complete Django Models Overview

### Blog App Models

#### Post Model
```python
class Post(models.Model):
    title, slug, excerpt, content, featured_image, author
    status, is_published, published_at, category, tags
    meta_title, meta_description, keywords
    view_count, like_count, created_at, updated_at
```

#### Category & Tag Models
```python
class Category(models.Model):  # Blog categories
    name, slug, description, color, is_active

class Tag(models.Model):  # Blog tags
    name, slug, color, is_active
```

#### Comment Model
```python
class Comment(models.Model):  # Post comments
    post, author_name, author_email, content, is_approved
    parent (for replies), created_at, updated_at
```

### Portfolio App Models

#### Project Model
```python
class Project(models.Model):
    title, slug, subtitle, description, detailed_description
    featured_image, gallery_images, status, visibility, is_active
    live_url, github_url, demo_url, start_date, end_date, launch_date
    category, technologies, owner, order, created_at, updated_at
```

#### Technology & Category Models
```python
class Technology(models.Model):  # Tech stack
    name, slug, icon, color, description, is_active

class Category(models.Model):  # Project categories
    name, slug, description, icon, color, is_active
```

#### Supporting Models
```python
class ProjectImage(models.Model):    # Additional project images
class Testimonial(models.Model):     # Client testimonials
```

### About App Models

#### TeamMember Model
```python
class TeamMember(models.Model):
    user, name, role, bio, avatar, avatar_emoji
    email, linkedin, github, twitter, website
    skills, experiences, is_active, is_featured, order
```

#### Skill Model
```python
class Skill(models.Model):
    name, category, proficiency, icon, color, description, is_active
    # Categories: programming, framework, database, tool, soft, other
```

#### Experience Model
```python
class Experience(models.Model):
    company_name, position, job_type, location, is_remote
    start_date, end_date, is_current, description, achievements
    company_website, company_logo, skills_used
```

#### Education Model
```python
class Education(models.Model):
    institution_name, degree, field_of_study, location
    start_date, end_date, is_current, gpa, description, achievements
```

#### Supporting Models
```python
class Certification(models.Model):  # Professional certifications
class Project(models.Model):       # Personal/side projects
```

## 🔧 Setup & Installation

### Prerequisites
- Python 3.8+
- Django 5.0+
- Audio Analysis: `pip install librosa numpy matplotlib`
- Audio Playback: `pip install pygame` (optional)
- Required packages (see requirements.txt if available)

### Database Setup
```bash
cd _360Dimension
python manage.py makemigrations  # Create migrations for all apps
python manage.py migrate         # Apply all migrations
```

### Create Sample Data (Optional)
After setting up the database, you can create sample data:

```python
# In Django shell: python manage.py shell
from django.contrib.auth.models import User
from blog.models import Category, Tag, Post
from portfolio.models import Technology, Category as PortfolioCategory, Project
from about.models import Skill, TeamMember

# Create sample blog categories
blog_cat = Category.objects.create(name="Technology", description="Tech articles")
ai_tag = Tag.objects.create(name="AI", color="#007bff")

# Create sample portfolio technologies
django_tech = Technology.objects.create(name="Django", icon="🐍")
react_tech = Technology.objects.create(name="React", icon="⚛️")

# Create sample skills
python_skill = Skill.objects.create(
    name="Python", category="programming", proficiency=90
)

# Create user for sample content
user = User.objects.create_user('admin', 'admin@example.com', 'password')
```

### Model Download
Download the required Mistral models:
```bash
python manage.py download_models
# Or download specific config:
python manage.py download_models --config-id 1
# Force re-download:
python manage.py download_models --force
```

## 🌐 URLs & Endpoints

### Platform URLs

#### Core Navigation
- `/` - Homepage with application showcase cards

#### Blog CMS (`/blog/`)
- `/blog/` - Blog index with recent posts and featured content
- `/blog/post/<slug>/` - Individual blog post with comments
- `/blog/category/<slug>/` - Posts filtered by category
- `/blog/tag/<slug>/` - Posts filtered by tag

#### Portfolio (`/portfolio/`)
- `/portfolio/` - Project showcase with filtering
- `/portfolio/project/<slug>/` - Detailed project view
- `/portfolio/category/<slug>/` - Projects by category
- `/portfolio/technology/<slug>/` - Projects by technology

#### About/Team (`/about/`)
- `/about/` - Team overview with skills and experience
- `/about/member/<id>/` - Individual team member profile
- `/about/skills/` - Detailed skills breakdown
- `/about/experience/` - Professional experience timeline

#### AI Chatbot (`/chatbot/`)
- `/chatbot/` - Interactive AI chat interface
- `/chatbot/config/` - Chatbot configuration dashboard
- `/chatbot/api/chatbot/` - Chat API endpoint for real-time conversations

#### Dusty Jukebox (`/jukebox/`)
- `/jukebox/` - Audio player with file management and analysis
- `/jukebox/guitar/` - Interactive guitar fretboard and composition tools
- `/jukebox/api/files/` - Audio files API endpoint
- `/jukebox/api/analyze/` - Audio analysis API (BPM/key detection)
- `/jukebox/api/play/` - Audio playback control API
- `/jukebox/api/fretboard/` - Guitar fretboard data API

### URL Configuration
```python
# chatbot/urls.py
urlpatterns = [
    path('', views.chatbot, name='chatbot'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    path('config/', views.chatbot_config, name='chatbot_config'),
]
```

## 🎨 Frontend Interface

### Chat Interface (`chat.html`)
- Modern, responsive design
- Real-time chat with JavaScript
- Message history display
- Typing indicators
- CSRF protection for API calls

### Configuration Dashboard (`config.html`)
- Overview of all model instances
- Recent conversations and messages
- Tool management
- Statistics display

### Key Features
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: AJAX-powered chat interactions
- **Session Management**: Persistent conversations across page reloads
- **Error Handling**: Comprehensive client-side error management

## 🔌 API Endpoints

### Chatbot API
**POST** `/chatbot/api/chatbot/`

Main chat API endpoint for AI conversations.

**Request:**
```json
{"message": "Hello, how are you?"}
```

**Response:**
```json
{
  "user_message": "Hello, how are you?",
  "assistant_message": "I'm doing well, thank you for asking!",
  "conversation_id": 1,
  "message_id": 123,
  "config_name": "Default Mistral Config",
  "model_version": "v0.3",
  "tools_used": 0,
  "session_id": "abc-123-def"
}
```

### Future APIs
- **Blog API**: `/blog/api/posts/` - Content management
- **Portfolio API**: `/portfolio/api/projects/` - Project data
- **Admin API**: `/api/admin/` - Administrative operations

## 🛠️ Usage Examples

### Chatbot Integration
```python
from chatbot.models import create_conversation, get_mistral_service

# Create a conversation
conversation = create_conversation(title="My Chat Session")

# Get the chat service
service = get_mistral_service()

# Send a message and get response
response = service.chat(conversation, "Hello, how are you?")
print(response.content)  # AI response
```

### Blog Content Management
```python
from blog.models import Post, Category, Tag
from django.contrib.auth.models import User

# Create blog content
author = User.objects.get(username='admin')
category = Category.objects.create(name="Technology", color="#007bff")

post = Post.objects.create(
    title="Getting Started with Django",
    content="Django is a powerful web framework...",
    author=author,
    category=category,
    status='published'
)
```

### Portfolio Project Creation
```python
from portfolio.models import Project, Technology, Category

# Create project showcase
web_dev = Category.objects.create(name="Web Development", icon="🌐")
django_tech = Technology.objects.create(name="Django", icon="🐍")

project = Project.objects.create(
    title="E-Commerce Platform",
    description="Modern e-commerce solution",
    category=web_dev,
    status='completed'
)
project.technologies.add(django_tech)
```

### Team Profile Management
```python
from about.models import TeamMember, Skill, Experience

# Create team member profile
member = TeamMember.objects.create(
    name="John Doe",
    role="Full Stack Developer",
    bio="Passionate developer with 5+ years experience"
)

# Add skills
python_skill = Skill.objects.create(
    name="Python",
    category="programming",
    proficiency=90
)
member.skills.add(python_skill)
```

## 🔧 Management Commands

### AI Model Management
```bash
# Download Mistral models for all active configurations
python manage.py download_models

# Download specific configuration
python manage.py download_models --config-id 1

# Force re-download existing models
python manage.py download_models --force
```

### Content Management
```bash
# Create superuser for admin access
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Collect static files for production
python manage.py collectstatic
```

## 🗃️ Database Schema

### Chatbot Tables
- **chatbot_chatbotconfig**: AI model configurations and API settings
- **chatbot_conversation**: Chat sessions with unique identifiers
- **chatbot_message**: Individual messages in conversations
- **chatbot_tool**: Available AI tools and functions

### Blog Tables
- **blog_post**: Blog articles with rich content and metadata
- **blog_category**: Content categorization with colors and descriptions
- **blog_tag**: Flexible tagging system for posts
- **blog_comment**: User comments with approval workflow

### Portfolio Tables
- **portfolio_project**: Project showcases with media and details
- **portfolio_technology**: Technology stack with proficiency tracking
- **portfolio_category**: Project type classifications
- **portfolio_testimonial**: Client feedback and validation
- **portfolio_projectimage**: Additional project media

### About/Team Tables
- **about_teammember**: Team member profiles and social links
- **about_skill**: Technical and soft skills with proficiency levels
- **about_experience**: Professional background and achievements
- **about_education**: Academic credentials and certifications
- **about_certification**: Professional credentials
- **about_project**: Personal/side projects

All tables include proper foreign key relationships, indexing, and Django admin integration for optimal performance and management.

## 🚀 Deployment Considerations

### Production Settings
- Set `DEBUG = False`
- Configure proper database (PostgreSQL recommended)
- Set up proper static file serving
- Configure environment variables for API keys
- Use proper caching for model loading

### Security
- API keys stored securely
- CSRF protection enabled
- Input validation and sanitization
- Rate limiting for API endpoints

### Performance
- Model caching to avoid reloads
- Database query optimization
- Background processing for heavy operations
- CDN for static assets

## 📊 Monitoring & Analytics

The configuration dashboard provides:
- Total conversations count
- Message statistics
- Tool usage metrics
- Model performance data
- Recent activity logs

## 🔄 Future Enhancements

Potential improvements:
- Multiple model support simultaneously
- Voice input/output capabilities
- File upload and processing
- Advanced tool integrations
- Conversation export/import
- Multi-language support
- Advanced analytics dashboard

## 🐛 Troubleshooting

### Common Issues

#### Template Errors
```
TemplateDoesNotExist: app/template.html
```
**Solution**: Ensure templates are in `app/templates/app/` directory structure

#### Database Errors
```
django.db.utils.OperationalError: no such table
```
**Solution**: Run migrations for all apps:
```bash
python manage.py makemigrations
python manage.py migrate
```

#### AI Model Issues
```
Exception: Failed to download Mistral models
```
**Solution**:
- Verify HuggingFace API key validity
- Check internet connection
- Ensure sufficient disk space
- Run: `python manage.py download_models --force`

#### Import Errors
```
ModuleNotFoundError: No module named 'app'
```
**Solution**: Add app to `INSTALLED_APPS` in `settings.py`

### Debug Configuration
Enable debug logging in Django settings:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 🚀 Development Roadmap

### Phase 1 (Current)
- ✅ Django model architecture for all apps
- ✅ AI chatbot with Mistral integration
- ✅ Basic CRUD operations
- ✅ Database migrations and relationships

### Phase 2 (Next)
- 🎨 Frontend templates for blog, portfolio, about
- 📱 Responsive design implementation
- 🔐 User authentication and permissions
- 📊 Admin dashboard enhancements

### Phase 3 (Future)
- 🌐 REST API development
- 📱 Mobile app integration
- 📈 Analytics and reporting
- 🔍 Advanced search functionality
- 🌍 Multi-language support

## 📊 Platform Statistics

- **5 Django Applications**: Intro, Blog, Portfolio, About, Chatbot
- **20+ Database Models**: Comprehensive data architecture
- **AI Integration**: Mistral 7B-Instruct model support
- **Modern UI**: Responsive web interface
- **Production Ready**: Scalable architecture with proper migrations

## 📞 Support & Contributing

### Getting Help
For issues or questions:
1. Check this README documentation
2. Review Django application logs
3. Verify database migrations are applied
4. Test with minimal examples
5. Check model configurations

### Contributing
1. Fork the repository
2. Create feature branch
3. Add comprehensive tests
4. Update documentation
5. Submit pull request

### License
This project is open source and available under the MIT License.

---

**Built with ❤️ using Django 5.0, Mistral AI, and modern web technologies**

*360Dimension - Where Innovation Meets Intelligence*
