import streamlit as st
import json
from openai import OpenAI
import time



from openai.types.beta.assistant_stream_event import (
    ThreadMessageCreated,
    ThreadMessageDelta,
    ThreadRunRequiresAction
    )
from openai.types.beta.threads.text_delta_block import TextDeltaBlock 

# Set page config
st.set_page_config(page_title="Zepi",
                   layout='wide')

# Get secrets
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
    st.session_state.messages2.append({"role": "assistant",
                                      "items": [{"type": "spinner", "content": "processing payment"}],
                                      "first": True})
    st.session_state.messages2.append({"role": "assistant",
                                      "items": [
                                          {"type": "success",
                                           "content": "Thank you! Your order has been received."},
                                      ],
                                      "first": True})
    st.session_state.messages2.append({"role": "assistant",
                                      "items": [
                                          {"type": "text",
                                           "content": "Order number: **973738**"},
                                          {"type": "text",
                                           "content": "We've also sent a confirmation to your email."},
                                          {"type": "text",
                                           "content": "You can come back here anytime to check your delivery status."}
                                      ],
                                      "first": True})

# Create a new thread
if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id
    print(st.session_state.thread_id)

st.session_state.prompt_message = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = "default user"

if "user_address" not in st.session_state:
    st.session_state.user_address = "default address"

if "inactivity_state" not in st.session_state:
    st.session_state.inactivity_state = "active"

if "inactivity_timer" not in st.session_state:
    st.session_state.inactivity_timer = 10

# UI

if "messages2" not in st.session_state:
    st.session_state.messages2 = [{"role": "assistant",
                                      "items": [
                                          {"type": "text",
                                           "content": "Nice pick " + st.session_state.user_name + "🤩"}],
                                            "first": True},
                                 {"role": "assistant",
                                  "items": [
                                      {"type": "text",
                                       "content": "Get the 2nd item 50% off and FREE SHIPPING (on orders above $150)"}],
                                        "first": True},
                                 {"role": "assistant",
                                  "items": [{"type": "buttons"}],
                                  "first": True}]


# UI

b1,b2,b3 = st.columns(3)
with b1:
    if st.button("flow1"):
        st.switch_page("chat_app.py")
with b2:
    if st.button("flow2"):
        st.switch_page("pages/flow2.py")
with b3:
    if st.button("flow3"):
        st.switch_page("pages/flow3.py")

for message in st.session_state.messages2:
    with st.chat_message(message["role"]):
        for item in message["items"]:
            item_type = item["type"]
            if item_type == "text":
                if message["first"] == False:
                    st.markdown(item["content"])
                else:
                    st.write_stream(stream_data(item["content"]))
                    message["first"] = False
            elif item_type == "image":
                for image in item["content"]:
                    st.html(image)
            elif item_type == "buttons":
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Add Items", disabled=not message["first"]):
                        st.markdown("Not Supported")
                        message["first"] = False
                with col2:
                    if st.button("Checkout", disabled=not message["first"]):
                        st.session_state.inactivity_state = "confirm"
                        st.session_state.inactivity_timer = 10
                        message["first"] = False
                        st.session_state.messages2.append({"role": "assistant",
                                                          "items": [
                                                              {"type": "text",
                                                               "content": "Is this your shipping address?"},
                                                              {"type": "text", "content": st.session_state.user_address}],
                                                          "first": True})
                        st.session_state.messages2.append({"role": "assistant",
                                                          "items": [{"type": "confirm"}],
                                                          "first": True})

            elif item_type == "confirm":
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Confirm", disabled=not message["first"]):
                        message["first"] = False
                        st.session_state.inactivity_timer = 12
                        st.session_state.inactivity_state = "pay"
                        st.session_state.messages2.append({"role": "assistant",
                                                          "items": [
                                                              {"type": "text",
                                                               "content": "Your order total is $112. How would you like to pay?"}],
                                                          "first": True})
                        st.session_state.messages2.append({"role": "assistant",
                                                          "items": [{"type": "pay"}],
                                                          "first": True})
                with col2:
                    if st.button("Change Shipping Address", disabled=not message["first"]):
                        st.markdown("not supported")
                        message["first"] = False
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
                with st.spinner(item["content"]):
                    time.sleep(3)
                message["first"] = False


