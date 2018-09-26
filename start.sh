#!/bin/sh

gunicorn -p app.pid -w 4 -t 300 -b 0.0.0.0:18001 -D run:app