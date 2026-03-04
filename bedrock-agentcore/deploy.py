"""Deploy LiveKit agent to Amazon Bedrock AgentCore Runtime.

Creates an AgentCore Runtime with your containerized agent.
Run after building and pushing your Docker image to ECR.

Usage:
    export AWS_ACCOUNT_ID=123456789012
    export SUBNET_IDS=subnet-abc123,subnet-def456
    export SECURITY_GROUP_IDS=sg-abc123
    export ROLE_ARN=arn:aws:iam::123456789012:role/AgentCoreRuntimeRole
    python deploy.py
"""

import os
import sys

import boto3

REGION = os.getenv("AWS_REGION", "us-west-2")
ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID", "")
ECR_REPO_NAME = os.getenv("ECR_REPO_NAME", "livekit-agentcore-agent")
AGENT_RUNTIME_NAME = os.getenv("AGENT_RUNTIME_NAME", "livekit-voice-agent")
SUBNET_IDS = os.getenv("SUBNET_IDS", "")
SECURITY_GROUP_IDS = os.getenv("SECURITY_GROUP_IDS", "")
ROLE_ARN = os.getenv("ROLE_ARN", "")


def deploy():
    missing = [v for v, val in [
        ("AWS_ACCOUNT_ID", ACCOUNT_ID), ("SUBNET_IDS", SUBNET_IDS),
        ("SECURITY_GROUP_IDS", SECURITY_GROUP_IDS), ("ROLE_ARN", ROLE_ARN),
    ] if not val]

    if missing:
        print(f"Error: Missing environment variables: {', '.join(missing)}")
        sys.exit(1)

    container_uri = f"{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/{ECR_REPO_NAME}:latest"
    subnets = [s.strip() for s in SUBNET_IDS.split(",") if s.strip()]
    security_groups = [s.strip() for s in SECURITY_GROUP_IDS.split(",") if s.strip()]

    print(f"Deploying: {AGENT_RUNTIME_NAME}")
    print(f"  Container: {container_uri}")
    print(f"  Subnets:   {subnets}")
    print(f"  SGs:       {security_groups}")

    client = boto3.client("bedrock-agentcore-control", region_name=REGION)

    try:
        resp = client.create_agent_runtime(
            agentRuntimeName=AGENT_RUNTIME_NAME,
            agentRuntimeArtifact={
                "containerConfiguration": {"containerUri": container_uri}
            },
            networkConfiguration={
                "networkMode": "VPC",
                "networkModeConfig": {
                    "subnets": subnets,
                    "securityGroups": security_groups,
                },
            },
            roleArn=ROLE_ARN,
        )
        print(f"\nCreated! ARN: {resp['agentRuntimeArn']}")
        print(f"Status: {resp['status']}")
    except client.exceptions.ConflictException:
        print(f"Runtime '{AGENT_RUNTIME_NAME}' already exists. Delete it first or use a different name.")
        sys.exit(1)


if __name__ == "__main__":
    deploy()
