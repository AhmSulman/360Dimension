from pathlib import Path
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
import json


class ChatbotConfig(models.Model):
    """Configuration for the Mistral chatbot model"""
    name = models.CharField(max_length=100, default="Mistral Chatbot")
    mistral_api_key = models.CharField(max_length=200, default="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")
    mistral_model = models.CharField(max_length=200, default="mistralai/Mistral-7B-Instruct-v0.3")
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
        return Path.home().joinpath('mistral_models', f'7B-Instruct-{self.mistral_model_version}')

    def ensure_models_downloaded(self):
        """Ensure Mistral models are downloaded"""
        from huggingface_hub import snapshot_download

        self.models_path.mkdir(parents=True, exist_ok=True)

        try:
            snapshot = snapshot_download(
                repo_id=self.mistral_model,
                allow_patterns=["params.json", "consolidated.safetensors", "tokenizer.model.v3"],
                local_dir=self.models_path
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
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conversation {self.session_id}" if not self.title else self.title

    def get_messages(self):
        """Get all messages in this conversation"""
        return self.messages.all().order_by('created_at')


class Message(models.Model):
    """An individual message in a conversation"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    tokens_used = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

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
            "parameters": self.parameters
        }


# Default configuration instance
def get_default_config():
    """Get or create default chatbot configuration"""
    config, created = ChatbotConfig.objects.get_or_create(
        name="Default Mistral Config",
        defaults={
            'mistral_api_key': "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",
            'mistral_model': "mistralai/Mistral-7B-Instruct-v0.3",
            'mistral_model_version': "v0.3",
            'mistral_model_version_number': 3,
            'max_tokens': 256,
            'temperature': 0.7,
        }
    )
    return config.id


# Update Conversation to use default config
Conversation._meta.get_field('config').default = get_default_config


class MistralChatService:
    """Service class for interacting with Mistral models"""

    def __init__(self, config=None):
        self.config = config or ChatbotConfig.objects.filter(is_active=True).first()
        if not self.config:
            raise ValueError("No active chatbot configuration found")

        # Ensure models are downloaded
        self.model_path = self.config.ensure_models_downloaded()
        self._tokenizer = None
        self._model = None

    @property
    def tokenizer(self):
        """Lazy load tokenizer"""
        if self._tokenizer is None:
            try:
                from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
                tokenizer_path = self.model_path / "tokenizer.model.v3"
                self._tokenizer = MistralTokenizer.from_file(str(tokenizer_path))
            except ImportError:
                # Fallback to transformers tokenizer
                from transformers import AutoTokenizer
                self._tokenizer = AutoTokenizer.from_pretrained(self.config.mistral_model)
        return self._tokenizer

    @property
    def model(self):
        """Lazy load model"""
        if self._model is None:
            try:
                from mistral_inference.transformer import Transformer
                self._model = Transformer.from_folder(self.model_path)
            except ImportError:
                # Fallback to transformers model
                from transformers import AutoModelForCausalLM
                import torch
                self._model = AutoModelForCausalLM.from_pretrained(
                    self.config.mistral_model,
                    torch_dtype=torch.bfloat16,
                    device_map="auto"
                )
        return self._model

    def generate_response(self, messages, tools=None, **kwargs):
        """Generate a response using Mistral model"""
        try:
            # Try using mistral-inference first
            from mistral_common.protocol.instruct.messages import UserMessage, AssistantMessage, SystemMessage
            from mistral_common.protocol.instruct.request import ChatCompletionRequest

            # Convert messages to Mistral format
            mistral_messages = []
            for msg in messages:
                if msg['role'] == 'user':
                    mistral_messages.append(UserMessage(content=msg['content']))
                elif msg['role'] == 'assistant':
                    mistral_messages.append(AssistantMessage(content=msg['content']))
                elif msg['role'] == 'system':
                    # Add system message as user message with system prefix
                    mistral_messages.append(UserMessage(content=f"System: {msg['content']}"))

            # Create completion request
            request_kwargs = {
                'messages': mistral_messages,
                'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
                'temperature': kwargs.get('temperature', self.config.temperature),
            }

            if tools:
                # Convert tools to Mistral format
                from mistral_common.protocol.instruct.tool_calls import Function, Tool as MistralTool
                mistral_tools = []
                for tool in tools:
                    mistral_tools.append(MistralTool(
                        function=Function(
                            name=tool['name'],
                            description=tool['description'],
                            parameters=tool['parameters']
                        )
                    ))
                request_kwargs['tools'] = mistral_tools

            completion_request = ChatCompletionRequest(**request_kwargs)

            # Tokenize
            tokens = self.tokenizer.encode_chat_completion(completion_request).tokens

            # Generate
            from mistral_inference.generate import generate
            out_tokens, _ = generate(
                [tokens],
                self.model,
                max_tokens=request_kwargs['max_tokens'],
                temperature=request_kwargs['temperature'],
                eos_id=self.tokenizer.instruct_tokenizer.tokenizer.eos_id
            )

            # Decode
            result = self.tokenizer.instruct_tokenizer.tokenizer.decode(out_tokens[0])
            return result

        except ImportError:
            # Fallback to transformers
            return self._generate_with_transformers(messages, tools, **kwargs)

    def _generate_with_transformers(self, messages, tools=None, **kwargs):
        """Generate response using Hugging Face transformers"""
        from transformers import pipeline

        if tools:
            # Use tool-enabled generation
            from transformers import AutoTokenizer
            import torch

            tokenizer = AutoTokenizer.from_pretrained(self.config.mistral_model)
            model = self.model  # This will load the transformers model

            # Format conversation for tool use
            inputs = tokenizer.apply_chat_template(
                messages,
                tools=[tool.to_function_dict() if hasattr(tool, 'to_function_dict') else tool for tool in (tools or [])],
                add_generation_prompt=True,
                return_dict=True,
                return_tensors="pt",
            )

            inputs.to(model.device)
            outputs = model.generate(
                **inputs,
                max_new_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                temperature=kwargs.get('temperature', self.config.temperature),
                do_sample=True
            )

            result = tokenizer.decode(outputs[0], skip_special_tokens=True)
            return result
        else:
            # Simple text generation
            chatbot = pipeline(
                "text-generation",
                model=self.config.mistral_model,
                tokenizer=self.config.mistral_model
            )

            # Format messages for pipeline
            formatted_messages = []
            for msg in messages:
                if msg['role'] == 'system':
                    formatted_messages.append({"role": "system", "content": msg['content']})
                elif msg['role'] == 'user':
                    formatted_messages.append({"role": "user", "content": msg['content']})
                elif msg['role'] == 'assistant':
                    formatted_messages.append({"role": "assistant", "content": msg['content']})

            outputs = chatbot(
                formatted_messages,
                max_new_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                temperature=kwargs.get('temperature', self.config.temperature),
                do_sample=True
            )

            # Extract the generated text
            if isinstance(outputs, list) and len(outputs) > 0:
                generated_text = outputs[0].get('generated_text', '')
                # Remove the input messages from the output
                for msg in formatted_messages:
                    if msg['role'] == 'user':
                        generated_text = generated_text.replace(msg['content'], '', 1)
                    elif msg['role'] == 'assistant':
                        generated_text = generated_text.replace(msg['content'], '', 1)
                return generated_text.strip()

            return "Sorry, I couldn't generate a response."

    def chat(self, conversation, user_message, **kwargs):
        """Handle a chat interaction"""
        # Get conversation history
        messages = []
        for msg in conversation.get_messages():
            messages.append({
                'role': msg.role,
                'content': msg.content
            })

        # Add the new user message
        messages.append({
            'role': 'user',
            'content': user_message
        })

        # Get available tools
        tools = list(Tool.objects.filter(is_active=True))
        tool_dicts = [tool.to_function_dict() for tool in tools] if tools else None

        # Generate response
        response = self.generate_response(messages, tools=tool_dicts, **kwargs)

        # Save the user message
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )

        # Save the assistant response
        assistant_message = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=response
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

    return Conversation.objects.create(
        user=user,
        session_id=session_id,
        title=title
    )


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