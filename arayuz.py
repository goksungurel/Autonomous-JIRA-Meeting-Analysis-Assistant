import os
import signal
import tempfile
import streamlit as st

# CrewAI Telemetry bypass
_orig_signal = signal.signal
def _safe_signal(sig, handler):
    try:
        return _orig_signal(sig, handler)
    except ValueError:
        return None
signal.signal = _safe_signal
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"

from toplanti_asistani import analiz_et

st.set_page_config(page_title="AI Meeting Assistant", layout="wide")
st.title("🤖 Meeting Analysis & Otonom JIRA Asistanı")
st.markdown("---")

with st.sidebar:
    st.header("Sistem Durumu")
    st.info("Ajan Modeli: Llama 3 (Ollama)")
    st.info("Embedding: Nomic-Embed-Text")
    st.success("RAG Sistemi: Aktif")
    st.info("Ses Modeli: Whisper (Small)")

uploaded_file = st.file_uploader(
    "Toplantı transkripti (.txt) veya ses kaydı (.mp3, .wav) yükleyin",
    type=["txt", "mp3", "wav"],
)

if uploaded_file is not None:
    dosya_adi = uploaded_file.name
    uzanti = (dosya_adi.rsplit(".", 1)[-1].lower()) if "." in dosya_adi else ""

    if st.session_state.get("uploaded_file_name") != dosya_adi:
        st.session_state["uploaded_file_name"] = dosya_adi
        st.session_state.pop("transkript_metni", None)

    if uzanti == "txt":
        metin = uploaded_file.getvalue().decode("utf-8")
        st.text_area("Yüklenen Metin", metin, height=150)
        analiz_metni = metin
    else:
        if "transkript_metni" not in st.session_state:
            try:
                from ses_transkript import sesi_metne_cevir
            except ModuleNotFoundError:
                st.error("Whisper kurulu değil. `pip install openai-whisper` ile kurun.")
                st.stop()
                
            if st.button("🎤 Sesi Metne Çevir (Whisper)"):
                with st.status("Ses transkripte çevriliyor...", expanded=True) as status:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(dosya_adi)[1]) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    try:
                        st.session_state["transkript_metni"] = sesi_metne_cevir(tmp_path)
                    except Exception as e:
                        st.error(f"Hata: {e}")
                        st.stop()
                    finally:
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
                    status.update(label="Transkript hazır.", state="complete", expanded=False)
                st.rerun()
            st.stop()
            
        analiz_metni = st.session_state["transkript_metni"]
        st.text_area("Whisper Transkripti", analiz_metni, height=150)

    if st.button("🧠 Ajanları Çalıştır ve JIRA'ya Aktar"):
        with st.status("Otonom ajanlar analiz yapıyor ve JIRA ile konuşuyor...", expanded=True) as status:
            try:
                sonuc = analiz_et(analiz_metni)
                status.update(label="İşlem Tamamlandı!", state="complete", expanded=False)
                st.subheader("✅ JIRA Görev Çıktısı")
                st.markdown(sonuc.raw) # CrewAI V2+ için .raw kullanmak daha garantidir
            except Exception as e:
                status.update(label="Ajan Hatası", state="error", expanded=True)
                st.error(f"Hata detayı: {e}")