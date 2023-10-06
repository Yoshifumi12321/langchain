# langchain
## streamlit_langchain.py
PDFの読み込み&ベクトル化して保存とLLMとの対話をインタラクティブに行えるアプリ
<img width="764" alt="image" src="https://github.com/Yoshifumi12321/langchain/assets/40589677/37db53f1-bf70-4936-8ebb-5d1bc931a96f">

### 起動方法
```bash
cd <langchainのローカルリポジトリ>/front #frontディレクトリに移動
docker-compose build # Streamlitのイメージををbuild
docker-compose up -d # Stremalitのイメージを起動 -d: コンソールログ非表示
```

## api/pdf_vectorstore.py
### 下記の機能を実現するAPI
1. PDFの読み込み&ベクトル化して保存
2. PDFの内容をもとに回答

### OpenAI API設定
下記Dockerfileの<your_api_key>にAPIトークンを置換する  
https://github.com/Yoshifumi12321/langchain/blob/main/api/Dockerfile
```bash
ENV OPENAI_API_KEY <your_api_key>
```

### 起動方法
```bash
cd <langchainのローカルリポジトリ>/api #apiディレクトリに移動
docker-compose build # FastAPIのイメージををbuild
docker-compose up -d # FastAPIのイメージを起動 -d: コンソールログ非表示
```

### curlでリクエスト方法
```bash
# PDFのアップロードとベクトル化
curl -X POST -F 'file=@<任意のファイル(PDF)>' http://127.0.0.1:8000/pdf
# 対話
curl -X POST -H 'Content-type: application/json' --data '{"query":"~について教えて"}' 'http://127.0.0.1:8000/chat'
```
