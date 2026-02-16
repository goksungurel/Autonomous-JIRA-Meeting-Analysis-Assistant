"""
Ses dosyalarını Whisper ile metne çevirir.
Desteklenen formatlar: .mp3, .wav (ffmpeg ile açılabilen diğer formatlar da çalışabilir).
"""

import ssl
import urllib.request
import whisper  # type: ignore[import-untyped]

# Proxy/kurumsal ağda self-signed sertifica için: indirme sırasında SSL doğrulamasız context
_ssl_unverified = ssl._create_unverified_context()


def sesi_metne_cevir(dosya_yolu: str, model_adi: str = "small") -> str:
    """
    Ses dosyasını Whisper ile transkripte çevirir.

    Args:
        dosya_yolu: Ses dosyasının yerel yolu (.mp3, .wav vb.)
        model_adi: Whisper model boyutu: "tiny", "base", "small", "medium", "large"

    Returns:
        Transkript metni (UTF-8).
    """
    # Model indirme: urllib.urlopen SSL doğrulaması atlanıyor (CERTIFICATE_VERIFY_FAILED önlemek için)
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
