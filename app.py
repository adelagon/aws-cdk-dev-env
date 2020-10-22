#!/usr/bin/env python3

from aws_cdk import core

from aws_dev_env.aws_dev_env_stack import AwsDevEnvStack


app = core.App()
AwsDevEnvStack(app, "aws-dev-env")

app.synth()
