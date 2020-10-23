import os
from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda as _lambda,
    core
)
from jenkins.computes import Computes
from jenkins.load_balancers import LoadBalancers
from jenkins.api_gateway import APIGateway

dirname = os.path.dirname(__file__)

class Jenkins(core.Construct):

    @property
    def instance(self):
        return self._instance

    @property
    def forwarder(self):
        return self._webhook_forwader

    def __init__(self, scope: core.Construct, id: str, vpc: ec2.IVpc, config: dict, **kwargs):
        super().__init__(scope, id, **kwargs)

        computes = Computes(
            self,
            "Computes",
            vpc,
            config["jenkins"],
            config["core"]["region"]
        )

        load_balancers = LoadBalancers(
            self,
            "LoadBalancers",
            vpc,
            [computes.instance]
        )

        api_gateway = APIGateway(
            self,
            "APIGateway",
            computes.forwarder
        )
        
        computes.add_ingress(load_balancers.private_load_balancer_security_group)
        computes.add_ingress(load_balancers.public_load_balancer_security_group)
        computes.set_webhook_url(load_balancers.private_load_balancer_dns)