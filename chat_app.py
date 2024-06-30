import streamlit as st
from openai import OpenAI
from mycomponent import mycomponent
import time

# Set page config
st.set_page_config(page_title="Zepi",
                   layout='wide')


# Initialise the OpenAI client, and retrieve the assistant
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
assistant = client.beta.assistants.retrieve(st.secrets["ASSISTANT_ID"])

# Apply custom CSS
st.html("""
        <style>
            #MainMenu {visibility: hidden}
            #header {visibility: hidden}
            #footer {visibility: hidden}
            .block-container {
                padding-top: 3rem;
                padding-bottom: 2rem;
                padding-left: 3rem;
                padding-right: 3rem;
                }
        </style>
        """)

def stream_data(textdata):
    for word in textdata.split(" "):
        yield word + " "
        time.sleep(0.05)

def payment_message():
    st.session_state.messages.append({"role": "assistant",
                                      "items": [{"type": "spinner"}],
                                      "first": True})
    st.session_state.messages.append({"role": "assistant",
                                      "items": [
                                          {"type": "success",
                                           "content": "Thank you! Your order has been received."},
                                      ],
                                      "first": True})
    st.session_state.messages.append({"role": "assistant",
                                      "items": [
                                          {"type": "text",
                                           "content": "Order number: **973738**"},
                                          {"type": "text",
                                           "content": "We've also sent a confirmation to your email."},
                                          {"type": "text",
                                           "content": "You can come back here anytime to check your delivery status."}
                                      ],
                                      "first": True})

if "aaa" not in st.session_state:
    st.session_state.aaa = False

if "user_name" not in st.session_state:
    st.session_state.user_name = "User"


if "prompt_message" not in st.session_state:
    st.session_state.prompt_message = ""

if "will_sleep" not in st.session_state:
    st.session_state.will_sleep = 0

if "inactivity_state" not in st.session_state:
    st.session_state.inactivity_state = "active"


b1,b2 = st.columns(2)
with b1:
    if st.button("flow1"):
        st.switch_page("chat_app.py")
with b2:
    if st.button("flow2"):
        st.switch_page("pages/flow2.py")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant",
                                  "items": [
                                      {"type": "text",
                                       "content": "Nice pick! 🤩"}],
                                  "first": True},
                                 {"role": "assistant",
                                  "items": [
                                      {"type": "text",
                                       "content": "Add $38 to your order and get **FREE SHIPPING!**"}],
                                  "first": True},
                                 {"role": "assistant",
                                  "items": [{"type": "buttons"}],
                                  "first": True}]


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        for item in message["items"]:
            item_type = item["type"]
            if item_type == "text":
                if message["first"] == False:
                    st.markdown(item["content"])
                else:
                    st.write_stream(stream_data(item["content"]))
            elif item_type == "image":
                for image in item["content"]:
                    st.html(image)
            elif item_type == "code_input":
                with st.status("Code", state="complete"):
                    st.code(item["content"])
            elif item_type == "code_output":
                with st.status("Results", state="complete"):
                    st.code(item["content"])
            elif item_type == "buttons":
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Add Items", disabled=not message["first"]):
                        st.markdown("Not Supported")
                        message["first"] = False
                with col2:
                    if st.button("Checkout", disabled=not message["first"]):
                        st.session_state.prompt_message = "John Dow"
                        st.session_state.will_sleep = 10
                        st.session_state.inactivity_state = "name"
                        message["first"] = False
                        st.session_state.messages.append({"role": "assistant",
                                                          "items": [
                                                              {"type": "text",
                                                               "content": "Let's complete a few details so I can calculate your order's total"},
                                                              {"type": "text", "content": "what is your name?"}],
                                                          "first": True})
            elif item_type == "pay":
                col1, col2, col3 = st.columns(3)
                isDisabled = not message["first"]
                with col1:
                    if st.button("gpay", disabled=isDisabled):
                        payment_message()
                        message["first"] = False

                with col2:
                    if st.button("apple", disabled=isDisabled ):
                        payment_message()
                        message["first"] = False
                with col3:
                    if st.button("credit", disabled=isDisabled ):
                        payment_message()
                        message["first"] = False
            elif item_type == "success":
                st.success(item["content"])
            elif item_type == "spinner" and message["first"] is True:
                with st.spinner('Processing payment'):
                    time.sleep(3)
                message["first"] = False
        message["first"] = False

if st.session_state.prompt_message == "Your shipping address:":
    st.session_state.prompt_message = ""
    st.session_state.aaa = True
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.session_state.user_address = mycomponent()

elif prompt:= st.chat_input(st.session_state.prompt_message):
    st.session_state.messages.append({"role": "user",
                                        "items": [
                                            {"type": "text",
                                            "content": prompt
                                            }],
                                      "first": False})

    # client.beta.threads.messages.create(
        #     thread_id=st.session_state.thread_id,
        #     role="user",
        #     content=prompt
        # )

    with st.chat_message("user"):
        st.markdown(prompt)
    if st.session_state.prompt_message == "John Dow":
        st.session_state.prompt_message = "Your shipping address:"
        st.session_state.inactivity_state = "active"
        st.session_state.user_name = prompt
        m = "Hi " + st.session_state.user_name +", what is the shipping address for this order?"
        st.session_state.messages.append({"role": "assistant",
                                              "items": [
                                                  {"type": "text",
                                                   "content": m
                                                   }],
                                         "first": True})
        st.rerun()
elif st.session_state.aaa == True:

    st.session_state.user_address = mycomponent()
    st.session_state.messages.append({"role": "user",
                                      "items": [
                                          {"type": "text",
                                           "content": st.session_state.user_address
                                           }],
                                      "first": False}
                                     )
    st.session_state.messages.append({"role": "assistant",
                                      "items":[
                                          {"type": "text",
                                           "content": "Your order total is $112. How would you like to pay?"}
                                      ],
                                      "first": True})
    st.session_state.messages.append({"role": "assistant",
                                      "items": [{"type": "pay"}],
                                      "first": True})
    st.session_state.aaa = False
    st.rerun()


if st.session_state.inactivity_state != "active":
    time.sleep(st.session_state.will_sleep)

if st.session_state.inactivity_state == "name":
    st.session_state.messages.append({"role": "assistant",
                                       "items": [
                                           {"type": "text",
                                            "content": "Are you still there? Just a few more details so I can calculate your order total. What’s your name?"}],
                                       "first": True})
    st.session_state.inactivity_state = "active"
    st.session_state.will_sleep = 0
    st.rerun()
