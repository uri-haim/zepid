import streamlit as st
from openai import OpenAI
from mycomponent import mycomponent
from inactiveuser import inactiveuser
from replacebutton import replacebutton
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json
import time

# Set page config
st.set_page_config(page_title="Zepi",layout='wide')

# Initialise the OpenAI client, and retrieve the assistant
# client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
# assistant = client.beta.assistants.retrieve(st.secrets["ASSISTANT_ID"])

# Apply custom CSS
st.html("""
        <style>
                html {
                    font-size: 20px !important;
                }

                .block-container {
                    padding: 0px;
                }

                [data-testid="stBottomBlockContainer"] > div {
                    padding: 0px !important;
                }
                .stChatMessage {
                    padding: 0px;
                }
             


        </style>
        """)

def stream_data(textdata):
    for word in textdata.split(" "):
        yield word + " "
        time.sleep(0.08)

def remove_table_margins():
    components.html("""
        <script>
            const doc = window.parent.document;
            var wrapIframe = doc.querySelector('[title="st.iframe"]');
            wrapIframe.parentElement.style.height = '0px';
            wrapIframe.style.height = '0px';

            const styleSheet = doc.styleSheets[3];
            //console.log(doc.styleSheets);
            for (let i = 0; i < styleSheet.cssRules.length; i++) {

              const rule = styleSheet.cssRules[i];
              if (rule.media)
              {
                if (rule.cssText.substring(0,10) != "@media pri")
                {
                // console.log(rule.cssText);
                styleSheet.deleteRule(i);
                i--;
                }
              }



              // if (rule.cssText == "@media (max-width: 640px) {\\n  .st-emotion-cache-keje6w { min-width: calc(100% - 1.5rem); }\\n}") {
                // console.log(i);
                //console.log(rule);
                // styleSheet.deleteRule(i);
                //i--; // Adjust index after deletion
              //}
            }
        </script>
    """)


def payment_message():
    st.session_state.flow_state = "completed"
    ref.set("6")
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

if "inactive_counter" not in st.session_state:
    st.session_state.inactive_counter = 0

if "user_name" not in st.session_state:
    st.session_state.user_name = "User"

if "prompt_message" not in st.session_state:
    st.session_state.prompt_message = ""

if "inactivity_state" not in st.session_state:
    st.session_state.inactivity_state = "active"

if "mydb" not in firebase_admin._apps:
    with open('firebasecred.json', 'r') as file:
        jsoncred = json.load(file)
    jsoncred['private_key_id'] = st.secrets['private_key_id']
    jsoncred['private_key'] = st.secrets['private_key']
    cred = credentials.Certificate(jsoncred)
    # Initialize the app with a service account, granting admin privileges
    mydb = firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://zepi-83415-default-rtdb.firebaseio.com'},"mydb")
else:
    mydb = firebase_admin.get_app("mydb")
ref = db.reference('/state',mydb)

if "flow_state" not in st.session_state:
    ref.set("1")
    st.session_state.flow_state = "begin"

if "user_address" not in st.session_state:
    st.session_state.user_address = "init"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant",
                                  "items": [
                                      {"type": "image",
                                       "content": "firstpic.jpeg"}],
                                  "first": True},
                                 {"role": "assistant",
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
    if message["role"] == "assistant":
        avatar = "eva.png"
    else:
        avatar = None
    with st.chat_message(message["role"], avatar=avatar):
        for item in message["items"]:
            item_type = item["type"]
            if item_type == "text":
                if message["first"] == False:
                    st.markdown(item["content"])
                else:
                    st.write_stream(stream_data(item["content"]))
            elif item_type == "image":
                st.image(item["content"], width=100)
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
                        st.session_state.flow_state = "name"
                        ref.set("2")
                        message["first"] = False
                        st.session_state.messages.append({"role": "assistant",
                                                          "items": [
                                                              {"type": "text",
                                                               "content": "Let's complete a few details so I can calculate your order's total"},
                                                              {"type": "text", "content": "what is your name?"}],
                                                          "first": True})
            elif item_type == "pay":
                isDisabled = not message["first"]
                if st.button("paypal", disabled=isDisabled):
                    payment_message()
                    message["first"] = False
                if st.button("apple", disabled=isDisabled ):
                    payment_message()
                    message["first"] = False
                if st.button("credit", disabled=isDisabled ):
                    payment_message()
                    message["first"] = False
            elif item_type == "success":
                st.success(item["content"])
            elif item_type == "spinner" and message["first"] is True:
                with st.spinner('Processing payment'):
                    time.sleep(3)
                st.session_state.messages.remove({"role": "assistant",
                                      "items": [{"type": "spinner"}],
                                      "first": True})
                st.rerun()
        message["first"] = False
remove_table_margins()
a = replacebutton()

scroll_script = f"""
<script>
  var textArea = document.getElementById("root");
  textArea.scrollTop = textArea.scrollHeight;
</script>
"""
st.markdown(scroll_script, unsafe_allow_html=True)

if st.session_state.flow_state == "address":
    st.html("""
    <style>
            [data-testid="stBottom"] > div {
                display: none !important;
            }    
    </style>
    """)
    if st.session_state.user_address == "init":
        st.session_state.user_address = mycomponent(timeout=st.session_state.inactive_counter)
    elif st.session_state.user_address == None:
        st.session_state.user_address = mycomponent(timeout=st.session_state.inactive_counter)
        if st.session_state.user_address == "timeout":
            st.session_state.user_address = "init"
            st.session_state.inactive_counter += 1
            st.session_state.messages.append({"role": "assistant",
                                                      "items": [
                                                          {"type": "text",
                                                           "content": "Start typing your address and select from the list below"}
                                                      ],
                                                      "first": True})
        else:
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
            st.session_state.flow_state = "payment"
            ref.set("5")
        st.rerun()
if prompt := st.chat_input(st.session_state.prompt_message):
    if prompt == "2":
        st.switch_page("pages/flow2.py")
    st.session_state.messages.append({"role": "user",
                                        "items": [
                                            {"type": "text",
                                            "content": prompt
                                            }],
                                      "first": False})
    with st.chat_message("user"):
        st.markdown(prompt)
    if st.session_state.flow_state == "name":
        st.session_state.inactivity_state = "active"
        st.session_state.flow_state = "address"
        ref.set("4")
        st.session_state.user_name = prompt
        m = "Hi " + st.session_state.user_name +", what is the shipping address for this order?"
        st.session_state.messages.append({"role": "assistant",
                                              "items": [
                                                  {"type": "text",
                                                   "content": m
                                                   }],
                                         "first": True})
        st.session_state.prompt_message = ""
        st.rerun()


if st.session_state.flow_state == "name" and st.session_state.inactive_counter < 2:
    st.session_state.inactivity_state = inactiveuser(timeout=10000)
    ref.set("3")
    st.session_state.inactive_counter += 1
if st.session_state.inactivity_state == "timeout":
    st.session_state.inactive_counter += 1
    st.session_state.inactivity_state = "active"
    st.session_state.messages.append({"role": "assistant",
                                       "items": [
                                           {"type": "text",
                                            "content": "Are you still there? Just a few more details so I can calculate your order total. What’s your name?"}],
                                       "first": True})
    st.rerun()


