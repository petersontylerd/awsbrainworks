## libraries
import argparse
import boto3
import os
import subprocess
import sys
import time

# custom imports
sys.path.append("{}/awsbrainworks".format(os.environ["WORKSPACE"]))
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
args = parser.parse_args()

## execute
if __name__ == "__main__":

    ### create s3 bucket manager
    # instantiate manager
    s3_manager = AWSBrainS3BucketManager()

    s3_manager.create_bucket(
        args.bucket_name
    )