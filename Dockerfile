FROM python:3.9.10
COPY . /src
WORKDIR /src
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt