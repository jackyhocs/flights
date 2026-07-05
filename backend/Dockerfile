FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY skypath skypath

ENV FLIGHTS_DATASET_PATH=/data/flights.json

EXPOSE 5000

CMD ["python", "app.py"]
