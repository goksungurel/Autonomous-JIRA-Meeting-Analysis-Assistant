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
from meeting_assistant import create_jira_tasks, draft_jira_tasks


def _parse_action_items(raw_text: str):
    lines = [line.strip() for line in (raw_text or "").splitlines() if line.strip()]
    items = []
    for line in lines:
        normalized = line.lstrip("-*• ").strip()
        if normalized:
            items.append(normalized)
    return items


def _action_items_to_markdown(items):
    valid_items = [item.strip() for item in items if item and item.strip()]
    return "\n".join(f"- {item}" for item in valid_items)

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

human_input = st.text_area(
    "Human Input (optional guidance for agents)",
    placeholder="Example: Prioritize backend tasks and skip non-technical notes.",
    height=100,
)

if uploaded_file is not None:
    file_name = uploaded_file.name
    extension = (file_name.rsplit(".", 1)[-1].lower()) if "." in file_name else ""

    if st.session_state.get("uploaded_file_name") != file_name:
        st.session_state["uploaded_file_name"] = file_name
        st.session_state.pop("transcript_text", None)
        st.session_state.pop("drafted_action_items", None)
        st.session_state.pop("jira_creation_output", None)

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

    if st.button("🧠 Generate Task Suggestions"):
        with st.status("Agents are analyzing the meeting and preparing draft tasks...", expanded=True) as status:
            try:
                draft_result = draft_jira_tasks(analysis_content, human_input=human_input)
                drafted_text = getattr(draft_result, "raw", str(draft_result))
                st.session_state["drafted_action_items"] = drafted_text
                st.session_state["editable_action_items"] = _parse_action_items(drafted_text)
                st.session_state["new_action_item_input"] = ""
                st.session_state.pop("jira_creation_output", None)
                status.update(label="Draft task list is ready.", state="complete", expanded=False)
            except Exception as e:
                status.update(label="Agent Error", state="error", expanded=True)
                st.error(f"Error detail: {e}")

    drafted_action_items = st.session_state.get("drafted_action_items")
    if drafted_action_items:
        st.subheader("📝 Proposed Tasks (Awaiting Human Approval)")
        st.caption("You can edit, delete, or add tasks before JIRA creation.")

        editable_items = st.session_state.get("editable_action_items", [])
        if not editable_items:
            st.info("No parsed action items found. Add one below to continue.")

        delete_index = None
        for idx, item in enumerate(editable_items):
            col_text, col_delete = st.columns([0.9, 0.1])
            with col_text:
                updated_value = st.text_input(
                    f"Task {idx + 1}",
                    value=item,
                    key=f"task_input_{idx}",
                    label_visibility="collapsed",
                    placeholder=f"Task {idx + 1}",
                )
                editable_items[idx] = updated_value
            with col_delete:
                if st.button("🗑️", key=f"delete_task_{idx}", help=f"Delete task {idx + 1}"):
                    delete_index = idx

        if delete_index is not None:
            editable_items.pop(delete_index)
            st.session_state["editable_action_items"] = editable_items
            st.rerun()

        st.markdown("**Add New Action Item**")
        st.text_input(
            "New action item",
            key="new_action_item_input",
            placeholder="Write a new action item...",
            label_visibility="collapsed",
        )
        if st.button("➕ Add Item"):
            new_item = st.session_state.get("new_action_item_input", "").strip()
            if new_item:
                editable_items.append(new_item)
                st.session_state["editable_action_items"] = editable_items
                st.session_state["new_action_item_input"] = ""
                st.rerun()
            else:
                st.warning("New action item cannot be empty.")

        preview_markdown = _action_items_to_markdown(editable_items)
        st.markdown("**Final Preview**")
        st.markdown(preview_markdown if preview_markdown else "_No approved items yet._")
        st.warning("JIRA tasks will NOT be created until you approve.")

        if st.button("✅ Approve & Create Tasks on JIRA"):
            if not preview_markdown:
                st.error("Please keep at least one action item before approval.")
                st.stop()
            with st.status("Creating approved tasks on JIRA...", expanded=True) as status:
                try:
                    jira_result = create_jira_tasks(preview_markdown, human_input=human_input)
                    st.session_state["jira_creation_output"] = getattr(jira_result, "raw", str(jira_result))
                    status.update(label="Approved tasks were created.", state="complete", expanded=False)
                except Exception as e:
                    status.update(label="JIRA Creation Error", state="error", expanded=True)
                    st.error(f"Error detail: {e}")

        if st.button("❌ Reject Draft Tasks"):
            st.session_state.pop("drafted_action_items", None)
            st.session_state.pop("editable_action_items", None)
            st.session_state.pop("new_action_item_input", None)
            st.session_state.pop("jira_creation_output", None)
            st.rerun()

    jira_creation_output = st.session_state.get("jira_creation_output")
    if jira_creation_output:
        st.subheader("✅ JIRA Task Creation Output")
        st.markdown(jira_creation_output)