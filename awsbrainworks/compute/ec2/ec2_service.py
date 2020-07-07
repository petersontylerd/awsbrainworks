## libraries
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


def get_raw_instances(self):
    """
    Documentation:

        ---
        Description:
            Associate each EC2 instance ID with its EC2 instance object.

        ---
        Returns:
           raw_instances : dict
                Dictonary where the keys are EC2 instance IDs and the
                values are the associated EC2 instance objects.
    """
    # gather EC2 instance object for each EC2 instance ID
    raw_instances = {}
    for instance in self.ec2_resource.instances.all():
        raw_instances[instance.id] = instance

    return raw_instances

def get_instance_name_tags(self):
    """
    Documentation:

        ---
        Description:
            Associate active EC2 instance IDs with Name tags.

        ---
        Returns:
            instance_name_tags : dict
                Dictonary where the keys are EC2 instance IDs
                and the values are the Name tags.
    """
    # return dictionary containing EC2 instance ID / EC2 instance pairs
    raw_instances = self.get_raw_instances()

    # gather Name tag for each active EC2 instance
    instance_name_tags = {}
    for instance in raw_instances.values():
        try:
            for tag_set in instance.tags:
                if tag_set["Key"] == "Name":
                    instance_name_tags[instance.id] = tag_set["Value"]
                else:
                    continue
        except TypeError:
            continue

    return instance_name_tags

def get_instance_names(self):
    """
    Documentation:

        ---
        Description:
            Gather all Name tags of active EC2 instances.

        ---
        Returns:
            instance_names : list
                List containing Name tags of all active EC2 instances.
    """
    # return dictionary containing EC2 instance ID / Name tag pairs
    instance_name_tags = self.get_instance_name_tags()

    # distill instance_name_tags down the Name tags
    instance_names = [instance for instance in instance_name_tags.values()]
    return instance_names

def get_instances(self):
    """
    Documentation:

        ---
        Description:
            Associated each EC2 instance object with its Name tag.

        ---
        Returns:
            instances : dictionary
                Dictionary where the keys are the Name tags and
                the values are the EC2 instance objects.
    """
    # return dictionary containing EC2 instance ID / EC2 instance pairs
    raw_instances = self.get_raw_instances()

    # return dictionary containing EC2 instance ID / Name tag pairs
    instance_name_tags = self.get_instance_name_tags()

    # gather EC2 instance object for each Name tag
    instances = {}
    for instance_id, instance in raw_instances.items():
        try:
            instances[instance_name_tags[instance_id]] = instance
        except KeyError:
            continue

    return instances

def go_create_ssh_key(self, key_name):
    """
    Documentation:

        ---
        Description:
            Generate SSH public key and private key. The private
            key is stored one level higher in the directory in a
            folder called .ssh.

        ---
        Parameters:
            key_name : str
                Name to give .pem private key file.
    """
    # set folder and file variables
    ssh_path = os.path.join(os.environ["HOME"], ".ssh")
    key_path = os.path.join(ssh_path, "{}.pem".format(key_name))

    # make hidden folder for SSH keys
    if not os.path.isdir(ssh_path):
        os.makedirs(ssh_path)

    # create a file to store the key locally
    outfile = open(key_path, "w")

    # call the boto ec2 function to create a key pair
    key_pair = self.ec2_resource.create_key_pair(KeyName=key_name)

    # capture the key and store it in a file
    KeyPairOut = str(key_pair.key_material)
    outfile.write(KeyPairOut)

    # make file executable
    os.chmod(key_path, int("400", base=8))

def get_instance_types(self):
    """
    Documentation:

        ---
        Description:
            Generate SSH pub
    """
    instance_types = sorted([instance_type["InstanceType"] for instance_type in self.ec2_client.describe_instance_types()["InstanceTypes"]])
    return instance_types
