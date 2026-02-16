import os
import signal
import tempfile

# CrewAI telemetry signal handler'ları Streamlit worker thread'inde hata veriyor;
# ana thread değilsek signal kaydını atlıyoruz.
_orig_signal = signal.signal
def _safe_signal(sig, handler):
    try:
        return _orig_signal(sig, handler)
    except ValueError:
        return None
signal.signal = _safe_signal

os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
import streamlit as st  # type: ignore[import-untyped]
from toplanti_asistani import analiz_et

st.set_page_config(page_title=" Meeting Analysis Assistant", layout="wide")

st.title("🤖 Meeting Analysis & JIRA Task Assistant")
st.markdown("---")

with st.sidebar:
    st.header("System Status")
    st.info("Model: Llama 3 (Local)")
    st.info("Embedding: Nomic-Embed-Text")
    st.success("RAG System: Active")
    st.info("Ses: Whisper (base)")
    st.caption("Ses için sistemde ffmpeg kurulu olmalı (örn. brew install ffmpeg)")

# Metin veya ses: .txt, .mp3, .wav
uploaded_file = st.file_uploader(
    "Toplantı transkripti (.txt) veya ses kaydı (.mp3, .wav) yükleyin",
    type=["txt", "mp3", "wav"],
)

if uploaded_file is not None:
    dosya_adi = uploaded_file.name
    uzanti = (dosya_adi.rsplit(".", 1)[-1].lower()) if "." in dosya_adi else ""

    # Dosya değiştiyse önceki ses transkriptini temizle
    if st.session_state.get("uploaded_file_name") != dosya_adi:
        st.session_state["uploaded_file_name"] = dosya_adi
        st.session_state.pop("transkript_metni", None)

    if uzanti == "txt":
        metin = uploaded_file.getvalue().decode("utf-8")
        st.text_area("Yüklenen Metin", metin, height=150)
        analiz_metni = metin
    else:
        # Ses dosyası: önce Whisper ile transkripte çevir
        if "transkript_metni" not in st.session_state:
            try:
                from ses_transkript import sesi_metne_cevir
            except ModuleNotFoundError:
                st.error(
                    "**Whisper kurulu değil.** Ses dosyalarını kullanmak için sanal ortamda kurun: "
                    "`pip install openai-whisper`"
                )
                st.stop()
            if st.button("🎤 Sesi metne çevir (Whisper)"):
                with st.status("Ses transkripte çevriliyor...", expanded=True) as status:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(dosya_adi)[1]) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    try:
                        st.session_state["transkript_metni"] = sesi_metne_cevir(tmp_path)
                    except Exception as e:
                        st.error(f"Ses transkript hatası: {e}")
                        st.stop()
                    finally:
                        try:
                            os.unlink(tmp_path)
                        except OSError:
                            pass
                    status.update(label="Transkript hazır.", state="complete", expanded=False)
                st.rerun()
            st.stop()
        analiz_metni = st.session_state["transkript_metni"]
        st.text_area("Ses dosyasından elde edilen metin (Whisper)", analiz_metni, height=150)

    if st.button("Analizi Başlat"):
        with st.status("Ajanlar çalışıyor, lütfen bekleyin...", expanded=True) as status:
            try:
                st.write("Toplantı Analisti dökümanları tarıyor...")
                sonuc = analiz_et(analiz_metni)
                status.update(label="Analiz Tamamlandı!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="Analiz hatası", state="error", expanded=True)
                st.error(f"Analiz hatası: {e}")
                st.stop()

        st.subheader("✅ JIRA Görevleri")
        st.markdown(sonuc)
