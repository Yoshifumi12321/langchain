import os
import tempfile # PDFアップロードの際に必要

from langchain.chat_models import AzureChatOpenAI
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import AzureOpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.base import BaseCallbackHandler
import streamlit as st

from lib.rag import *

folder_name = "./.data"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# ストリーム表示
class StreamCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.tokens_area = st.empty()
        self.tokens_stream = ""

    def on_llm_new_token(self, token, **kwargs):
        self.tokens_stream += token
        self.tokens_area.markdown(self.tokens_stream)

# UI周り
st.title("QA")
st.chat_message("ai").write("こんにちは！AIアシスタントです🤖  <br>PDFを読み込むとその文書に記載されている内容から回答します。",unsafe_allow_html=True)

with st.sidebar:
    user_api_key = st.text_input(
        label="OpenAI API key",
        placeholder="Paste your openAI API key",
        type="password"
    )
    user_base_uri = st.text_input(
        label="Azure Endpoint",
        placeholder="Paste your openAI Endpoint",
    )
    # 
    os.environ['OPENAI_API_KEY'] = user_api_key
    os.environ["AZURE_OPENAI_ENDPOINT"] = user_base_uri
    os.environ["OPENAI_API_TYPE"] = 'azure'
    # 
    select_model = st.selectbox("Model", ["gpt-4-32k"])
    select_temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=0.0, step=0.1,)
    select_chunk_size = st.slider("Chunk", min_value=0.0, max_value=1000.0, value=300.0, step=10.0,)
    uploaded_file = st.file_uploader("Upload a file after paste OpenAI API key", type="pdf")

os.environ["OPENAI_API_VERSION"] = '2023-06-01-preview'
embeddings = AzureOpenAIEmbeddings(
    model="text-embedding-ada-002",
    azure_deployment="text-embedding-ada-002",
)

database = Chroma(
    persist_directory="./.data",
    embedding_function=embeddings,
)

# database.add_documents(data)
# retrieverに変換（検索、プロンプトの構築）
retriever = database.as_retriever()

chat = AzureChatOpenAI(
            model=select_model,
            temperature=select_temperature,
            streaming=True,
        )

# 会話履歴を初期化
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
    )

memory = st.session_state.memory

chain = ConversationalRetrievalChain.from_llm(
    llm=chat,
    retriever=retriever,
    memory=memory,
)

# UI用の会話履歴を初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# UI用の会話履歴を表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# UI周り
prompt = st.chat_input("Ask something about the file.")

if prompt:
    # UI用の会話履歴に追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = StreamCallbackHandler()
        with st.spinner("Thinking..."):
            response = chain(
                {"question": prompt},
                # callbacks=[stream], # ストリーム表示
            )
        st.markdown(response["answer"])
    # UI用の会話履歴に追加
    st.session_state.messages.append({"role": "assistant", "content": response["answer"]})

if uploaded_file:
    # 一時ファイルにPDFを書き込みバスを取得
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    loader = PyMuPDFLoader(file_path=tmp_file_path) 
    documents = loader.load() 

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = select_chunk_size,
        chunk_overlap  = 100,
        length_function = len,
    )

    data = text_splitter.split_documents(documents)

# メモリの内容をターミナルで確認
print(memory)
