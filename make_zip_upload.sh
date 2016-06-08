#!/usr/bin/env bash

set -e
set -x

TMP=temp

mkdir -p $TMP

# copy any required files
cp src/handler.py $TMP
cp src/private.py $TMP

# install any requirements
pip install -r requirements-lambda.txt -t $TMP

cd $TMP
zip -r ../master_lambda.zip *
cd -
rm -rf $TMP