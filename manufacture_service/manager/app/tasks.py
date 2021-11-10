from app import app


@app.task
def simple_task(name):
    return f'Hello, {name}!'
