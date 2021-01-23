# pull official python base image
FROM python:3.8

# set work directory
WORKDIR /ner-service

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy requirements file
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy project
COPY ./app ./app

# download spacy dependencies
RUN python -m spacy download en_core_web_sm

# run webservice
CMD ["python", "./app/main.py"]

