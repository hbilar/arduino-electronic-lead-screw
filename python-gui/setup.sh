#!/bin/bash

progdir=$(dirname $0)
source $progdir/config.sh

echo "Setting up a virtualenv called $venv"

virtualenv -p /usr/bin/python3.6 --always-copy --download $venv

echo "Start your env by running:"
echo "source $venv/bin/activate"


source $venv/bin/activate 

cd $progdir
pip install -r requirements.txt

