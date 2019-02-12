FROM python:latest

WORKDIR /app
RUN pip install pipenv
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install
COPY main.py .
COPY .env .
COPY just.html .
