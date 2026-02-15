import streamlit as st  # type: ignore[import-untyped]
import os
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
from toplanti_asistani import analiz_et

st.set_page_config(page_title="Nuevo AI Assistant", layout="wide")

st.title("🤖 Nuevo AI - Toplantı & JIRA Asistanı")
st.markdown("---")

with st.sidebar:
    st.header("Sistem Bilgileri")
    st.info("Model: Llama 3 (Local)")
    st.info("Embedding: Nomic-Embed-Text")
    st.success("RAG Sistemi: Aktif")

uploaded_file = st.file_uploader("Toplantı transkriptini (.txt) yükleyin", type="txt")

if uploaded_file is not None:
    metin = uploaded_file.read().decode("utf-8")
    st.text_area("Yüklenen Metin", metin, height=150)
    
    if st.button("Analizi Başlat"):
        with st.status("Ajanlar çalışıyor, lütfen bekleyin...", expanded=True) as status:
            st.write("Toplantı Analisti dökümanları tarıyor...")
            sonuc = analiz_et(metin)
            status.update(label="Analiz Tamamlandı!", state="complete", expanded=False)
        
        st.subheader("✅ JIRA Görevleri")
        st.markdown(sonuc)