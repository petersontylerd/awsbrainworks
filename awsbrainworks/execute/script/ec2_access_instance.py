## libraries
import argparse
import boto3
import os
import sys
import subprocess
import time

# custom imports
sys.path.append(os.path.join(os.environ["HOME"], ".aws_attributes"))
sys.path.append(os.path.join(os.environ["HOME"],"workspace", "awsbrainworks"))

import aws_attributes
from awsbrainworks import AWSBrainEC2InstanceManager


## arguments
parser = argparse.ArgumentParser(description="")

parser.add_argument(
    "--instance_name",
    required=True,
    type=str,
    dest="instance_name",
    help="Name of instance to self.ssh_tunnel.",
    )
parser.add_argument(
    "--start_if_stopped",
    required=False,
    default=False,
    action="store_true",
    dest="start_if_stopped",
    help="Controls whether to start the instance if it's stopped.",
    )
args = parser.parse_args()

## execute
if __name__ == "__main__":

    ### launch instance
    # instantiate launcher
    ec2_launcher = AWSBrainEC2InstanceManager(instance_name=args.instance_name)

    # access instance using SSH
    ec2_launcher.go_access_instance(
        start_if_stopped=args.start_if_stopped
    )