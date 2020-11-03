from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    core
)

class LoadBalancers(core.Construct):

    @property
    def public_load_balancer_security_group(self):        
        return self._public_security_group

    def __init__(self, scope: core.Construct, id: str, vpc: ec2.IVpc, instances: list, certificate_arn: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        health_check = elbv2.HealthCheck(
            path="/",
            healthy_http_codes="200-399"
        )

        public_target_group = elbv2.ApplicationTargetGroup(
            self, "PublicTG",
            port=8080,
            vpc=vpc,
            health_check=health_check
        )

        for instance in instances:
            public_target_group.add_target(
                elbv2.InstanceTarget(
                instance.instance_id,
                port=8080
            )
        )   

        self._public_security_group  = ec2.SecurityGroup(
            self, "PublicLBSG",
            vpc=vpc
        )
        self._public_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(443)
        )

        self._public_lb = elbv2.ApplicationLoadBalancer(
            self, "PublicLB",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=vpc.select_subnets(subnet_type=ec2.SubnetType.PUBLIC).subnets),
            internet_facing=True,
            security_group=self._public_security_group
        )

        self._public_lb.add_listener(
            "PublicLBListener",
            certificates=[elbv2.ListenerCertificate(certificate_arn)],
            port=443,
            default_target_groups=[public_target_group])

        core.CfnOutput(self, "CloudIDE URL", value="https://{}".format(self._public_lb.load_balancer_dns_name))