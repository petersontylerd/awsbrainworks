## libraries
import argparse
import boto3
import os
import subprocess
import sys
import time

# custom imports
sys.path.append(os.path.join(os.environ["HOME"], ".aws_attributes"))
sys.path.append(os.path.join(os.environ["HOME"],"workspace", "awsbrainworks"))

import aws_attributes
from awsbrainworks import (
    AWSBrainEC2InstanceManager,
    AWSBrainS3BucketManager,
)

## arguments
parser = argparse.ArgumentParser(description="")

parser.add_argument(
    "--instance_name",
    required=True,
    type=str,
    dest="instance_name",
    help="Name of EC2 instance.",
    )
parser.add_argument(
    "--buckets_to_sync",
    required=True,
    type=str,
    dest="buckets_to_sync",
    help="Name of bucket to sync.",
    )
args = parser.parse_args()

## execute
if __name__ == "__main__":
    ### create S# bucket manager
    # instantiate S3 bucket manager
    s3_manager = AWSBrainS3BucketManager()

    # convert input to string to list
    args.buckets_to_sync = s3_manager.parse_buckets_arg(args.buckets_to_sync)

    # if buckets_to_sync is not None, ensure these buckets exist
    assert set(args.buckets_to_sync).issubset(s3_manager.get_bucket_names()), "One or more of the buckets_to_sync does not exist on S3."

    ### create EBS volume manager
    # instantiate manager
    ec2_instance = AWSBrainEC2InstanceManager(instance_name=args.instance_name)

    ssh_tunnel = ec2_instance.get_ssh_tunnel()

    # sync S3 bucket to EBS volume
    ec2_instance.go_sync_ebs_volume_to_s3_bucket(
        args.buckets_to_sync,
        ssh_tunnel,
    )