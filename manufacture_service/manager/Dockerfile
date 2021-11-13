# CELERY for manufacture service
FROM python
WORKDIR /code
COPY requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT celery -A app worker --loglevel=info
