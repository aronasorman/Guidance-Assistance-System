#!/bin/bash

DBNAME='counselor.db'

if [[ -e  "$DBNAME" ]]; then
    rm $DBNAME
fi

bin/python init_db.py
bin/python generate_period.py
bin/python import_registrar_csv.py 00-xxx.csv
bin/python test_data.py
