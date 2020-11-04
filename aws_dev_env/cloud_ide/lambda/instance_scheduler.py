import os
import boto3

def lambda_handler(event, context):
    ec2 = boto3.client("ec2")
    instance_id = os.environ["InstanceID"]
    if "ScheduleOff" in event["resources"][0]:
        print("Turning OFF instances: {}".format(instance_id))
        ec2.stop_instances(InstanceIds=[instance_id])
    if "ScheduleOn" in event["resources"][0]:
        print("Turning ON instances: {}".format(instance_id))
        ec2.start_instances(InstanceIds=[instance_id])
