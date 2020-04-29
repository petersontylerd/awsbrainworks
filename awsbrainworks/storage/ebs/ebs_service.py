## libraries
import boto3
import os
import subprocess
import sys
import time

# custom imports
sys.path.append("{}/.aws".format(os.environ["WORKSPACE"]))
sys.path.append("{}/awsbrainworks".format(os.environ["WORKSPACE"]))

import aws_attributes
import awsbrainworks


def get_raw_volumes(self):
    """
    Documentation:

        ---
        Description:
            Associate each EBS volume ID with its EBS volume object.

        ---
        Returns:
           raw_volumes : dict
                Dictonary where the keys are EBS volume IDs and the
                values are the associated EBS volume objects.
    """
    # gather EBS volume objects
    raw_volumes = {}

    for volume in self.ebs_resource.volumes.all():
        raw_volumes[volume.id] = volume
    return raw_volumes

def get_volume_name_tags(self):
    """
    Documentation:

        ---
        Description:
            Associate EBS volume IDs with Name tags.

        ---
        Returns:
            volume_name_tags : dict
                Dictonary where the keys are EBS volume IDs
                and the values are the Name tags.
    """
    # return dictionary containing EBS volume ID / EBS volume pairs
    raw_volumes = self.get_raw_volumes()

    # gather Name tag for each EBS volume
    volume_name_tags = {}
    for volume in raw_volumes.values():
        try:
            for tag_set in volume.tags:
                if tag_set["Key"] == "Name":
                    volume_name_tags[volume.id] = tag_set["Value"]
                else:
                    continue
        except TypeError:
            continue

    return volume_name_tags

def get_volume_device_names(self):
    """
    Documentation:

        ---
        Description:
            Associate EBS volume names with device names.

        ---
        Returns:
            volume_device_names : dict
                Dictonary where the keys are EBS volume names
                and the values are the device names.
    """
    # return dictionary containing EBS volume ID / EBS volume pairs
    raw_volumes = self.get_raw_volumes()

    # gather Name tag for each EBS volume
    volume_device_names = {}
    for volume in raw_volumes.values():
        try:
            for tag_set in volume.attributes:
                if tag_set["Key"] == "Name":
                    volume_device_names[volume.id] = tag_set["Value"]
                else:
                    continue
        except TypeError:
            continue

    return volume_device_names

def get_volume_names(self):
    """
    Documentation:

        ---
        Description:
            Gather all Name tags of EBS volumes.

        ---
        Returns:
            volume_names : list
                List containing Name tags of all EBS volumes.
    """
    # return dictionary containing EBS volume ID / Name tag pairs
    volume_name_tags = self.get_volume_name_tags()

    # distill instance_name_tags down the Name tags
    volume_names = [volume for volume in volume_name_tags.values()]
    return volume_names

def get_volumes(self):
    """
    Documentation:

        ---
        Description:
            Associated each EBS volume object with its Name tag.

        ---
        Returns:
            volumes : dictionary
                Dictionary where the keys are the Name tags and
                the values are the EBS volume objects.
    """
    # return dictionary containing EBS volume ID / EBS volume pairs
    raw_volumes = self.get_raw_volumes()

    # return dictionary containing EBS volume ID / Name tag pairs
    volume_name_tags = self.get_volume_name_tags()

    # gather EBS volume object for each Name tag
    volumes = {}
    for volume_id, volume in raw_volumes.items():
        try:
            volumes[volume_name_tags[volume_id]] = volume
        except KeyError:
            continue

    return volumes