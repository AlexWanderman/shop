# CELERY for manufacture service
FROM python
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT celery -A app worker --loglevel=info
