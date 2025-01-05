#!/bin/bash
gunicorn 'main:create_app()' -b 0.0.0.0:9932 --certfile=../cert.crt --keyfile=../cert.key -w 1