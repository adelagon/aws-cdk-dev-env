from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    core
)

class LoadBalancers(core.Construct):

    @property
    def private_load_balancer_security_group(self):        
        return self._private_security_group

    @property
    def public_load_balancer_security_group(self):        
        return self._public_security_group

    @property
    def private_load_balancer_dns(self):
        return self._private_lb.load_balancer_dns_name

    def __init__(self, scope: core.Construct, id: str, vpc: ec2.IVpc, instances: list, **kwargs):
        super().__init__(scope, id, **kwargs)

        health_check = elbv2.HealthCheck(
            path="/login"
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

        private_target_group = elbv2.ApplicationTargetGroup(
            self, "PrivateTG",
            port=8080,
            vpc=vpc,
            health_check=health_check
        )

        for instance in instances:
            private_target_group.add_target(
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
            ec2.Port.tcp(80),
        )

        self._public_lb = elbv2.ApplicationLoadBalancer(
            self, "PublicLB",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=vpc.select_subnets(subnet_type=ec2.SubnetType.PUBLIC).subnets),
            internet_facing=True,
            security_group=self._public_security_group
        )

        self._public_lb.add_listener("PublicLBListener", port=80, default_target_groups=[public_target_group])

        self._private_security_group  = ec2.SecurityGroup(
            self, "PrivateLBSG",
            vpc=vpc
        )
        self._private_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
        )

        self._private_lb = elbv2.ApplicationLoadBalancer(
            self, "PrivateLB",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE).subnets),
            internet_facing=False,
            security_group=self._private_security_group
        )

        self._private_lb.add_listener("PrivateLBListener", port=80, default_target_groups=[private_target_group])