if prompt := st.chat_input(st.session_state.prompt_message):

    st.session_state.messages2.append({"role": "user",
                                        "items": [
                                            {"type": "text",
                                            "content": prompt
                                            }],
                                      "first": False})

    client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

    with st.chat_message("user"):
        st.markdown(prompt)

    if prompt == "no" and st.session_state.inactivity_state == "pay":
        st.session_state.messages2.remove({"role": "assistant","items": [{"type": "pay"}],"first": True})
        st.session_state.messages2.append({"role": "assistant",
                                           "items": [
                                               {"type": "text",
                                                "content": "How would you like to pay (your order total is $112)?"}],
                                           "first": True})
        st.session_state.messages2.append({"role": "assistant",
                                           "items": [{"type": "pay"}],
                                           "first": True})
        st.rerun()
    elif prompt == "yes" and st.session_state.inactivity_state == "cupon":
        st.session_state.messages2.remove({"role": "assistant", "items": [{"type": "pay"}], "first": True})
        st.session_state.messages2.append({"role": "assistant",
                                           "items": [
                                               {"type": "text",
                                                "content": "Great. Your coupon is redeemed. The order total is now $106.4 ($112). How would you like to pay?"}],
                                           "first": True})
        st.session_state.messages2.append({"role": "assistant",
                                           "items": [{"type": "pay"}],
                                           "first": True})
        st.rerun()
    else:
        with (st.chat_message("assistant")):
            stream = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=st.secrets["ASSISTANT_ID"],
                #tool_choice={"type": "file_search"},
                stream=True
            )
            assistant_output = []
            tool_outputs = []
            assistant_first = False
            for event in stream:
                if isinstance(event, ThreadMessageCreated):
                    assistant_output.append({"type": "text",
                                            "content": ""})
                    assistant_text_box = st.empty()

                elif isinstance(event, ThreadMessageDelta):
                    if isinstance(event.data.delta.content[0], TextDeltaBlock):
                        assistant_text_box.empty()
                        assistant_output[-1]["content"] += event.data.delta.content[0].text.value
                        assistant_text_box.markdown(assistant_output[-1]["content"])
                elif isinstance(event, ThreadRunRequiresAction):
                    for tool_call in event.data.required_action.submit_tool_outputs.tool_calls:
                        tool_call_id = tool_call.id
                        if tool_call.function.name == "too_expensive":
                            assistant_text_box = st.empty()
                            assistant_output.append({"type": "text",
                                                     "content": "Okay. Let me see what I can do about it…"}),
                            assistant_output.append({"type": "text",
                                                     "content": "Please hold on"}
                                                    )
                            assistant_first = True
                        # arguments = json.loads(tool_call.function.arguments)
                        # response = arguments  # arguments is the response
                        # tool_outputs.append({
                        #     "tool_call_id": tool_call_id,
                        #     "outputs": {"response": response}
                        # })
                    client.beta.threads.runs.submit_tool_outputs(thread_id=st.session_state.thread_id,
                                                                 run_id=event.data.id,
                                                                 tool_outputs=[
                                                                     {
                                                                         "tool_call_id": tool_call_id,
                                                                         "output": "bla"
                                                                     }])
            st.session_state.messages2.append({"role": "assistant", "items": assistant_output, "first": assistant_first})
            if assistant_first:
                st.session_state.messages2.append({"role": "assistant",
                                                   "items": [{"type": "spinner", "content": "checking discount option"}],
                                                   "first": True})
                st.session_state.messages2.append({"role": "assistant",
                                                   "items": [
                                                       {"type": "text",
                                                        "content": "I just got approval to give you an additional 5% discount on your order. "
                                                                   "This is a one-time coupon which is applicable for this order only. "},
                                                       {"type": "text",
                                                        "content": "Would you like to redeem it now?"},
                                                   ],
                                                   "first": True})
                st.session_state.inactivity_state = "cupon"
                st.rerun()

            st.session_state.inactivity_state = "chat"
            st.session_state.inactivity_timer = 5

if st.session_state.inactivity_state != "active":
    time.sleep(st.session_state.inactivity_timer)

if st.session_state.inactivity_state == "chat":
    st.session_state.inactivity_timer = 10
    st.session_state.inactivity_state = "pay"
    st.session_state.messages2.append({"role": "assistant",
                                       "items": [
                                           {"type": "text",
                                            "content": "Is there anything else I can help you with?"}],
                                       "first": True})
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="assistant",
        content="Is there anything else I can help you with?"
    )

    st.rerun()
elif st.session_state.inactivity_state == "pay":
    print(st.session_state.inactivity_timer)
    st.session_state.inactivity_state = "pay2"
    st.session_state.inactivity_timer = 8
    st.session_state.messages2.append({"role": "assistant",
                                       "items": [
                                           {"type": "text",
                                            "content": "Is there anything I can do to assist you in making your purchase decision?"}],
                                       "first": True})
    st.rerun()
elif st.session_state.inactivity_state == "pay2":
    st.session_state.inactivity_state = "give_up"
    st.session_state.messages2.append({"role": "assistant",
                                       "items": [
                                           {"type": "text",
                                            "content": "May I ask what’s keeping you from completing the order?"}],
                                       "first": True})
    st.rerun()
elif st.session_state.inactivity_state == "confirm":
    st.session_state.inactivity_state = "active"
    st.session_state.messages2.append({"role": "assistant",
                                       "items": [
                                           {"type": "text",
                                            "content": "Please confirm your shipping address so I can calculate your order total"}],
                                       "first": True})
    st.rerun()
