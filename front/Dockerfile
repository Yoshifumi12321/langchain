FROM python:3.9

ENV OPENAI_API_KEY aaaa

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

EXPOSE 8501
ENTRYPOINT ["streamlit", "run"]
CMD ["/code/app/streamlit_langchain.py"]

#CMD ["uvicorn", "app.api.pdf_vectorstore:api", "--host", "0.0.0.0", "--port","80"]
