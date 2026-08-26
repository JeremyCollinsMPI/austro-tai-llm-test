FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV NLP_API_URL=http://13.229.134.226:5000/chat
ENV NLP_MODEL=gpt-4.1

ENTRYPOINT ["python", "-m", "src.main"]
