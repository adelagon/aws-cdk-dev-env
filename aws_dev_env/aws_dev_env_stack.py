import yaml
from aws_cdk import (
    core
)

from core.networking import Network
from core.persistence import SharedDisk
from jenkins.jenkins import Jenkins
from cloud_ide.cloud_ide import CloudIDE

class AwsDevEnvStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, config: dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        network = Network(
            self,
            "VPC"
        )

        shared_disk = SharedDisk(
            self,
            "SharedDisk",
            network.vpc,
            network.private_subnets
        )

        if config["cloud_ide"]["enabled"]:
            ide = CloudIDE(
                self,
                "CloudIDE",
                network.vpc,
                config
            )
            shared_disk.allow_connection(ide.instance)
            ide.set_user_data(
                updates=config["cloud_ide"]["update_on_create"],
                reboot=config["cloud_ide"]["reboot_on_create"],
                mount_point=config["cloud_ide"]["efs_mount_point"],
                efs=shared_disk.fs
            )

        if config["jenkins"]["enabled"]:
            jenkins = Jenkins(
                self,
                "Jenkins",
                network.vpc,
                config
            )



