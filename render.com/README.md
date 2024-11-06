# Render.com LiveKit Agent Deployment Example

This directory demonstrates how to deploy the `agent-example` to a fly.io environment. 

Deployment configuration lives mostly in the `fly.toml` file. Documentation for chosen configuration can be found as comments in-line in that file.

## Getting Started

### Copy Example App w/ Dockerfile 

This guide assumes the app and relevant files exist in this directory. 
We provide an example app in the `python-agent-implementation` directory at the top-level of this repo.

```bash
cp ../python-agent-example-app/* .
cp ../python-agent-example-app/.dockerignore .
```

### Create environment variables

On your render.com dashboard, create an Environment Group called `AgentExampleEnvironmentGroup`.

Add the following environment variables:

```
LIVEKIT_URL=wss://your-url-from-livekit-cloud-dashboard.livekit.cloud
LIVEKIT_API_KEY="api-key-from-livekit-cloud-dashboard"
LIVEKIT_API_SECRET="api-secret-from-livekit-cloud-dashboard"
```