#!/usr/bin/env python3
import yaml
from aws_cdk import core

from aws_dev_env.aws_dev_env_stack import AwsDevEnvStack

config = yaml.load(open('./config.yaml'), Loader=yaml.FullLoader)

app = core.App()

env = core.Environment(region=config["core"]["region"])

stack_name = config["stack_name"] + "-" + config["environment"]
AwsDevEnvStack(app, stack_name, config, env=env)

app.synth()
