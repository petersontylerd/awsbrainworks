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


def get_volume(self):
    """
    Documentation:

        ---
        Description:
            Use a Name tag to return a single EBS volume object.

        ---
        Returns:
            volume : EBS volume
                EBS volume object.
    """
    # return dictionary containing Name tag / EBS volume object
    volumes = self.get_volumes()

    # check that there is an volume with that name
    assert self.volume_name in self.get_volume_names(), "\nNo EBS volume with that name.\n"

    # filter volumes by volume_name
    volume = volumes[self.volume_name]

    return volume

def get_volume_device_name(self):
    """
    Documentation:

        ---
        Description:
            Use a Name tag to return the EBS volume device name.

        ---
        Returns:
            volume_device_name : str
                EBS volume device name.
    """
    # filter volumes by volume_name
    volume_device_name = self.volume.attachments[0]["Device"]

    return volume_device_name

def go_attach_volume(self, instance_name, ebs_device_name="/dev/xvdf"):
    """
    Documentation:

        ---
        Description:
            Attach EBS volume to running or stopped EC2 instance.

        ---
        Parameters:
            instance_name : str
                Name of instance to attach EBS volume to.
            ebs_device_name : str, default="/dev/xvdf"
                Name to give block storage device within EC2 instance.
    """
    # create EC2 instance manager
    ec2 = awsbrainworks.AWSBrainEC2InstanceManager(instance_name=instance_name)

    # check that there is an volume with that name
    assert self.volume_name in self.get_volume_names(), "\nNo EBS volume with that name.\n"

    # check that there is an instance with that name
    assert ec2.instance_name in ec2.get_instance_names(), "\nNo activate EC2 instance with that name.\n"

    # attach volume to instance
    self.volume.attach_to_instance(
        Device=ebs_device_name,
        InstanceId=ec2.instance.id,
        DryRun=False,
    )

    ## waiter
    custom_filter = [{
                "Name":"tag:Name",
                "Values": [self.volume_name]
            },
    ]

    # wait until volume is available
    waiter = self.ebs_client.get_waiter('volume_in_use')
    waiter.wait(Filters=custom_filter)
    print("Success: EBS Volume '{}' is now in use by EC2 Instance '{}'".format(self.volume_name, ec2.instance_name))

def go_detach_volume(self, instance_name, ebs_device_name="/dev/xvdf"):
    """
    Documentation:

        ---
        Description:
            Detach EBS volume to running or stopped EC2 instance.

        ---
        Parameters:
            instance_name : str
                Name of instance to detach EBS volume from.
            ebs_device_name : str, default="/dev/xvdf"
                Name of block storage device within EC2 instance.
    """
    # create EC2 instance manager
    ec2 = awsbrainworks.AWSBrainEC2InstanceManager(instance_name=instance_name)

    # check that there is an volume with that name
    assert self.volume_name in self.get_volume_names(), "\nNo EBS volume with that name.\n"

    # check that there is an instance with that name
    assert ec2.instance_name in ec2.get_instance_names(), "\nNo activate EC2 instance with that name.\n"

    # detach volume from instance
    self.volume.detach_from_instance(
        Device=ebs_device_name,
        InstanceId=ec2.instance.id,
        DryRun=False,
    )

    ## waiter
    custom_filter = [{
                "Name":"tag:Name",
                "Values": [self.volume_name]
            },
    ]

    # wait until volume is available
    waiter = self.ebs_client.get_waiter('volume_available')
    waiter.wait(Filters=custom_filter)
    print("Success: EBS Volume '{}' is now detached from EC2 Instance '{}' and is available".format(self.volume_name, ec2.instance_name))

def go_delete_volume(self):
    """
    Documentation:

        ---
        Description:
            Delete EBS volume.
    """
    self.volume.delete()

    # ## waiter
    # custom_filter = [{
    #             "Name":"tag:Name",
    #             "Values": [self.volume_name]
    #         },
    # ]

    # # wait until volume is available
    # waiter = self.ebs_client.get_waiter('volume_deleted')
    # waiter.wait(Filters=custom_filter)
    # print("Success: EBS Volume '{}' is now deleted".format(self.volume_name))
