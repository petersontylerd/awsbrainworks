## libraries
import argparse
import boto3
import os
import subprocess
import sys
import time

# custom imports
sys.path.append("{}/awsbrainworks".format(os.environ["WORKSPACE"]))
from awsbrainworks import AWSBrainEBSVolumeManager


## arguments
parser = argparse.ArgumentParser(description="")

parser.add_argument(
    "--buckets_to_sync",
    required=True,
    type=str,
    dest="buckets_to_sync",
    help="Name of bucket to create.",
)
args = parser.parse_args()

## execute
if __name__ == "__main__":

    ### create EBS volume manager
    # instantiate manager
    ebs_manager = AWSBrainEBSVolumeManager()

    ebs_manager.sync_ebs_s3(
        args.buckets_to_sync
    )