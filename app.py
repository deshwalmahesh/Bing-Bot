from helpers import *
import streamlit as st
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space

st.set_page_config(page_title="Free Bing Chat")


with st.sidebar:
    st.title('Free Unlimited GPT-4 Chats')
    st.markdown('''
    # About
    This app is directly powered by [Bing Chat](https://www.bing.com/search?q=Bing+AI&showconv=1&FORM=hpcodx) which uses GPT-4

    💡 <span style="color:green">No API key and No payment required!!!</span>
    ''', unsafe_allow_html=True)

    st.warning("""If there's aproblem with response, either increase the delay or click 'Force Reload Bing'. Reloading the app works too but new selenium browser will be created""", icon="ℹ️")


if 'past' not in st.session_state: # past stores User's questions
    st.session_state['past'] = ["Default Hi!!"]

if 'generated' not in st.session_state:
    st.session_state['generated'] = ["Ok! now get to the point. You're not even paying a dime"]

if "tone" not in st.session_state:
    st.session_state["tone"] = "precise"

if "delay" not in st.session_state:
    st.session_state["delay"] = 30

if "agent" not in st.session_state:
    st.session_state["agent"] = BingGPT4("../bing", tone = st.session_state["tone"], wait_time = st.session_state["delay"])

if "msg_count" not in st.session_state:
    st.session_state["msg_count"] = 5

if "input" not in st.session_state:
    st.session_state["input"] = ""


st.warning(f"""After {str(st.session_state["msg_count"])} messages, chat bot won't have any context of our current conversation""",icon = "🚨")

col1, col2 = st.columns(2)
with col1:
    tone = st.radio("Model Tone", ['Precise', 'Balanced', 'Creative'], help = "One of the 3 tones provided by Bing. Visit Bing website for more detail")
    if tone != st.session_state["tone"]:
        if st.session_state["msg_count"] != 5:
            st.exception(ValueError("Can't change model in between conversation. 'Force Reload Bing' and then choose"))
        else:
            st.session_state["agent"]._change_tone(st.session_state["tone"])
            st.session_state["tone"] = tone

with col2:
    delay = st.number_input("Expected delay (in seconds)", min_value=20, max_value=120, value = st.session_state["delay"], 
                   help = "Expected delay in seconds. Depends on Input Length, Output Length and Bandwidth")
    if delay != st.session_state["delay"]:
        st.session_state["agent"].wait_time = int(st.session_state["delay"])
        st.session_state["delay"] = delay

with st.sidebar:
    if st.button("Force Reload Bing", help = "Reload the Bing Website if there is some error from the Bing side"):
        with st.spinner("Reloading Bing...."):
            st.session_state["agent"]._reload_bing_chat(st.session_state["tone"])
            st.session_state["msg_count"] = 5

add_vertical_space(2)
# Layout of input/response containers
input_container = st.container()
colored_header(label='', description='', color_name='blue-30')
response_container = st.container()


## Function for taking user provided prompt as input
def get_text():
    input_text = st.text_input("Enter you message here: ", "")
    if input_text == st.session_state["input"]: input_text = ''
    else: st.session_state["input"] = input_text
    if input_text:
        st.session_state["msg_count"] -= 1 # Model has a history storing only 
        if not st.session_state["msg_count"]: st.session_state["msg_count"] = 5

    return input_text

## Applying the user input box
with input_container:
    user_input = get_text()
    
## Conditional display of AI generated responses as a function of user provided prompts
with response_container:
    if user_input:

        with st.spinner(f"""Hold on!! Getting response in {st.session_state["delay"]} seconds"""):
            response, response_html, links = st.session_state["agent"].chat(user_input, stream = True)
            print("Merging response and response links into one longer textstring.")
            response = response + "\n\n" + links
        st.session_state.past.append(user_input)
        st.session_state.generated.append(response)
        
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')