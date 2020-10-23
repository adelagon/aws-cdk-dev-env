import yaml
from aws_cdk import (
    core
)

from core.networking import Network
from jenkins.jenkins import Jenkins

class AwsDevEnvStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, config: dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        network = Network(
            self,
            "VPC"
        )

        jenkins = Jenkins(
            self,
            "Jenkins",
            network.vpc,
            config
        )



