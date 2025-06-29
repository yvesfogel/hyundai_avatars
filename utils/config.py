"""
Configuration settings for the Hyundai Voice Assistant.
"""

import os
from dotenv import load_dotenv

class Config:
    """Configuration class for the Hyundai Voice Assistant."""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # API Keys
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "your_anthropic_api_key_here")
        self.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your_deepseek_api_key_here")
        self.ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "your_elevenlabs_api_key_here")

        # AI Model Settings
        self.AI_PROVIDER = os.getenv("AI_PROVIDER", "fastest")
        self.CHATGPT_MODEL = os.getenv("CHATGPT_MODEL", "gpt-4o-mini")
        self.CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet")
        self.DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        # Local LLM Settings (Ollama)
        self.USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
        self.OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "mistral:7b")
        self.LOCAL_LLM_TEMPERATURE = float(os.getenv("LOCAL_LLM_TEMPERATURE", "0.7"))
        self.LOCAL_LLM_MAX_TOKENS = int(os.getenv("LOCAL_LLM_MAX_TOKENS", "500"))
        
        self.SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "Eres un asistente de voz útil y amigable, contestas preguntas de la marca Hyundai. 1. Responde en español de manera natural y conversacional. 2. Muchas veces la informacion te va a llegar entrecortada, intenta completar la pregunta del usuario segun el contexto. 3. No le digas nunca que la pregunta esta incompleta, intenta completarla segun el contexto. 4. Siempre que puedas, intenta completar la pregunta del usuario segun el contexto.")

        # Language Settings
        self.LANGUAGE = os.getenv("LANGUAGE", "es")

        # Audio Settings
        self.AUDIO_DEVICE = int(os.getenv("AUDIO_DEVICE", "2")) if os.getenv("AUDIO_DEVICE") else None
        self.SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))  # Silero VAD works best at 16kHz
        self.TARGET_SAMPLE_RATE = int(os.getenv("TARGET_SAMPLE_RATE", "24000"))  # Target sample rate for TTS output
        self.CHANNELS = int(os.getenv("CHANNELS", "1"))
        self.MIN_PHRASE_DURATION = float(os.getenv("MIN_PHRASE_DURATION", "0.5"))
        
        # Silero VAD Settings
        self.SILENCE_TIMEOUT = float(os.getenv("SILENCE_TIMEOUT", "1.5"))  # Seconds of silence before stopping recording
        self.MIN_SPEECH_DURATION = float(os.getenv("MIN_SPEECH_DURATION", "0.3"))  # Minimum speech duration to consider valid

        # Audio File Paths
        self.TEMP_AUDIO_PATH = "temp_audio.wav"
        self.RESPONSE_AUDIO_PATH = "response_audio.wav"

        # ElevenLabs Settings
        self.ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "AvFwmpNEfWWu5mtNDqhH")
        self.ELEVENLABS_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_flash_v2_5")
        self.VOICE_SETTINGS = {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }

        # Unreal Engine Settings
        self.UE5_CONNECTION_METHOD = os.getenv("UE5_CONNECTION_METHOD", "remote_exec")
        self.UE5_HOST = os.getenv("UE5_HOST", "127.0.0.1")
        self.UE5_PORT = int(os.getenv("UE5_PORT", "8080"))
        self.UE5_PROJECT_PATH = os.getenv("UE5_PROJECT_PATH", "C:\\Users\\YourUsername\\Documents\\Unreal Projects\\hyundai_26mar25\\hyundai_26mar25.uproject")

        # GRPC Settings
        self.USE_GRPC = os.getenv("USE_GRPC", "true").lower() == "true"
        
        # Audio2Face Settings
        self.AUDIO2FACE_HOST = os.getenv("AUDIO2FACE_HOST", "127.0.0.1")
        self.AUDIO2FACE_PORT = int(os.getenv("AUDIO2FACE_PORT", "50051"))
        
        # Streaming Pipeline Settings
        self.USE_STREAMING_PIPELINE = os.getenv("USE_STREAMING_PIPELINE", "true").lower() == "true"
        self.STREAMING_CHUNK_STRATEGY = os.getenv("STREAMING_CHUNK_STRATEGY", "semantic")  # "semantic", "sentence", "phrase", "pause"
        self.STREAMING_MAX_WORKERS = int(os.getenv("STREAMING_MAX_WORKERS", "3"))
        self.STREAMING_MIN_CHUNK_SIZE = int(os.getenv("STREAMING_MIN_CHUNK_SIZE", "20"))
        self.STREAMING_MAX_CHUNK_SIZE = int(os.getenv("STREAMING_MAX_CHUNK_SIZE", "200"))

# Create a global instance
config = Config()

# Export all settings as module-level variables for backward compatibility
print("DEBUG: Exporting config variables...")
for key, value in config.__dict__.items():
    if not key.startswith('_'):
        globals()[key] = value
        print(f"DEBUG: Exported {key} = {value}")
print("DEBUG: Config export completed")