# AWS ECS Deployment Example

This directory demonstrates how to deploy the `agent-example` to AWS ECS. 

Deployment configuration lives mostly in the `cloudformation.yaml` file. 

## Getting Started

### Copy Example App w/ Dockerfile 

This guide assumes the app and relevant files exist in this directory. 
We provide an example app in the `agent-example-app` directory at the top-level of this repo.

```bash
cp ../agent-example-app/* .
cp ../agent-example-app/.dockerignore .
```

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
  --name ecs/agent-example/livekit-url \
  --region us-east-1 \
  --secret-string "wss://your-url-from-livekit-cloud-dashboard.livekit.cloud"

aws secretsmanager create-secret \
  --name ecs/agent-example/livekit-api-key \
  --region us-east-1 \
  --secret-string "api-key-from-livekit-cloud-dashboard"

aws secretsmanager create-secret \
  --name ecs/agent-example/livekit-api-secret \
  --secret-string "api-secret-from-livekit-cloud-dashboard"
```

Update the cloudformation.yaml with the arn from these created secrets.

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

This will scaffold:
- VPC + Subnet
- ECS Cluster
- ECR (Docker Repository)
- ECS Task Definition with configuration for the agent-example
- IAM Role for ECS Task Definition execution
- ECS Service for the agent-example

The `DesiredCount` set on the ECS Service is initially set to `0`. This is
because there is a chicken-egg problem:
- The Docker repository and `agent-example` docker image don't exist
- The CloudFormation stack creation won't succeed until the service starts successfully
- The Service depends on the Docker image

In the next steps, we will build and push the Docker image and scale the Service.

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
docker buildx build --platform linux/amd64 -t "<repository uri from above>":<version> --push .
```

Update the image used in the `AgentExampleService` section in `cloudformation.yaml`

### Scale the service

Now that the image exists, we can scale the service. We'll start once instance
by setting `DesiredCount: 1` in the `AgentExampleService` of `cloudformation.yaml`.

Once you make this change, run:

```bash
aws cloudformation update-stack \
  --stack-name agents-stack \
  --template-body file://cloudformation.yaml \
  --capabilities CAPABILITY_NAMED_IAM
```

### Updating a deployment

```bash
docker buildx build --platform linux/amd64 -t "<repository uri from above>":<new version> --push .
```

Then update the image in cloudformation and run the `update-stack` command again.