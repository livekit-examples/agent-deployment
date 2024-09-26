# AWS ECS Deployment Example

This directory demonstrates how to deploy the `agent-example` to a fly.io environment. 

Deployment configuration lives mostly in the `fly.toml` file. Documentation for chosen configuration can be found as comments in-line in that file.

The `scripts` directory contains scripts for the common deployment-lifecycle commands.

## Getting Started

### Install dependencies:


1. [AWS Cli](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
2. [Docker](https://docs.docker.com/engine/install/)

[!NOTE]
Once the aws cli is installed, you'll need to configure it.
There are a lot of ways to do this so we defer to the
(aws docs)[https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html]

### Create secrets
```bash
aws secretsmanager create-secret \
  --name ecs/python-agent-example/livekit-url \
  --region us-east-1 \
  --secret-string "wss://your-url-from-livekit-cloud-dashboard.livekit.cloud"

aws secretsmanager create-secret \
  --name ecs/python-agent-example/livekit-api-key \
  --region us-east-1 \
  --secret-string "api-key-from-livekit-cloud-dashboard"

aws secretsmanager create-secret \
  --name ecs/python-agent-example/livekit-api-secret \
  --secret-string "api-secret-from-livekit-cloud-dashboard"
```

These secrets are referenced in the cloudformation configuration and will 
be available as environment variables in the worker process. 
You will likely need to add additional secrets here as 
well depending on your agent, for example, `OPENAI_API_KEY`.

### Create Cloud Formation Stack

This example leverages cloud formation for creating resources in aws:
```bash
aws cloudformation create-stack \
  --stack-name agents-stack \
  --template-body file://cloudformation.yaml \
  --capabilities CAPABILITY_NAMED_IAM
```
Additional configuration for your specific agent should be done in the `cloudformation.yaml` file.

After modifying the `cloudformation.yaml` file you can run
```bash
aws cloudformation update-stack \
  --stack-name agents-stack \
  --template-body file://cloudformation.yaml \
  --capabilities CAPABILITY_NAMED_IAM
```

### Login Docker to your Image Repository

Fetch the repositoryUri from aws:
```bash
aws ecr describe-repositories
```

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin "<repository uri from above>"
```

### Build and Push Docker Image

```bash
docker build -t "<repository uri from above>":latest .
```

```bash
docker push "<repository uri from above>":latest
```