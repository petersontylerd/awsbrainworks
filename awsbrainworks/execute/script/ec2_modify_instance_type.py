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
import awsbrainworks

## arguments
parser = argparse.ArgumentParser(description="")


parser.add_argument(
    "--instance_name",
    required=True,
    type=str,
    dest="instance_name",
    help="Name of instance to stop.",
)
parser.add_argument(
    "--instance_type",
    required=True,
    type=str,
    dest="instance_type",
    help="The type of EC2 instance to change to.",
)


if __name__ == "__main__":

    ### launch instance
    # instantiate launcher
    ec2_launcher = AWSBrainEC2InstanceManager()

    ec2_launcher.modify_instance_type(
        args.instance_name,
        args.instance_type,
    )
