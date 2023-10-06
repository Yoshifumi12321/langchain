FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

#EXPOSE 8501
#ENTRYPOINT ["streamlit", "run"]
#CMD ["/code/app/streamlit_langchain.py"]
