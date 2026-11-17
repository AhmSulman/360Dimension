import os
from pathlib import Path
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
import json


class ChatbotConfig(models.Model):
    """Configuration for the Mistral chatbot model"""

    name = models.CharField(max_length=100, default="Mistral Chatbot")
    mistral_api_key = models.CharField(
        max_length=200, default="", blank=True
    )
    mistral_model = models.CharField(
        max_length=200, default="mistralai/Mistral-7B-Instruct-v0.3"
    )
    mistral_model_version = models.CharField(max_length=50, default="v0.3")
    mistral_model_version_number = models.IntegerField(default=3)
    max_tokens = models.IntegerField(default=256)
    temperature = models.FloatField(default=0.7)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Chatbot Configuration"
        verbose_name_plural = "Chatbot Configurations"

    def __str__(self):
        return f"{self.name} ({self.mistral_model_version})"

    @property
    def models_path(self):
        """Get the path where Mistral models are stored"""
        return Path.home().joinpath(
            "mistral_models", f"7B-Instruct-{self.mistral_model_version}"
        )

    def ensure_models_downloaded(self):
        """Ensure Mistral models are downloaded"""
        from huggingface_hub import snapshot_download

        self.models_path.mkdir(parents=True, exist_ok=True)

        try:
            snapshot = snapshot_download(
                repo_id=self.mistral_model,
                allow_patterns=[
                    "params.json",
                    "consolidated.safetensors",
                    "tokenizer.model.v3",
                ],
                local_dir=self.models_path,
            )
            return Path(snapshot)
        except Exception as e:
            raise Exception(f"Failed to download Mistral models: {str(e)}")


class Conversation(models.Model):
    """A chat conversation session"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=200, blank=True)
    config = models.ForeignKey(ChatbotConfig, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Conversation {self.session_id}" if not self.title else self.title

    def get_messages(self):
        """Get all messages in this conversation"""
        return self.messages.all().order_by("created_at")


class Message(models.Model):
    """An individual message in a conversation"""

    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System"),
    ]

    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    tokens_used = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class Tool(models.Model):
    """Available tools/functions that the chatbot can use"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    parameters = models.JSONField(help_text="JSON schema for tool parameters")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def to_function_dict(self):
        """Convert to the format expected by Mistral"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


# Default configuration instance
def get_default_config():
    """Get or create default chatbot configuration"""
    config, created = ChatbotConfig.objects.get_or_create(
        name="Default Mistral Config",
        defaults={
            "mistral_api_key": os.environ.get("HF_API_TOKEN", ""),
            "mistral_model": "mistralai/Mistral-7B-Instruct-v0.3",
            "mistral_model_version": "v0.3",
            "mistral_model_version_number": 3,
            "max_tokens": 256,
            "temperature": 0.7,
        },
    )
    return config.id


# Update Conversation to use default config
Conversation._meta.get_field("config").default = get_default_config


class MistralChatService:
    """Service class for interacting with Mistral models"""

    def __init__(self, config=None):
        self.config = config or ChatbotConfig.objects.filter(is_active=True).first()
        if not self.config:
            raise ValueError("No active chatbot configuration found")

    def generate_response(self, messages, tools=None, **kwargs):
        """Generate a response using Mistral Inference API via Hugging Face"""
        import requests

        # Prepare API endpoint and headers
        api_url = (
            f"https://api-inference.huggingface.co/models/{self.config.mistral_model}"
        )
        headers = {
            "Authorization": f"Bearer {self.config.mistral_api_key or os.environ.get('HF_API_TOKEN', '')}",
            "Content-Type": "application/json",
        }

        # Format prompt for Mistral Instruction model
        # Mistral Instruct format: <s>[INST] user message [/INST] assistant response </s>
        prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                # Simplified: prepend system message to the first user message
                prompt += f"[INST] System: {msg['content']}\n"
            elif msg["role"] == "user":
                prompt += f"{msg['content']} [/INST] "
            elif msg["role"] == "assistant":
                prompt += f"{msg['content']} </s> [INST] "

        # Clean up any trailing tags if the last message was user
        if not prompt.endswith("[/INST] "):
            prompt += " [/INST] "

        payload = {
            "inputs": prompt.strip(),
            "parameters": {
                "max_new_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "return_full_text": False,
            },
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
                return generated_text.strip()

            return "Sorry, I couldn't generate a response."

        except requests.exceptions.HTTPError as e:
            print(f"HTTPError: {e}")
            return f"Error connecting to AI service: {e.response.text if hasattr(e, 'response') else str(e)}"
        except Exception as e:
            print(f"Exception: {str(e)}")
            return f"Unexpected error: {str(e)}"

    def chat(self, conversation, user_message, **kwargs):
        """Handle a chat interaction"""
        # Get conversation history
        messages = []
        for msg in conversation.get_messages():
            messages.append({"role": msg.role, "content": msg.content})

        # Add the new user message
        messages.append({"role": "user", "content": user_message})

        # Get available tools (not fully supported by basic Inference API, but kept for context)
        tools = list(Tool.objects.filter(is_active=True))
        tool_dicts = [tool.to_function_dict() for tool in tools] if tools else None

        # Generate response
        response_text = self.generate_response(messages, tools=tool_dicts, **kwargs)

        # Save the user message
        Message.objects.create(
            conversation=conversation, role="user", content=user_message
        )

        # Save the assistant response
        assistant_message = Message.objects.create(
            conversation=conversation, role="assistant", content=response_text
        )

        # Update conversation timestamp
        conversation.save()

        return assistant_message


# Utility functions for backward compatibility
def get_mistral_service(config=None):
    """Get a MistralChatService instance"""
    return MistralChatService(config)


def create_conversation(user=None, session_id=None, title=""):
    """Create a new conversation"""
    if not session_id:
        import uuid

        session_id = str(uuid.uuid4())

    return Conversation.objects.create(user=user, session_id=session_id, title=title)


# Example usage:
"""
# Create a conversation
conversation = create_conversation(title="My Chat Session")

# Get the chat service
service = get_mistral_service()

# Chat
response = service.chat(conversation, "Hello, how are you?")
print(response.content)
"""


# Management command helper for downloading models
class ModelDownloader:
    """Helper class for downloading Mistral models"""

    @staticmethod
    def download_all_active_models():
        """Download all models for active configurations"""
        configs = ChatbotConfig.objects.filter(is_active=True)
        for config in configs:
            try:
                print(f"Downloading model for config: {config.name}")
                config.ensure_models_downloaded()
                print(f"Successfully downloaded model for: {config.name}")
            except Exception as e:
                print(f"Failed to download model for {config.name}: {str(e)}")
