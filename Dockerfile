FROM python:3.9.10-alpine3.14
COPY . /src
WORKDIR /src
RUN pip install -r requirements.txt