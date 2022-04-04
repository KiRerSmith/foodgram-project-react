FROM python:3.7-slim

WORKDIR /app

COPY backend/requirements.txt .

COPY data/ ./data

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY backend/foodgram/ .


CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"] 