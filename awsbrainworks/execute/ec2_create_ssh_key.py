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
from awsbrainworks import AWSBrainEC2InstanceService


## arguments
parser = argparse.ArgumentParser(description="")

parser.add_argument(
    "--key_name",
    type=str,
    dest="key_name",
    help="Name for the SSH key",
)
args = parser.parse_args()


## execute
if __name__ == "__main__":
    AWSBrainEC2InstanceService().go_create_ssh_key(args.key_name)