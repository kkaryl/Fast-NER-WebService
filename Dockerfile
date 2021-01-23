FROM python:3.8

WORKDIR /ner-service

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./app ./app

RUN python -m spacy download en_core_web_sm

CMD ["python", "./app/main.py"]

# docker build -t ner-service .
# docker run -p 8000:8000 ner-service
# XX docker run -t -i ner-service

# Check running containers
## docker container ls
# Kill container
## docker rm -f <container-name>


# Normal cmd go to docker image shell
## docker ps
## docker exec -it 7cd92bc852f6 /bin/sh
