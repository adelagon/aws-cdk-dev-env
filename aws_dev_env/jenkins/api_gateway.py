from aws_cdk import(
    core,
    aws_lambda as _lambda,
    aws_apigateway as apigw
)

class APIGateway(core.Construct):

    def __init__(self, scope: core.Construct, id: str, func: _lambda.IFunction, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        api = apigw.RestApi(
            self,
            "APIGateway",
        )

        entity = api.root.add_resource("github")
        entity_lambda_integration = apigw.LambdaIntegration(
            func,
            proxy=True
        )
        entity.add_method("POST", entity_lambda_integration)
