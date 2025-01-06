#!/bin/sh
set -e
cd ${PROJECT_NAME}

if [ ${RUN_LOAD_DATA} = "True" ]; then
    echo "===============Load User examples==============="
    python3 manage.py loaddata fixtures/*.json --settings=${DJANGO_SETTINGS_MODULE}
fi