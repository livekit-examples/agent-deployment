# Amazon Bedrock AgentCore Runtime

Deploy a LiveKit voice agent to [Amazon Bedrock AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) — a serverless container hosting service with auto-scaling, session isolation, and CloudWatch observability.

The agent runs as a standard LiveKit WebRTC participant inside an AgentCore container. It connects to LiveKit Cloud (or a self-hosted server) through a TURN server for NAT traversal. No code changes to `livekit-agents` are required.

**Voice pipeline in this example:** Amazon Transcribe (STT) → Amazon Bedrock Nova Lite (LLM) → Amazon Polly (TTS)

## Architecture

![Architecture Overview](./architecture.svg)

AgentCore Runtime deploys in VPC mode with a NAT Gateway for internet access. The TURN server relays WebRTC media between the agent (behind NAT) and LiveKit.

## How this example differs from ECS / Kubernetes

Unlike the `aws-ecs/` or `kubernetes/` folders in this repo, this example includes agent-side code (`agent.py`, `kvs_turn.py`) in addition to deployment configuration. This is because AgentCore runs agents in microVMs inside a VPC, which requires TURN server configuration for WebRTC NAT traversal — a requirement that doesn't apply to ECS or Kubernetes deployments where the agent has direct network access.

This example also includes its own ARM64 Dockerfile because AgentCore requires `linux/arm64` containers, whereas the shared `python-agent-example-app/Dockerfile` targets amd64. This ARM64 variant could be useful as a shared option in `python-agent-example-app/` for anyone deploying to Graviton instances or developing on Apple Silicon.

## Prerequisites

