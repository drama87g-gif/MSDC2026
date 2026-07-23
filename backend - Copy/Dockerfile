FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app


cmd ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Create media dir
RUN mkdir -p /app/media

EXPOSE 8000

CMD ["gunicorn", "msdc_backend.wsgi:application", "--bind", "0.0.0.0:8000"]