#!/bin/bash

export FLASK_ENV=development
export FLASK_APP=src/main/__init__.py

flask $*

