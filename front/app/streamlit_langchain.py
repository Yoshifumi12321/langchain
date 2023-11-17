import streamlit as st
import streamlit.components.v1 as stc

if "generated" not in st.session_state:
    st.session_state.generated = []
if "past" not in st.session_state:
    st.session_state.past = []

st.title("LangChain検証")

import os

import json
import requests

import tempfile
from pathlib import Path
import base64

# END_POINT = "http://54.248.123.248:8080"
END_POINT = "http://localhost:8000"


# 参考：https://shunyaueta.com/posts/2021-07-08/
def show_pdf(file_path:str):
    """Show the PDF in Streamlit
        That returns as html component

        Parameters
        ----------
        file_path : [str]
            Uploaded PDF file path
    """
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="1000" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)

st.markdown('### PDFの内容を回答してくれるアプリ')
st.markdown('#### 読み込みたいPDFをアップロード')
file = st.file_uploader('画像をアップロードしてください.', type=['pdf'])
if file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        # st.markdown("## Original PDF file")
        pdftmpfile = f'{tmp_file.name}.pdf'
        fp = Path(pdftmpfile)
        fp.write_bytes(file.getvalue())
        response = requests.post(f'{END_POINT}/pdf', files={'file': open(pdftmpfile, 'rb')})
        
        st.markdown(f'{tmp_file.name} をアップロードしました.')

pdf_url = ""
pdf_url_reqistory = ""

st.markdown('#### AIに質問')
# if 'generated' not in st.session_state: 
st.chat_message("ai").write("こんにちは！AIアシスタントです🤖  <br>PDFを読み込むとその文書に記載されている内容から回答します。",unsafe_allow_html=True)
if 'chat_history' not in st.session_state: 
	st.session_state['chat_history'] = [] #chat_historyがsession_stateに追加されていない場合，[]で初期化

from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
msgs = StreamlitChatMessageHistory(key="chat_messages")
memory = ConversationBufferMemory(memory_key="history", chat_memory=msgs)

template = """You are an AI chatbot in Japan having a conversation with a human.

{history}
Human: {human_input}
AI: """

prompt = PromptTemplate(input_variables=["history", "human_input"], template=template)

for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

if prompt := st.chat_input():
    # message = st.chat_message("human").write(prompt)
    json_data = {
        "query" : prompt,
        "chat_history": st.session_state.chat_history
    }
    # As usual, new messages are added to StreamlitChatMessageHistory when the Chain is called.
    response = requests.post(f'{END_POINT}/chat', data = json.dumps(json_data) )
    st.session_state.chat_history.append(prompt)
    
    # 会話履歴をセッションで保持
    st.session_state.past.append(prompt)
    st.session_state.generated.append(response)

    for i in range(len(st.session_state['past'])):
        # st.markdown(st.session_state['past'])
        st.chat_message("human").write(st.session_state['past'][i], is_user=True, key=str(i) + "_user")
        response = st.session_state['generated'][i]
        
        if response is not None:
            json_data = response.json()
            with st.chat_message("ai"):
                st.write(json_data['answer'])
                st.write("source_documents:")
                st.json({"source_documents":json_data['source_documents']},expanded=True)

stc.html('<footer><div style="text-align: right;"> <p>created by josys lab ai-1 </p></div></footer>')

