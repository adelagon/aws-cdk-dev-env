import yaml
from aws_cdk import (
    core
)

from core.networking import Network
from jenkins.jenkins import Jenkins
from cloud_ide.cloud_ide import CloudIDE

class AwsDevEnvStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, config: dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        network = Network(
            self,
            "VPC"
        )

        if config["cloud_ide"]["enabled"]:
            ide = CloudIDE(
                self,
                "CloudIDE",
                network.vpc,
                config
            )

        if config["jenkins"]["enabled"]:
            jenkins = Jenkins(
                self,
                "Jenkins",
                network.vpc,
                config
            )



