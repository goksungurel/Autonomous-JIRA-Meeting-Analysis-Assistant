"""
Streamlit UI for the AI Meeting Assistant. Completely translated to English.
"""
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

# Refactored imports
from meeting_assistant import analyze_meeting

st.set_page_config(page_title="AI Meeting Assistant", layout="wide")
st.title("🤖 Autonomous JIRA & Meeting Analysis Assistant")
st.markdown("---")

with st.sidebar:
    st.header("System Status")
    st.info("Agent Model: Llama 3 (Ollama)")
    st.info("Embedding: Nomic-Embed-Text")
    st.success("RAG System: Active")
    st.info("Audio Model: Whisper (Small)")

uploaded_file = st.file_uploader(
    "Upload meeting transcript (.txt) or audio recording (.mp3, .wav)",
    type=["txt", "mp3", "wav"],
)

if uploaded_file is not None:
    file_name = uploaded_file.name
    extension = (file_name.rsplit(".", 1)[-1].lower()) if "." in file_name else ""

    if st.session_state.get("uploaded_file_name") != file_name:
        st.session_state["uploaded_file_name"] = file_name
        st.session_state.pop("transcript_text", None)

    if extension == "txt":
        text_content = uploaded_file.getvalue().decode("utf-8")
        st.text_area("Uploaded Text", text_content, height=150)
        analysis_content = text_content
    else:
        if "transcript_text" not in st.session_state:
            try:
                # Refactored import
                from transcription import transcribe_audio_only
            except ModuleNotFoundError:
                st.error("Whisper is not installed. Run `pip install openai-whisper`.")
                st.stop()
                
            diarization_active = st.checkbox("🎙️ Perform speaker diarization (who said what?)")    
            if st.button("🎤 Transcribe Audio (Whisper)"):
                with st.status("Transcribing audio...", expanded=True) as status:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    try:
                        if diarization_active:
                            # Refactored import
                            from transcription import transcribe_with_diarization
                            st.session_state["transcript_text"] = transcribe_with_diarization(tmp_path)
                        else:
                            st.session_state["transcript_text"] = transcribe_audio_only(tmp_path)
                       
                    except Exception as e:
                        st.error(f"Error: {e}")
                        st.stop()
                    finally:
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
                    status.update(label="Transcript ready.", state="complete", expanded=False)
                st.rerun()
            st.stop()
            
        analysis_content = st.session_state["transcript_text"]
        st.text_area("Whisper Transcript (Source)", analysis_content, height=150)

    if st.button("🧠 Run Autonomous Agents & Sync with JIRA"):
        with st.status("Autonomous agents are analyzing and communicating with JIRA...", expanded=True) as status:
            try:
                result = analyze_meeting(analysis_content)
                status.update(label="Process Completed!", state="complete", expanded=False)
                st.subheader("✅ JIRA Task Creation Output")
                # Using .raw for compatibility with CrewAI V2+
                st.markdown(result.raw) 
            except Exception as e:
                status.update(label="Agent Error", state="error", expanded=True)
                st.error(f"Error detail: {e}")