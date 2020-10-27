import os
from aws_cdk import (
    aws_ec2 as ec2,
    core
)
from cloud_ide.computes import Computes
from cloud_ide.certificates import Certificate
from cloud_ide.load_balancers import LoadBalancers
from cloud_ide.secrets import Secrets

dirname = os.path.dirname(__file__)

class CloudIDE(core.Construct):

    def __init__(self, scope: core.Construct, id: str, vpc: ec2.IVpc, config: dict, **kwargs):
        super().__init__(scope, id, **kwargs)

        secrets = Secrets(
            self,
            "Secrets",
            config["cloud_ide"]
        )

        computes = Computes(
            self,
            "Computes",
            vpc,
            config["cloud_ide"],
            config["core"]["region"]
        )

        certificate = Certificate(
            self,
            "Certificate",
            config["cloud_ide"]["domain_name"]
        )

        load_balancers = LoadBalancers(
            self,
            "LoadBalancers",
            vpc,
            [computes.instance],
            certificate.arn
        )

        secrets.grant_read(computes.role)
        computes.add_ingress(load_balancers.public_load_balancer_security_group)
