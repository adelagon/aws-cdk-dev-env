import os
from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda as _lambda,
    core
)

dirname = os.path.dirname(__file__)

class Computes(core.Construct):

    @property
    def instance(self):
        return self._instance

    @property
    def forwarder(self):
        return self._webhook_forwarder

    def __init__(self, scope: core.Construct, id: str, vpc: ec2.IVpc, config: dict, region: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        ### EC2 Server for Jenkins
        image = ec2.GenericLinuxImage(
            {
                region: config["ami_id"],
            },
        )

        role = iam.Role(self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2RoleforSSM"))

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
            role=role,
            security_group=self.security_group
        )

        ### Lambda for github webhooks
        self._webhook_forwarder = _lambda.Function(
            self, "WebHookForwarder",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset(os.path.join(
                dirname, "lambda", "webhook_forwarder")),
            handler="lambda_function.lambda_handler",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE).subnets)
        )
    
    def add_ingress(self, peer):
        self.security_group.add_ingress_rule(
            peer,
            ec2.Port.tcp(8080)
        )

    def set_webhook_url(self, url):
        self._webhook_forwarder.add_environment(
            "WEBHOOK_URL",
            ''.join(["http://", url, "/github-webhook/"])
        )
