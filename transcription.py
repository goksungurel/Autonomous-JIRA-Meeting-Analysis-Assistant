"""
Transcribes audio files using OpenAI Whisper.
Optional: Includes pyannote.audio for speaker diarization (who said what).
"""
import os
import ssl
import whisper
import certifi
from dotenv import load_dotenv

load_dotenv()

# whisper.load_model() downloads the model over HTTPS using the interpreter's
# default SSL context, which on some macOS Python installs has no CA bundle
# configured. Point it at certifi's bundle instead of disabling verification.
_ssl_verified = ssl.create_default_context(cafile=certifi.where())
ssl._create_default_https_context = lambda: _ssl_verified

HF_TOKEN = os.environ.get("HF_TOKEN")

_MODEL_CACHE: dict[str, "whisper.Whisper"] = {}


def _load_model(model_name: str):
    if model_name not in _MODEL_CACHE:
        _MODEL_CACHE[model_name] = whisper.load_model(model_name)
    return _MODEL_CACHE[model_name]


def transcribe_audio_only(file_path: str, model_name: str = "small", language: str = "en") -> str:
    """Performs transcription using only Whisper — traditional behavior preserved."""
    model = _load_model(model_name)

    result = model.transcribe(
        file_path,
        fp16=False,
        language=language,
        initial_prompt="PostgreSQL, JIRA, API v2, Onboarding, Sprint, Whisper, Python, Backend, Frontend, Deployment, Repo, GitHub, Review, Test, Bug, Feature",
    )
    return (result.get("text") or "").strip()

def transcribe_with_diarization(file_path: str, model_name: str = "small", language: str = "en") -> str:
    """
    Combines Whisper + pyannote diarization.
    Outputs format: Who said what.
    [SPEAKER_00 - 00:03]: Hello, welcome to the meeting.
    [SPEAKER_01 - 00:07]: Thanks, let's start.
    """
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN environment variable is missing! Add your Hugging Face token.")

    try:
        from pyannote.audio import Pipeline
    except ImportError:
        raise ImportError(
            "pyannote.audio is not installed. "
            "Run: pip install pyannote.audio"
        )

    # 1. Get transcription with Whisper (with word timestamps)
    model = _load_model(model_name)
    result = model.transcribe(
        file_path,
        fp16=False,
        language=language,
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
    # Materialize the diarization turns once — itertracks() re-walks the whole
    # annotation on every call, so calling it per-segment was O(segments * turns).
    _turns = list(diarization.itertracks(yield_label=True))

    def find_speaker(start, end):
        max_intersection = 0
        found_speaker = "SPEAKER_??"
        for turn, _, speaker in _turns:
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