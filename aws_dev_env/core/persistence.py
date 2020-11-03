from aws_cdk import (
    aws_efs as efs,
    aws_ec2 as ec2,
    core
)

class SharedDisk(core.Construct):

    @property
    def fs(self):
        return self._fs
        
    def __init__(self, scope: core.Construct, id: str, vpc: ec2.IVpc, vpc_subnets: list, config: dict, **kwargs):
        super().__init__(scope, id, **kwargs)

        if config["efs"]["enabled"]:
            self._fs = efs.FileSystem(
                self,
                "EFS",
                vpc=vpc,
                vpc_subnets=vpc_subnets,
                encrypted=True,
                enable_automatic_backups=True,
                performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,
                throughput_mode=efs.ThroughputMode.BURSTING,
                lifecycle_policy=getattr(efs.LifecyclePolicy, config["efs"]["lifecycle_policy"])
            )
            core.CfnOutput(self, "EFS_FSID", value=self._fs.file_system_id)

    def allow_connection(self, resource):
        self._fs.connections.allow_default_port_from(resource)