from aws_cdk import (
    aws_s3 as s3,
    Stack, 
    aws_lambda as lamb,
    aws_iam as iam,
    aws_s3_notifications as notifications,
    RemovalPolicy,
    Tags, 
    CfnOutput

)

from constructs import Construct


class s3lambda(Stack):
    def __init__(self, scope:Construct, construct_id:str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        #S3 bucket creation
        bucket = s3.Bucket(self,'SixthS3',
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True, 
        )

        #Bucket policy
        bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="SecureTransport",
                effect=iam.Effect.DENY,
                principals=[iam.AnyPrincipal()],
                actions=["s3:*"],
                resources=[bucket.bucket_arn, bucket.arn_for_objects("*")],
                conditions={"Bool": {"aws:SecureTransport": "false"}},
            )
        )

        #Lambda to parse new files landing in bucket
        new_lambda_function = lamb.Function(self, 'sixth-lambda',
             runtime= lamb.Runtime.PYTHON_3_13, 
             handler= "handler.lambda_handler",
             code= lamb.Code.from_asset("lambda")           
            )
        
        #Lambda read to bucket
        bucket.grant_read(new_lambda_function)
        
        #Invoke the lambda on every object creation event
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            notifications.LambdaDestination(new_lambda_function)
        )

        #Tags
        Tags.of(bucket).add("bucket-name", "sixth-s3")
        Tags.of(new_lambda_function).add("lambda-name", "sixth-lambda")

        #Output
        CfnOutput(self, "BucketName", value= bucket.bucket_name)
        CfnOutput(self, "LambdaName", value=new_lambda_function.function_name)
