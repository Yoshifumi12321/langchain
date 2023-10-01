import os
import shutil

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

from pydantic import BaseModel  # リクエストbodyを定義するために必要

# API用
from fastapi import FastAPI, File, UploadFile

import tempfile

api = FastAPI()

#os.environ["OPENAI_API_KEY"] = '<input_your_api_key>'
model_name = "text-davinci-002"

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

  openai.api_key = os.getenv("OPENAI_API_KEY")
  llm = OpenAI(temperature=0,model_name=model_name,
    max_tokens=512,
    frequency_penalty=0.02
  )
  # save to disk
  embeddings = OpenAIEmbeddings()
  vectorstore = Chroma.from_documents(pages, embedding=embeddings, persist_directory="./chroma_db")
  vectorstore.persist()
  return True

# #################################
# 対話するためのAPI
# usage: curl -X POST -H 'Content-type: application/json' --data '{"query":"かんた ん決済について教えて"}' 'http://127.0.0.1:8000/chat'
class Chat(BaseModel):
  query: str

chat_history = []
@api.post("/chat")
def chat_query(chat: Chat):
  print(f"text: {chat.query}")
  openai.api_key = os.getenv("OPENAI_API_KEY")
  llm = OpenAI(temperature=0,model_name=model_name,
    max_tokens=512,
    frequency_penalty=0.02
  )
  query = chat.query

  # load from disk
  embeddings = OpenAIEmbeddings()
  vectorstore= Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
  # docs = vectorstore.similarity_search(query)
  # vectorstore.persist()
  pdf_qa = ConversationalRetrievalChain.from_llm(llm, vectorstore.as_retriever(), return_source_documents=True)
  result = pdf_qa({"question": query, "chat_history": chat_history})
  return result["answer"]

# 参考：https://python.langchain.com/docs/integrations/vectorstores/chroma