- **AWS account** with permissions for AgentCore, ECR, VPC, IAM, and optionally KVS
- **LiveKit Cloud account** (or self-hosted server) — [cloud.livekit.io](https://cloud.livekit.io)
- **Python 3.10+**
- **Docker** with [buildx](https://docs.docker.com/buildx/working-with-buildx/) for ARM64 builds
- **AWS CLI** configured with credentials

## Requirements

| Requirement | Detail |
|---|---|
| AgentCore network mode | **VPC** (required for UDP egress) |
| VPC | Private subnets + NAT Gateway + Internet Gateway |
| TURN server | KVS Managed TURN or third-party (Cloudflare, Twilio, metered.ca) |
| Container architecture | `linux/arm64` (required by AgentCore) |

### Why VPC mode?

AgentCore supports `PUBLIC` and `VPC` network modes. LiveKit agents need **VPC mode** because WebRTC media transport uses UDP, and only VPC mode with a NAT Gateway provides outbound UDP connectivity.

## TURN server options

The agent runs behind a NAT, so a TURN server is needed for WebRTC NAT traversal. Two options are supported:

### Option A: KVS Managed TURN (AWS-native)

Amazon Kinesis Video Streams provides managed TURN via the [GetIceServerConfig](https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/API_signaling_GetIceServerConfig.html) API. Credentials are temporary and auto-rotated. The `kvs_turn.py` module handles the full flow.

**Tradeoffs:**
- Requires a KVS signaling channel ($0.03/month each) even though signaling goes through LiveKit
- `GetIceServerConfig` is rate-limited to 5 TPS per channel
- For >100K sessions/month, evaluate a channel pooling strategy or use third-party TURN
- No PrivateLink — VPC still needs internet egress for KVS TURN endpoints

### Option B: Third-party TURN

Static credentials from [Cloudflare TURN](https://developers.cloudflare.com/calls/turn/), [Twilio](https://www.twilio.com/docs/stun-turn), or [metered.ca](https://www.metered.ca/stun-turn) configured via environment variables. TCP TURN recommended for VPC.

### Choosing between options

| Factor | KVS Managed TURN | Third-party TURN |
|---|---|---|
| Best for | AWS-centric deployments | Simplicity, high volume |
| Setup | Moderate (signaling channel + API) | Low (env vars) |
| Credentials | Auto-rotating | Manual or provider-managed |
| Cost (<100K sessions/mo) | ~$0.03/month | Varies by provider |
| Cost (>100K sessions/mo) | Needs pooling strategy | Predictable |

## Setup

### 1. Configure VPC

Create a VPC with private subnets, a NAT Gateway, and an Internet Gateway. If you already have a VPC with internet access, you can reuse it.

```bash
# Create VPC
VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
  --query 'Vpc.VpcId' --output text)
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames

# Create subnets (two AZs for high availability)
PRIVATE_SUBNET_1=$(aws ec2 create-subnet --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 --availability-zone us-west-2a \
  --query 'Subnet.SubnetId' --output text)

PRIVATE_SUBNET_2=$(aws ec2 create-subnet --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 --availability-zone us-west-2b \
  --query 'Subnet.SubnetId' --output text)

PUBLIC_SUBNET=$(aws ec2 create-subnet --vpc-id $VPC_ID \
  --cidr-block 10.0.3.0/24 --availability-zone us-west-2a \
  --query 'Subnet.SubnetId' --output text)

# Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway \
  --query 'InternetGateway.InternetGatewayId' --output text)
aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID

# NAT Gateway
EIP_ALLOC=$(aws ec2 allocate-address --domain vpc --query 'AllocationId' --output text)
NAT_GW_ID=$(aws ec2 create-nat-gateway --subnet-id $PUBLIC_SUBNET \
  --allocation-id $EIP_ALLOC --query 'NatGateway.NatGatewayId' --output text)
aws ec2 wait nat-gateway-available --nat-gateway-ids $NAT_GW_ID

# Route tables
PUBLIC_RT=$(aws ec2 create-route-table --vpc-id $VPC_ID \
  --query 'RouteTable.RouteTableId' --output text)
aws ec2 create-route --route-table-id $PUBLIC_RT \
  --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
aws ec2 associate-route-table --route-table-id $PUBLIC_RT --subnet-id $PUBLIC_SUBNET

PRIVATE_RT=$(aws ec2 create-route-table --vpc-id $VPC_ID \
  --query 'RouteTable.RouteTableId' --output text)
aws ec2 create-route --route-table-id $PRIVATE_RT \
  --destination-cidr-block 0.0.0.0/0 --nat-gateway-id $NAT_GW_ID
aws ec2 associate-route-table --route-table-id $PRIVATE_RT --subnet-id $PRIVATE_SUBNET_1
aws ec2 associate-route-table --route-table-id $PRIVATE_RT --subnet-id $PRIVATE_SUBNET_2

# Security group
SG_ID=$(aws ec2 create-security-group --group-name agentcore-agent-sg \
  --description "LiveKit agent on AgentCore" --vpc-id $VPC_ID \
  --query 'GroupId' --output text)
```

> Subnets must be in [supported Availability Zones](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-vpc.html). Verify with: `aws ec2 describe-subnets --subnet-ids <id> --query 'Subnets[0].AvailabilityZoneId'`

### 2. Configure IAM

Create an IAM role for AgentCore Runtime with:
- `BedrockAgentCoreFullAccess` managed policy
- ECR image pull permissions
- Trust relationship for `bedrock-agentcore.amazonaws.com`

If using KVS Managed TURN, add:

```json
{
    "Effect": "Allow",
    "Action": [
        "kinesisvideo:DescribeSignalingChannel",
        "kinesisvideo:CreateSignalingChannel",
        "kinesisvideo:GetSignalingChannelEndpoint",
        "kinesisvideo:GetIceServerConfig"
    ],
    "Resource": "arn:aws:kinesisvideo:us-west-2:*:channel/livekit-agent-turn/*"
}
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
- LiveKit connection: `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`
- AWS credentials: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- TURN provider: set `TURN_PROVIDER=kvs` or `TURN_PROVIDER=static` and fill in the corresponding variables

### 4. Test locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python agent.py download-files
python agent.py console    # terminal-only test
python agent.py dev        # connects to LiveKit
```

### 5. Build and push to ECR

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=us-west-2

aws ecr create-repository --repository-name livekit-agentcore-agent --region $AWS_REGION

aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin \
  ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

docker buildx build --platform linux/arm64 \
  -t ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/livekit-agentcore-agent:latest \
  --push .
```

### 6. Deploy to AgentCore Runtime

```bash
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export SUBNET_IDS=subnet-XXXXX,subnet-YYYYY
export SECURITY_GROUP_IDS=sg-ZZZZZ
export ROLE_ARN=arn:aws:iam::${AWS_ACCOUNT_ID}:role/AgentCoreRuntimeRole

python deploy.py
```

Save the ARN printed by the script.

### 7. Invoke the agent

```python
import boto3, json

client = boto3.client("bedrock-agentcore", region_name="us-west-2")
response = client.invoke_agent_runtime(
    agentRuntimeArn="<your-runtime-arn>",
    runtimeSessionId="session-" + "a" * 30,
    payload=json.dumps({"action": "start"}),
    qualifier="DEFAULT",
)
print(json.loads(response["response"].read()))
```

Open the [LiveKit Playground](https://agents-playground.livekit.io/) to talk to the agent.

## Monitoring

```bash
aws logs tail /aws/bedrock-agentcore/runtimes/<runtime-id>-DEFAULT --follow
```

## Cleanup

```bash
# Delete runtime
python -c "
import boto3
boto3.client('bedrock-agentcore-control', region_name='us-west-2').delete_agent_runtime(agentRuntimeId='<runtime-id>')
print('Deleted')
"

# Delete ECR repo
aws ecr delete-repository --repository-name livekit-agentcore-agent --region us-west-2 --force

# If using KVS TURN, delete signaling channel
aws kinesisvideo delete-signaling-channel --channel-arn <channel-arn> --region us-west-2
```

Don't forget to clean up VPC resources (NAT Gateway, Elastic IP, etc.) to avoid ongoing charges.

## Files

| File | Description |
|---|---|
| `agent.py` | LiveKit agent with TURN configuration (KVS + static) |
| `kvs_turn.py` | KVS Managed TURN helper (GetIceServerConfig flow) |
| `deploy.py` | Deployment script using boto3 |
| `Dockerfile` | ARM64 container for AgentCore |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template |

## Resources

- [AgentCore Runtime docs](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)
- [AgentCore VPC configuration](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-vpc.html)
- [KVS GetIceServerConfig API](https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/API_signaling_GetIceServerConfig.html)
- [LiveKit Agents docs](https://docs.livekit.io/agents/)
- [LiveKit AWS plugin](https://docs.livekit.io/agents/integrations/aws.md)
- [LiveKit self-hosted deployments](https://docs.livekit.io/deploy/custom/deployments.md)
