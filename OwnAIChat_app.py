import streamlit as st
from OwnAIChat import OwnAIChat
from langchain.agents import AgentExecutor
import speech_text
import shutil
import tempfile
import os

st.title("Welcome to Own GenAI Chat🔥")
QUESTION_HISTORY: str = 'question_history'
USER_QUESTION: str = 'user_question'
list_of_files_uploaded = []
reload_required = False
is_speech_question = False


@st.cache_resource()
def prepare_agent() -> AgentExecutor:
    return OwnAIChat().set_up_agent()


def submit():
    st.session_state[USER_QUESTION] = st.session_state.query
    st.session_state.query = ''


# Disable the speech button after it is clicked
def disable():
    st.session_state.disabled = True


if 'speak_button' in st.session_state and st.session_state.speak_button:
    st.session_state.running = True
else:
    st.session_state.running = True

# Initialize disabled for form_submit_button to False
if "disabled" not in st.session_state:
    st.session_state.disabled = False


def intro_text():
    with st.sidebar.expander("Click to see application info:"):
        st.write(f"""Ask questions about:
- Personal content, will search in the uploaded documents
- Search engine content ([DuckDuckGo](https://duckduckgo.com/))
- [Wikipedia](https://www.wikipedia.org/) Content
- Mathematical calculations
- ***Please note: its still work n progress***
- Its secured, all uploaded docs would be deleted after closing.
- Speak your question ***Its disabled, client mic access issue on streamlit web***
- ***known issues:***
     After disabling speak button, unable to enable until text entered in question box
            currently , a refresh of screen is must to enable button, which has
            performance issues. so, no refresh performed programmatically.
    """)


intro_text()


def process_uploaded_files(uploaded_files):
    for file in uploaded_files:
        if file is not None:
            with tempfile.NamedTemporaryFile(dir="data/", delete=False) as f:
                f.write(file.getbuffer())
                temp = f.name
                destination = "data/" + file.name
                shutil.copyfile(temp, destination)
                f.close()
                os.unlink(f.name)
                list_of_files_uploaded.append(file.name)
    print("files uploaded\n")


with st.sidebar.form("my-form", clear_on_submit=True):
    files = st.file_uploader("For personal content, upload related Docs", type=["pdf", "txt"],
                             accept_multiple_files=True)
    submitted = st.form_submit_button("upload")

if submitted and files is not None:
    process_uploaded_files(files)
    reload_required = True
    st.sidebar.write("Uploaded files: ", list_of_files_uploaded)


def init_stream_lit():
    global reload_required
    print("init_stream_lit entered and reload_required: ", reload_required)
    if reload_required:
        st.cache_resource.clear()
        reload_required = False
    agent_executor: AgentExecutor = prepare_agent()
    if QUESTION_HISTORY not in st.session_state:
        st.session_state[QUESTION_HISTORY] = []

    simple_chat_tab, historical_tab = st.tabs([":blue[***AI Chat***]", ":black[***Session Chat History***]"])
    with simple_chat_tab:
        print("Entered : simple_chat_tab")
        st.text_input(":red[Your question ❓]", key='query', on_change=submit)
        user_question = ''
        global is_speech_question

        if USER_QUESTION in st.session_state:
            user_question = st.session_state[USER_QUESTION]

        speak_btn = st.button('💬:blue[***Click here to say your question***] 🎤',
                              disabled=st.session_state.running, key='speak_button')
        if speak_btn:
            # st.session_state.disabled = False
            # st.experimental_rerun()
            user_question = speech_text.get_audio_to_text()
            is_speech_question = True

        if user_question:
            with st.spinner('Please wait ...'):
                try:

                    st.write(f":red[Q: {user_question}]")
                    response = agent_executor.run(user_question)

                    if is_speech_question:
                        speech_text.output_text_to_speak(response)
                        is_speech_question = False

                    st.write("🔥 :green[Own-AI : ]" f":green[{response}]")
                    st.session_state[QUESTION_HISTORY].append((user_question, response))

                except Exception as e:
                    st.error(f"Error occurred: {e}")

    with historical_tab:
        print("Entered : historical_tab")
        for q in st.session_state[QUESTION_HISTORY]:
            question = q[0]
            if len(question) > 0:
                st.write(f":red[Q: {question}]")
                st.write(f":green[A: {q[1]}]")


if __name__ == "__main__":
    print("main entered")
    init_stream_lit()
