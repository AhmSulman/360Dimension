from django.shortcuts import render


def home(request):
    """Main intro page with navigation to different apps"""
    apps = [
        {
            "name": "Blog",
            "url": "/blog/",
            "description": "Read our latest articles and posts",
            "icon": "📝",
        },
        {
            "name": "Portfolio",
            "url": "/portfolio/",
            "description": "View our projects and work samples",
            "icon": "🎨",
        },
        {
            "name": "About",
            "url": "/about/",
            "description": "Learn more about us",
            "icon": "ℹ️",
        },
        {
            "name": "Chatbot",
            "url": "/chatbot/",
            "description": "Talk to our AI assistant powered by Mistral",
            "icon": "🤖",
        },
        {
            "name": "Dusty Jukebox Analyzer",
            "url": "/jukebox/",
            "description": "Audio player with BPM & Key analysis",
            "icon": "💿",
        },
        {
            "name": "Guitar Bud",
            "url": "/jukebox/guitar/",
            "description": "Interactive Fretboard and Composition toolkit",
            "icon": "🎸",
        },
        {
            "name": "Piano Tutor",
            "url": "/jukebox/piano/",
            "description": "Test your skills on this beautiful interactive Piano",
            "icon": "🎹",
        },
    ]
    return render(request, "intro/home.html", {"apps": apps})
