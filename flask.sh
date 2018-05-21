#!/bin/bash

export FLASK_ENV=development
export FLASK_APP=src/main/app.py
# export FLASK_DEBUG=1
# export CAPTCHA="on.captcha"

flask $*

