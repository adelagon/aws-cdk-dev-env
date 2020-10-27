from aws_cdk import (
    core,
    aws_ssm as ssm
)

class Secrets(core.Construct):

    @property
    def code_server_password(self):
        return self._code_server_password

    def __init__(self, scope: core.Construct, id: str, config: dict, **kwargs):
        super().__init__(scope, id, **kwargs)

        self._code_server_password = ssm.StringParameter(
            self,
            "CodeServerPassword",
            string_value=config["code_server_password"]
        )

    def grant_read(self, role):
        self._code_server_password.grant_read(role)