#!/bin/bash
cd ../script

python s3_create_bucket.py \
            --bucket_name=$1 \