# coding=utf-8

# gunicorn -c gunicorn_conf.py -b 0.0.0.0:18001 run:app
daemon = True
worker_class = 'gevent'
pidfile = 'app.pid'
workers = 8
timeout = 300
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'
accesslog = 'access.log'
errorlog = 'error.log'
