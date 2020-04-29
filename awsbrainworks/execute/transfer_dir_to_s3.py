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
parser.add_argument(
    "--local_directory",
    required=True,
    type=str,
    dest="local_directory",
    help="Name of directory to move to bucket.",
)
parser.add_argument(
    "--prefix",
    type=str,
    default="",
    dest="prefix",
    help="String to append to beginning of file name in s3 bucket.",
)
args = parser.parse_args()


## execute
if __name__ == "__main__":

    ### create s3 bucket manager
    # instantiate manager
    s3_manager = AWSBrainS3BucketManager()

    s3_manager.upload_directory_to_bucket(
        args.bucket_name,
        args.local_directory,
        args.prefix,
    )