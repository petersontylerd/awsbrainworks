## libraries
import argparse
import boto3
import os
import subprocess
import sys
import time

# custom imports
sys.path.append(os.path.join(os.environ["HOME"], ".aws_attributes"))
sys.path.append(os.path.join(os.environ["HOME"],"repos", "awsbrainworks"))

import aws_attributes
from awsbrainworks import AWSBrainS3BucketManager

## arguments
parser = argparse.ArgumentParser(description="")

parser.add_argument(
    "--bucket_name",
    required=True,
    type=str,
    dest="bucket_name",
    help="Name of bucket to create.",
)
parser.add_argument(
    "--local_object",
    required=True,
    type=str,
    dest="local_object",
    help="Name of file or directory to move to bucket.",
)
parser.add_argument(
    "--prefix",
    required=False,
    type=str,
    dest="prefix",
    help="Optional string to append to front of S3 object name.",
)
args = parser.parse_args()


## execute
if __name__ == "__main__":

    ### create S3 bucket manager
    # instantiate manager
    s3_manager = AWSBrainS3BucketManager(bucket_name=args.bucket_name)

    s3_manager.go_upload_local_object_to_bucket(
        args.bucket_name,
        args.local_object,
        args.prefix,
    )