# englishAudioBot/textToSpeech.py

from gtts import gTTS
from io import BytesIO


async def generate_audio_bytes(text: str) -> BytesIO:
    """
    Generate TTS in English from the given text.
    Returns BytesIO so we can send it directly without saving to disk.
    """
    audio_fp = BytesIO()
    tts = gTTS(text, lang="en")
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)  # Move cursor back to the start
    return audio_fp
