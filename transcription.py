"""
Transcribes audio files using OpenAI Whisper.
Optional: Includes pyannote.audio for speaker diarization (who said what).
"""
import os
import ssl
import urllib.request
import whisper
from pyannote.audio import Pipeline
from dotenv import load_dotenv

load_dotenv()

_ssl_unverified = ssl._create_unverified_context()
HF_TOKEN = os.environ.get("HF_TOKEN")

def transcribe_audio_only(file_path: str, model_name: str = "small") -> str:
    """Performs transcription using only Whisper — traditional behavior preserved."""
    _orig_urlopen = urllib.request.urlopen
    def _urlopen_no_verify(url, *args, **kwargs):
        if isinstance(url, str) and url.startswith("https://"):
            kwargs.setdefault("context", _ssl_unverified)
        return _orig_urlopen(url, *args, **kwargs)
    try:
        urllib.request.urlopen = _urlopen_no_verify
        model = whisper.load_model(model_name)
    finally:
        urllib.request.urlopen = _orig_urlopen

    result = model.transcribe(
        file_path,
        fp16=False,
        language="tr", # Set language of the AUDIO. Agents will handle English translation.
        initial_prompt="PostgreSQL, JIRA, API v2, Onboarding, Sprint, Whisper, Python, Backend, Frontend, Deployment, Repo, GitHub, Review, Test, Bug, Feature",
    )
    return (result.get("text") or "").strip()

def transcribe_with_diarization(file_path: str, model_name: str = "small") -> str:
    """
    Combines Whisper + pyannote diarization.
    Outputs format: Who said what.
    [SPEAKER_00 - 00:03]: Hello, welcome to the meeting.
    [SPEAKER_01 - 00:07]: Thanks, let's start.
    """
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN environment variable is missing! Add your Hugging Face token.")

    # 1. Get transcription with Whisper (with word timestamps)
    model = whisper.load_model(model_name)
    result = model.transcribe(
        file_path,
        fp16=False,
        language="tr", # Set language of the AUDIO. Agents will handle English translation.
        initial_prompt="PostgreSQL, JIRA, API v2, Onboarding, Sprint, Backend, Frontend",
        word_timestamps=True,
    )
    segments = result.get("segments", [])

    # 2. Get speaker diarization with pyannote
    # Make sure your pyannote model is updated to use the new Hugging Face parameters
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        token=HF_TOKEN # Use 'token' instead of 'use_auth_token' for newer versions
    )
    diarization = pipeline(file_path)

    # 3. Match each Whisper segment with the closest speaker
    def find_speaker(start, end):
        max_intersection = 0
        found_speaker = "SPEAKER_??"
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            intersection = min(end, turn.end) - max(start, turn.start)
            if intersection > max_intersection:
                max_intersection = intersection
                found_speaker = speaker
        return found_speaker

    # 4. Combine the output
    lines = []
    for seg in segments:
        start = seg["start"]
        end = seg["end"]
        text = seg["text"].strip()
        speaker = find_speaker(start, end)
        minutes = int(start // 60)
        seconds = int(start % 60)
        # We output in English format because the agents are now English-speaking
        lines.append(f"[{speaker} - {minutes:02d}:{seconds:02d}]: {text}")

    return "\n".join(lines)