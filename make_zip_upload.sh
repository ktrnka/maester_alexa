#!/usr/bin/env bash

set -e
set -x

mkdir -p temp
cp src/handler.py temp
cp src/private.py temp

cd temp
zip -r ../master_lambda.zip *
cd -
rm -rf temp