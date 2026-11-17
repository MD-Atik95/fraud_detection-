FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python -m fraud.train
EXPOSE 8000 8501
CMD ["uvicorn", "fraud.api:app", "--host", "0.0.0.0", "--port", "8000"]
