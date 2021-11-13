# MANUFACTURE SERVICE
FROM python
WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT gunicorn --bind 0.0.0.0:5000 wsgi:app
