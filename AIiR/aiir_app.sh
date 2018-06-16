#!/bin/bash
python3 poller.py &
FLASK_APP=flaskhello.py flask run &
