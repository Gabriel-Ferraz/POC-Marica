import os
import tempfile


async def speech_to_text(audio_bytes: bytes, mime_type: str = "audio/wav") -> str:
    """Convert audio bytes to text. Uses mock in POC."""
    return "Olá, gostaria de abrir uma nova solicitação de protocolo administrativo."


async def text_to_speech(text: str) -> bytes:
    """Convert text to audio bytes. Returns mock silent WAV in POC."""
    wav_header = (
        b"RIFF" + (36).to_bytes(4, "little") +
        b"WAVE" +
        b"fmt " + (16).to_bytes(4, "little") +
        (1).to_bytes(2, "little") +      # PCM
        (1).to_bytes(2, "little") +      # mono
        (22050).to_bytes(4, "little") +  # sample rate
        (44100).to_bytes(4, "little") +  # byte rate
        (2).to_bytes(2, "little") +      # block align
        (16).to_bytes(2, "little") +     # bits per sample
        b"data" + (0).to_bytes(4, "little")
    )
    return wav_header
