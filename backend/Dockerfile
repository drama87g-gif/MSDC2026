FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 5000

# Create uploads directory
RUN mkdir -p /app/uploads

# Run Flask app with development server (gunicorn can be used in production)
CMD ["flask", "run", "--host", "0.0.0.0"]
