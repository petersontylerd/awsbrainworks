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
from awsbrainworks import AWSBrainS3BucketCreator

## arguments
parser = argparse.ArgumentParser(description="")

parser.add_argument(
    "--bucket_name",
    required=True,
    type=str,
    dest="bucket_name",
    help="Name of bucket to create.",
)
args = parser.parse_args()

## execute
if __name__ == "__main__":

    ### create S3 bucket manager
    # instantiate manager
    s3_creator = AWSBrainS3BucketCreator(bucket_name=args.bucket_name)

    s3_creator.create_bucket()