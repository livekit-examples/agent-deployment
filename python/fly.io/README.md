# Fly.io LiveKit Agent Deployment Example

This directory demonstrates how to deploy the `agent-example` to a fly.io environment. 

Deployment configuration lives mostly in the `fly.toml` file. Documentation for chosen configuration can be found as comments in-line in that file.

The `scripts` directory contains scripts for the common deployment-lifecycle commands.

## Getting Started

### Install the `fly` command-line interface:

https://fly.io/docs/flyctl/install/

### Authenticate with Fly.io

```bash
fly auth login
```

### Create your app
```bash
fly app create python-agent-example
```

### Create secrets
```bash
fly secrets set --app python-agent-example \
LIVEKIT_URL="wss://your-url-from-livekit-cloud-dashboard.livekit.cloud" \
LIVEKIT_API_KEY="api-key-from-livekit-cloud-dashboard" \
LIVEKIT_API_SECRET="api-secret-from-livekit-cloud-dashboard"
```

These secrets will be available as environment variables in the worker process. You will likely need to add additional secrets here as well depending on your agent, for example, `OPENAI_API_KEY`.

### Deploy your app
```bash
fly deploy -c fly.toml 
```

### Scaling

Scaling can be done manually using fly commands:

```bash
fly scale count --app python-agent-example
```

For autoscaling on fly, we defer to their guide: https://fly.io/docs/launch/autoscale-by-metric/