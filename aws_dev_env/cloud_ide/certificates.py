from aws_cdk import (
    aws_ec2 as ec2,
    aws_certificatemanager as acm,
    core
)

class Certificate(core.Construct):

    @property
    def arn(self):        
        return self._certificate.certificate_arn

    def __init__(self, scope: core.Construct, id: str, domain_name: str,  **kwargs):
        super().__init__(scope, id, **kwargs)

        self._certificate = acm.Certificate(
            self,
            "Certificate",
            domain_name=domain_name,
            validation=acm.CertificateValidation.from_dns()
        )
