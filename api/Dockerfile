FROM python:3.9

ENV OPENAI_API_KEY '<your_api_key>'

WORKDIR /var/www/html

RUN pip install --upgrade pip

COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./app /app

#EXPOSE 8080
#CMD ["uvicorn", "pdf_vectorstore:api","--reload", "--host", "0.0.0.0", "--port","8080"]
