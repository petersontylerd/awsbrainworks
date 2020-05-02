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
args = parser.parse_args()

## execute
if __name__ == "__main__":

    ### launch instance
    # instantiate launcher
    ec2_launcher = AWSBrainEC2InstanceManager(instance_name=args.instance_name)

    # access instance using SSH
    ec2_launcher.access_instance()