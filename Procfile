web: gunicorn restaurants.wsgi --log-file -
worker: celery -A restaurants worker -l info
