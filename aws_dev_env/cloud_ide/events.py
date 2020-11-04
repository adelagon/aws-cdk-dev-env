from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as events_targets
)

class LambdaCron(core.Construct):

    def __init__(self, scope: core.Construct, id: str, schedule: dict, function: _lambda.IFunction, **kwargs):
        super().__init__(scope, id, **kwargs)

        target = events_targets.LambdaFunction(handler=function)

        self._rule = events.Rule(
            self,
            "CWRule",
            schedule=events.Schedule.expression(schedule),
            targets=[target]
        )
