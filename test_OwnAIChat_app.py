import streamlit as st
from OwnAIChat import OwnAIChat
from langchain.agents import AgentExecutor
import speech_text
import shutil
import tempfile
import os
from audiorecorder import audiorecorder
from urllib.parse import urlparse

st.set_page_config("Voice based GenAI chat -Latest events and own data")
st.subheader('''
**Search latest events and own uploaded data by asking question through (text/voice)**
****Your data is secured[option to delete uploaded data]**** ''')

st.title("Own GenAI Chat🔥")

QUESTION_HISTORY: str = 'question_history'
USER_QUESTION: str = 'user_question'
AUDIO_INPUT: audiorecorder = ""
AUDIO_EVENT_TRIGGERED: bool = True

list_of_files_uploaded = []
reload_required = False
is_speech_question = False

if QUESTION_HISTORY not in st.session_state:
    st.session_state[QUESTION_HISTORY] = []

if USER_QUESTION not in st.session_state:
    st.session_state[USER_QUESTION] = ""

if AUDIO_INPUT not in st.session_state:
    st.session_state[AUDIO_INPUT] = ""

if AUDIO_EVENT_TRIGGERED not in st.session_state:
    st.session_state[AUDIO_EVENT_TRIGGERED] = True


@st.cache_resource()
def prepare_agent() -> AgentExecutor:
    return OwnAIChat().set_up_agent()


def submit():
    st.session_state[USER_QUESTION] = st.session_state.query
    st.session_state.query = ''
    st.session_state[AUDIO_EVENT_TRIGGERED] = False


def intro_text():
    with st.sidebar.expander("Click to see application info:"):
        st.write(f""" contact: syam.genaisolutions@gmail.com
- ***Ask questions about:***
- Personal content, will search in the uploaded documents
- Latest events
- Wikipedia Content
- Mathematical calculations
- Its secured, option to delete all uploaded docs.
- Voice based search enabled and response could be played through audio.
- ***Please note: its still work in progress***
    """)


intro_text()


def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except:
        return False


with st.sidebar.form("my-url-upload-form", clear_on_submit=True):
    st.text_area("Enter comma separated URLs")
    submit_urls = st.form_submit_button("upload URLs")
    if submit_urls:
        st.write(submit_urls)
        st.session_state[AUDIO_EVENT_TRIGGERED] = False


#   input_url = st.sidebar.text_input("Enter comma separated URLs")
#  submit_urls = st.form_submit_button("upload URLs")
# if submit_urls and input_url is not None:
#   st.sidebar.write("urls uploaded: ")
# process_urls(input_url)
# reload_required = True
# st.sidebar.write("Uploaded files: ", list_of_files_uploaded)

# input_url = st.sidebar.text_input("Enter a valid URL")
# if input_url:
#   urlStatusPlaceHolder = st.sidebar.empty()

#  import requests

# try:
#    r = requests.get(input_url)
#   urlStatusPlaceHolder.write("Proper Url")
# except:
#   urlStatusPlaceHolder.write("wrong URL")

# urlStatusPlaceHolder.write(r.content)
# if uri_validator(input_url):
# urlStatusPlaceHolder.write("Proper Url")
# if os.path.isfile("author_data/url_data"):
# reload_required = True

# else:
# urlStatusPlaceHolder.write("wrong URL")


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


with st.sidebar.form("my-upload-form", clear_on_submit=True):
    uploaded_files = st.file_uploader("For personal content, upload related Docs", type=["pdf", "txt"],
                                      accept_multiple_files=True)
    submit_uploaded_files = st.form_submit_button("upload")

if submit_uploaded_files and uploaded_files is not None:
    st.session_state[AUDIO_EVENT_TRIGGERED] = False
    process_uploaded_files(uploaded_files)
    if list_of_files_uploaded:
        reload_required = True
        st.sidebar.write("Uploaded files: ", list_of_files_uploaded)

with st.sidebar.form("my-delete-file-form", clear_on_submit=True):
    files_to_delete = os.listdir("data/")
    submit_delete_data = st.form_submit_button("Delete uploaded data")

if submit_delete_data and files_to_delete is not None:
    st.session_state[AUDIO_EVENT_TRIGGERED] = False
    for file in files_to_delete:
        if file != "author_data.txt":
            file_path = os.path.join("data/", file)
            if os.path.isfile(file_path):
                os.remove(file_path)


# prompt = st.chat_input("Say something")
# if prompt:
#    st.write(f"User: {prompt}")
#   with st.chat_message("user"):
#      st.write("Hello 👋")


def init_stream_lit():
    global reload_required

    print("init_stream_lit entered and reload_required: ", reload_required)
    if reload_required:
        st.cache_resource.clear()
        reload_required = False

    agent_executor: AgentExecutor = prepare_agent()

    simple_chat_tab, historical_tab = st.tabs([":blue[***AI Chat***]", ":black[***Session Chat History***]"])
    with simple_chat_tab:
        # print("Entered : simple_chat_tab")
        st.text_input(":red[Your question ❓]", key='query', on_change=submit)

        print("st.session_state[USER_QUESTION] after text: ", st.session_state[USER_QUESTION])
        print("st.session_state[AUDIO_EVENT_TRIGGERED] : ", st.session_state[AUDIO_EVENT_TRIGGERED])

        st.session_state[AUDIO_INPUT] = audiorecorder("🎙️ speak", "🎙️ stop")
        if not st.session_state[AUDIO_EVENT_TRIGGERED]:
            st.session_state[AUDIO_INPUT] = ""
        st.session_state[AUDIO_EVENT_TRIGGERED] = True

        if len(st.session_state[AUDIO_INPUT]) and not st.session_state[USER_QUESTION]:
            st.session_state[USER_QUESTION] = speech_text.audio_to_text_Convertion(
                st.session_state[AUDIO_INPUT].export("audio.wav", format="wav"))
            if os.path.isfile("audio.wav"):
                os.remove("audio.wav")
        # if st.session_state[USER_QUESTION]== "Could not understand your audio, PLease try again !":

        st.session_state[AUDIO_INPUT] = ""
        print("st.session_state[USER_QUESTION] after audio: ", st.session_state[USER_QUESTION])

        if st.session_state[USER_QUESTION]:
            with st.spinner('Please wait ...'):
                try:
                    question_placeholder = st.empty()
                    player_placeholder = st.empty()
                    reponse_placeholder = st.empty()
                    if st.session_state[USER_QUESTION] == "Could not understand your audio, PLease try again !":
                        reponse_placeholder.write("🔥 :green[Own-AI : ]" f":green[st.session_state[USER_QUESTION]]")
                    else:
                        question_placeholder.write(f":red[Q: {st.session_state[USER_QUESTION] }]")
                        response = agent_executor.run(st.session_state[USER_QUESTION])
                        reponse_placeholder.write("🔥 :green[Own-AI : ]" f":green[{response}]")

                    audioout_file = speech_text.output_text_to_speak(response)
                    player_placeholder.audio(audioout_file)
                    os.remove(audioout_file)

                    st.session_state[QUESTION_HISTORY].append((st.session_state[USER_QUESTION], response))
                    st.session_state[USER_QUESTION] = ""
                    print("st.session_state[USER_QUESTION] after append: ", st.session_state[USER_QUESTION])

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
