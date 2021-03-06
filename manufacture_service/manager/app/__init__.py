from celery import Celery

# TODO Move to env
app = Celery(
    'app',
    broker='amqp://admin:whatever@rabbit:5672',  # Defined in compose
    backend='rpc://',
    include=['app.tasks']
)

if __name__ == '__main__':
    app.start()
