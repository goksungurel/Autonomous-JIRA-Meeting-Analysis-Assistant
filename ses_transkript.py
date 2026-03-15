"""
Ses dosyalarını Whisper ile metne çevirir.
Opsiyonel: pyannote.audio ile konuşmacı diarization (kim ne söyledi).
"""
from dotenv import load_dotenv
load_dotenv()

import os
import ssl
import urllib.request
import whisper
from pyannote.audio import Pipeline

_ssl_unverified = ssl._create_unverified_context()
HF_TOKEN = os.environ.get("HF_TOKEN")


def sesi_metne_cevir(dosya_yolu: str, model_adi: str = "small") -> str:
    """Sadece Whisper ile transkript — eski davranış korundu."""
    _orig_urlopen = urllib.request.urlopen
    def _urlopen_no_verify(url, *args, **kwargs):
        if isinstance(url, str) and url.startswith("https://"):
            kwargs.setdefault("context", _ssl_unverified)
        return _orig_urlopen(url, *args, **kwargs)
    try:
        urllib.request.urlopen = _urlopen_no_verify
        model = whisper.load_model(model_adi)
    finally:
        urllib.request.urlopen = _orig_urlopen

    sonuc = model.transcribe(
        dosya_yolu,
        fp16=False,
        language="tr",
        initial_prompt="PostgreSQL, JIRA, API v2, Onboarding, Sprint, Whisper, Python",
    )
    return (sonuc.get("text") or "").strip()


def sesi_konusmacilarla_cevir(dosya_yolu: str, model_adi: str = "small") -> str:
    """
    Whisper + pyannote diarization.
    Kim ne söyledi formatında çıktı verir:
    [SPEAKER_00 - 00:03]: Merhaba, toplantıya hoş geldiniz.
    [SPEAKER_01 - 00:07]: Teşekkürler, başlayalım.
    """
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN environment variable eksik! Hugging Face tokenını ekle.")

    # 1. Whisper ile transkript al (zaman damgalı)
    model = whisper.load_model(model_adi)
    sonuc = model.transcribe(
        dosya_yolu,
        fp16=False,
        language="tr",
        initial_prompt="PostgreSQL, JIRA, API v2, Onboarding, Sprint",
        word_timestamps=True,
    )
    segmentler = sonuc.get("segments", [])

    # 2. pyannote ile kim konuştu bilgisini al
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=HF_TOKEN
    )
    diarizasyon = pipeline(dosya_yolu)

    # 3. Her Whisper segmentini en yakın konuşmacıyla eşleştir
    def konusmaci_bul(baslangic, bitis):
        max_kesisim = 0
        bulunan = "SPEAKER_??"
        for turn, _, speaker in diarizasyon.itertracks(yield_label=True):
            kesisim = min(bitis, turn.end) - max(baslangic, turn.start)
            if kesisim > max_kesisim:
                max_kesisim = kesisim
                bulunan = speaker
        return bulunan

    # 4. Çıktıyı birleştir
    satirlar = []
    for seg in segmentler:
        baslangic = seg["start"]
        bitis = seg["end"]
        metin = seg["text"].strip()
        konusmaci = konusmaci_bul(baslangic, bitis)
        dakika = int(baslangic // 60)
        saniye = int(baslangic % 60)
        satirlar.append(f"[{konusmaci} - {dakika:02d}:{saniye:02d}]: {metin}")

    return "\n".join(satirlar)