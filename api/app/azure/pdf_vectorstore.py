import os
import shutil

# import openai
import chromadb
import langchain
from langchain.llms import OpenAI

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import PyPDFLoader

from pydantic import BaseModel  # リクエストbodyを定義するために必要

# API用

from fastapi import FastAPI, File, UploadFile

import tempfile

api = FastAPI()

#os.environ["OPENAI_API_KEY"] = '<input_your_api_key>'
model_name = "gpt-4-32k"

os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_KEY"] = ""
os.environ["OPENAI_API_BASE"] = ""

from langchain.document_loaders import PyPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import AzureChatOpenAI

# ######################################
# PDFを読み込みベクトル化して保存するためのAPI
# usage: curl -X POST -F 'file=@./docs/kantan_service.pdf' http://127.0.0.1:8000/pdf
@api.post("/pdf")
async def post(file: UploadFile = File(...)):
  if file:
    # アップロードされたファイルをローカルにコピー
    pdf_filename = file.filename
    pdf_fileobj = file.file
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
      print(tmp_file.name)
      pdf_upload_dir = open(tmp_file.name,'wb+')
      # アップロードされたファイルをローカルにコピー
      shutil.copyfileobj(pdf_fileobj, pdf_upload_dir)
      # ベクトル化して保存
      to_vectorstore(pdf_upload_dir.name)
      pdf_upload_dir.close()
    return {"message": "PDFが正常に読み込まれました"}
  return {"Error": "アップロードファイルが見つかりません。"}

# ベクトル化して保存する関数
def to_vectorstore(pdf_file_path):
  loader = PyPDFLoader(pdf_file_path)
  pages = loader.load_and_split()
  # save to disk
  # embeddings = OpenAIEmbeddings()
  embeddings = OpenAIEmbeddings(
    model='text-embedding-ada-002',
    model_kwargs={"deployment_id":"text-embedding-ada-02"},
    chunk_size=1)
  vectorstore = Chroma.from_documents(pages, embedding=embeddings, persist_directory="./chroma_db")
  vectorstore.add_documents(documents=pages, embedding=embeddings)
  vectorstore.persist()
  return True

# #################################
# 対話するためのAPI
# usage: curl -X POST -H 'Content-type: application/json' --data '{"query":"かんた ん決済について教えて","chat_history":[]}' 'http://127.0.0.1:8000/chat'
class Chat(BaseModel):
  query: str
  chat_history: list

chat_history = []
@api.post("/chat")
def chat_query(chat: Chat):
  print(chat)
  print(f"text: {chat.query}")
  # openai.api_key = os.getenv("OPENAI_API_KEY")
  # 検索用のLLMsを定義
  llm = OpenAI(model_name='gpt-4-32k', model_kwargs={"deployment_id":"gpt-4-32k"},
               max_tokens=1024,
               frequency_penalty=0.02,
               temperature=0.1
               )
  # llm = OpenAI(temperature=0,model_name=model_name,
  #   max_tokens=512,
  #   frequency_penalty=0.02
  # )

  query = chat.query

  # load from disk
  # embeddings = OpenAIEmbeddings()
  embeddings = OpenAIEmbeddings(
    model='text-embedding-ada-002',
    model_kwargs={"deployment_id":"text-embedding-ada-02"},
    chunk_size=5)
  vectorstore= Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

  # 検索・参照先ファイルを出力するチェーンを作成
  pdf_qa = ConversationalRetrievalChain.from_llm(llm, vectorstore.as_retriever(), return_source_documents=True)

  # # テキストをベクトル化/インデックス化
  # index = VectorstoreIndexCreator(embedding=embeddings).from_loaders([loader])

  # result = pdf_qa({"question": query, "chat_history": chat_history})
  # return chain({chain.question_key: query})["answer"]

  return pdf_qa({"question": query, "chat_history": chat_history})
  # return index.query(llm=llm, question=query)

# 参考：https://python.langchain.com/docs/integrations/vectorstores/chroma
