import os
from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda as _lambda,
    core
)

dirname = os.path.dirname(__file__)

class EC2(core.Construct):

    @property
    def instance(self):
        return self._instance

    @property
    def forwarder(self):
        return self._webhook_forwarder

    @property
    def role(self):
        return self._role

    def __init__(self, scope: core.Construct, id: str, vpc: ec2.IVpc, config: dict, region: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self._region = region

        ### EC2 Server for Jenkins
        image = ec2.GenericLinuxImage(
            {
                region: config["ami_id"],
            },
        )

        self._role = iam.Role(self, "InstanceRole", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))
        for policy in config["iam_role_policies"]:
            self._role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(policy))

        subnet = vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE).subnets[0]
        subnet_selection = ec2.SubnetSelection(subnets=[subnet])

        self.security_group = ec2.SecurityGroup(
            self, "EC2SG",
            vpc=vpc
        )

        self._instance = ec2.Instance(
            self, "EC2",
            instance_type=ec2.InstanceType(config["instance_type"]),
            machine_image=image,
            vpc=vpc,
            vpc_subnets=subnet_selection,
            role=self._role,
            security_group=self.security_group
        )

        core.CfnOutput(self, "CodeServerInstanceID", value=self._instance.instance_id)
    
    def add_ingress(self, peer):
        self.security_group.add_ingress_rule(
            peer,
            ec2.Port.tcp(8080)
        )

    def set_updates_on(self):
        self._instance.add_user_data(
            "yum check-update -y",
            "yum upgrade -y",
        )

    def set_efs_mount(self, efs, mount_point):
        self._instance.add_user_data(
            "yum install -y amazon-efs-utils",
            "yum install -y nfs-utils",
            "mkdir -p {}".format(mount_point),
            "test -f /sbin/mount.efs && echo {}: {} efs defaults,_netdev  >> /etc/fstab || ".format(efs.file_system_id, mount_point),
            "echo {}.efs.{}.amazonaws.com:/ {} nfs4 nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport,_netdev 0 0 >> /etc/fstab".format(
                efs.file_system_id,
                self._region,
                mount_point)
        )
        
    def set_code_server_password(self, password):
        # TODO: Probably it is best to use AWS Secrets Manager here
        self._instance.add_user_data(
            "sed -i 's/<CODESERVERPASSWD>/{}/' /lib/systemd/system/code-server.service".format(password),
        )

    def enable_code_server(self):
        self._instance.add_user_data(
            "systemctl enable code-server"
        )

    def disable_code_server(self):
        self._instance.add_user_data(
            "systemctl disable code-server"
        )

    def set_reboot(self):
        self._instance.add_user_data(
            "reboot",
        )

class InstanceScheduler(core.Construct):
    @property
    def function(self):
        return self._function

    def __init__(self, scope: core.Construct, id: str, instance: ec2.IInstance, **kwargs):
        super().__init__(scope, id, **kwargs)

        ec2_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "ec2:Start*",
                "ec2:Stop*"
            ],
            resources=["*"]
        )

        self._function = _lambda.Function(
            self,
            "InstanceSchedulerFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset(os.path.join(
                dirname, "lambda")),
            handler="instance_scheduler.lambda_handler",
        )

        self._function.add_to_role_policy(ec2_policy)
        self._function.add_environment(
            "InstanceID",
            instance.instance_id
        )