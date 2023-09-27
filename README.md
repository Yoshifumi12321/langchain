# langchain

## streamlit_langchain.py
PDFの読み込み&ベクトル化して保存とLLMとの対話をインタラクティブに行えるアプリ

起動方法
```bash
streamlit run streamlit_langchain.py
```

## api/pdf_vectorstore.py
下記の機能を実現するAPI
1. PDFの読み込み&ベクトル化して保存
2. PDFの内容をもとに回答

呼び出し方法
```bash
# PDFのアップロードとベクトル化
curl -X POST -F 'file=@<任意のファイル(PDF)>' http://127.0.0.1:8000/pdf
# 対話
curl -X POST -H 'Content-type: application/json' --data '{"query":"~について教えて"}' 'http://127.0.0.1:8000/chat'
```
