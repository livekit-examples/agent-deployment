# Fly.io LiveKit Agents Deployment Example

This directory demonstrates how to deploy LiveKit Agents to [fly.io](https://fly.io) using a sample `fly.toml` file.

You also need a working agents app and Dockerfile. See the examples for [Python](/python-agent-example-app) or [Node.js](/node-agent-example-docker) if necessary.


## Getting Started

### Install the `fly` command-line interface:

https://fly.io/docs/flyctl/install/

### Authenticate with Fly.io

```bash
fly auth login
```

### Copy the sample `fly.toml` file

Copy the `fly.toml` file to the root of your project (wherever your `Dockerfile` is located).

### Create your app

Create your app, and use the `fly.toml` file you already have. You can change the name if you'd like, both in the file and in the command below.

```bash
fly app create agent-example
```

### Create secrets

You will need to create secrets for your app. You can do this using the `fly secrets` command.

```bash
fly secrets set --app agent-example \
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
fly scale count --app agent-example
```

For autoscaling on fly, see their guide: https://fly.io/docs/launch/autoscale-by-metric/
