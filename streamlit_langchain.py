import streamlit as st
import streamlit.components.v1 as stc
from streamlit_chat import message

if "generated" not in st.session_state:
    st.session_state.generated = []
if "past" not in st.session_state:
    st.session_state.past = []

st.title("LangChain検証")

from langchain import OpenAI, ConversationChain
import openai
import os

import platform
import openai
import chromadb
import langchain
from langchain.llms import OpenAI

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import PyPDFLoader

import json
import requests

import tempfile
from pathlib import Path
import base64


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
        response = requests.post('http://127.0.0.1:8000/pdf', files={'file': open(pdftmpfile, 'rb')})
        
        st.markdown(f'{tmp_file.name} をアップロードしました.')

pdf_url = ""
chat_history = []
pdf_url_reqistory = ""

st.markdown('#### 対話')
with st.form("my_forms"):
    user_message = st.text_area("メッセージを送信してください")
    submitted = st.form_submit_button("送信する")

    if submitted:
        json_data = {
            "query" : user_message
        }
        st.markdown(json_data)
        
        response = requests.post('http://127.0.0.1:8000/chat', data = json.dumps(json_data) )
        st.session_state.past.append(user_message)
        st.session_state.generated.append(response)

    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state['past'][i], is_user=True, key=str(i) + "_user")
            response = st.session_state['generated'][i]
            if response is not None:
                try:
                    json_data = response.json()
                    message(json_data, key=str(i))
                except Exception as e:
                    st.error(f"Failed to convert response to JSON: {str(e)}")

stc.html('<div style="text-align: right;"> created by josys lab ai-1 </div>')
