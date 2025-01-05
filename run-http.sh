#!/bin/bash
python3 -m gunicorn 'main:create_app()' -b 127.0.0.1:9999 -w 1