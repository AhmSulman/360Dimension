from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import sqlite3
import os
import sys
import time
import datetime
import random
import string
import requests
import urllib.parse
import urllib.request
import json
from .models import (
    ChatbotConfig,  # Configuration for the Mistral chatbot model
    Conversation,    # A chat conversation session
    Message,         # An individual message in a conversation
    Tool,            # Available tools/functions that the chatbot can use
    MistralChatService,  # Service class for interacting with Mistral models
    create_conversation,  # Utility function to create new conversation
    get_mistral_service   # Utility function to get Mistral service instance
)


def chatbot(request):
    """Chatbot page - Initialize and display chat interface"""
    # Initialize default configuration if it doesn't exist
    from .models import get_default_config
    default_config_id = get_default_config()

    # Create a new conversation or get existing one
    session_id = request.session.get('chat_session_id')
    if not session_id:
        conversation = create_conversation(user=request.user if request.user.is_authenticated else None)
        request.session['chat_session_id'] = conversation.session_id
    else:
        conversation = get_object_or_404(Conversation, session_id=session_id)

    # Get conversation messages
    messages = conversation.get_messages()

    # Get available tools for display
    available_tools = Tool.objects.filter(is_active=True)

    return render(request, 'chatbot/chat.html', {
        'conversation': conversation,
        'messages': messages,
        'available_tools': available_tools
    })


@csrf_exempt
@require_POST
def chatbot_api(request):
    """API endpoint for chatbot interactions - Initialize all model classes"""

    try:
        # Parse request data
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        # Initialize/Get ChatbotConfig - Configuration for the Mistral chatbot model
        config = ChatbotConfig.objects.filter(is_active=True).first()
        if not config:
            # Create default config if none exists
            config = ChatbotConfig.objects.create(
                name="Default Mistral Config",
                mistral_api_key=os.environ.get("HF_API_TOKEN", ""),
                mistral_model="mistralai/Mistral-7B-Instruct-v0.3",
                mistral_model_version="v0.3",
                mistral_model_version_number=3,
                max_tokens=256,
                temperature=0.7
            )

        # Initialize/Get Conversation - A chat conversation session
        session_id = request.session.get('chat_session_id')
        if not session_id:
            conversation = create_conversation(user=request.user if request.user.is_authenticated else None)
            request.session['chat_session_id'] = conversation.session_id
        else:
            conversation = get_object_or_404(Conversation, session_id=session_id)

        # Ensure conversation has config
        if not conversation.config:
            conversation.config = config
            conversation.save()

        # Initialize MistralChatService - Service class for interacting with Mistral models
        service = MistralChatService(config)

        # Get available tools - Available tools/functions that the chatbot can use
        tools = list(Tool.objects.filter(is_active=True))

        # Generate response using the service
        response_message = service.chat(conversation, user_message)

        # Create response data with all initialized model information
        response_data = {
            'user_message': user_message,
            'assistant_message': response_message.content,
            'conversation_id': conversation.id,
            'message_id': response_message.id,
            'config_name': config.name,
            'model_version': config.mistral_model_version,
            'tools_used': len(tools),
            'session_id': conversation.session_id
        }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'error_type': type(e).__name__
        }, status=500)


def chatbot_config(request):
    """View to display and manage chatbot configurations"""
    configs = ChatbotConfig.objects.all()
    conversations = Conversation.objects.all()[:10]  # Recent conversations
    messages = Message.objects.all()[:20]  # Recent messages
    tools = Tool.objects.all()

    return render(request, 'chatbot/config.html', {
        'configs': configs,
        'conversations': conversations,
        'messages': messages,
        'tools': tools
    })
