import os
from aws_cdk import (
    aws_ec2 as ec2,
    core
)
from cloud_ide.computes import (
    EC2,
    InstanceScheduler
)
from cloud_ide.certificates import Certificate
from cloud_ide.load_balancers import LoadBalancers
from cloud_ide.events import LambdaCron

dirname = os.path.dirname(__file__)

class CloudIDE(core.Construct):

    @property
    def instance(self):
        return self._ec2.instance

    def __init__(self, scope: core.Construct, id: str, vpc: ec2.IVpc, config: dict, **kwargs):
        # TODO: Add a better persistence store here EFS or S3 sync
        super().__init__(scope, id, **kwargs)

        self._ec2 = EC2(
            self,
            "Computes",
            vpc,
            config["cloud_ide"],
            config["core"]["region"]
        )

        if config["cloud_ide"]["enable_code_server"]:
            certificate = Certificate(
                self,
                "Certificate",
                config["cloud_ide"]["domain_name"]
            )

            load_balancers = LoadBalancers(
                self,
                "LoadBalancers",
                vpc,
                [self._ec2.instance],
                certificate.arn
            )

            self._ec2.add_ingress(load_balancers.public_load_balancer_security_group)
            self._ec2.set_code_server_password(config["cloud_ide"]["code_server_password"])
            self._ec2.enable_code_server()
        else:
            self._ec2.disable_code_server()

        instance_scheduler = InstanceScheduler(
            self,
            "InstanceScheduler",
            self._ec2.instance)

        self._schedules = []
        if config["cloud_ide"].get("schedule_on"):
            i = 1
            for schedule in config["cloud_ide"]["schedule_on"]:
                self._schedules.append(LambdaCron(
                    self,
                    "ScheduleOn{}".format(i),
                    schedule,
                    instance_scheduler.function
                ))
                i+=1

        if config["cloud_ide"].get("schedule_off"):
            i = 1
            for schedule in config["cloud_ide"]["schedule_off"]:
                self._schedules.append(LambdaCron(
                    self,
                    "ScheduleOff{}".format(i),
                    schedule,
                    instance_scheduler.function
                ))
                i+=1

    def set_user_data(self, updates=False, efs=False, mount_point=None, reboot=False):
        if updates:
            self._ec2.set_updates_on()
        if efs:
            self._ec2.set_efs_mount(efs, mount_point)
        if reboot:
            self._ec2.set_reboot()