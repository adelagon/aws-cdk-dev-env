import os
from aws_cdk import (
    aws_ec2 as ec2,
    core
)
from cloud_ide.computes import Computes
from cloud_ide.certificates import Certificate
from cloud_ide.load_balancers import LoadBalancers

dirname = os.path.dirname(__file__)

class CloudIDE(core.Construct):

    @property
    def instance(self):
        return self._computes.instance

    def __init__(self, scope: core.Construct, id: str, vpc: ec2.IVpc, config: dict, **kwargs):
        # TODO: Add a better persistence store here EFS or S3 sync
        super().__init__(scope, id, **kwargs)

        self._computes = Computes(
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
            [self._computes.instance],
            certificate.arn
        )

        self._computes.add_ingress(load_balancers.public_load_balancer_security_group)
        self._computes.set_code_server_password(config["cloud_ide"]["code_server_password"])

    def set_user_data(self, updates=False, efs=False, mount_point=None, reboot=False):
        if updates:
            self._computes.set_updates_on()
        if efs:
            self._computes.set_efs_mount(efs, mount_point)
        if reboot:
            self._computes.set_reboot()