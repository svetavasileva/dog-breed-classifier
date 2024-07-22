FROM python:3.9-slim

WORKDIR /app

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y libhdf5-dev pkg-config gcc

RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY webapp/ /app

COPY model/dog_breed_classifier_model.h5 /app/

EXPOSE 80

ENV FLASK_APP=app.py

CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]
