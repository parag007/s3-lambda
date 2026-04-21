import aws_cdk as cdk

from s3.s3_bucket_creation import s3lambda

app = cdk.App()
s3lambda(app, "create-bucket-lambda")
app.synth()