from celery import Celery
app = Celery('tasks', backend='redis://localhost:6379/0', broker='redis://localhost:6379/0')

# Use solo pool for Windows compatibility
app.conf.update(
    worker_pool='solo',
    worker_concurrency=1,
)

@app.task
def add(x, y):
    return x + y