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


def go_create_volume(self):
    """
    Documentation:

        ---
        Description:
            Create new EBS volume.
    """
    # check that there is an volume with that name
    assert self.volume_name not in self.get_volume_names(), "\nEBS name already associated with another volume.\n"

    # check that there is an instance with that name
    self.ebs_client.create_volume(
        AvailabilityZone=aws_attributes.AVAILABILITY_ZONE,
        Encrypted=False,
        Size=self.volume_size,
        VolumeType=self.volume_type,
        DryRun=False,
        TagSpecifications=[
            {
                "ResourceType": "volume",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": self.volume_name,
                    },
                ]
            },
        ],
        MultiAttachEnabled=False
    )

    ## waiter
    custom_filter = [{
                "Name":"tag:Name",
                "Values": [self.volume_name]
            },
    ]

    # wait until volume is available
    print("EBS Volume initializing...")
    waiter = self.ebs_client.get_waiter('volume_available')
    waiter.wait(Filters=custom_filter)
    print("Success: EBS Volume '{}' is now available".format(self.volume_name))

    # get EBS volume object for newly created volume
    self.volume = self.get_volume()