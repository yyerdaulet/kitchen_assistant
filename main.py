import streamlit as st
from ai_agent import app
from langchain_core.messages.tool import ToolMessage
from langchain.schema import AIMessage

st.title("Kitchen assistant")

if "messages" not in st.session_state:
    st.session_state["messages"]= []

def add_message(role,message):
    st.session_state["messages"].append({"role":role,"message":message})

def agent_response(user_message):
    input = {"messages":[("user",f"{user_message}")]}
    res = app.invoke(input)
    answer = ""
    for message in res["messages"]:
        if isinstance(message,ToolMessage):
            answer = message.content
        elif isinstance(message,AIMessage):
            answer = message.content
    return answer

user_input = st.text_input("Enter your message")


if st.button("Submit") and user_input:
    add_message("user",user_input)
    response = agent_response(user_input)
    add_message("response",response)

for chat in st.session_state["messages"]:
    if chat["role"] == "user":
        st.markdown(f"**You:** {chat['message']}")
    else:
        st.markdown(f"**Bot:** {chat['message']}")




