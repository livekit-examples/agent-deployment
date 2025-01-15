# Cerebrium.ai LiveKit Agent Deployment Example

This directory demonstrates how to deploy a LiveKit agent to [Cerebrium](https://www.cerebrium.ai)

Deployment configuration lives mostly in the `cerebrium.toml` file. Documentation for chosen configuration can be found as comments in-line in that file.

## Getting Started

### Create Cerebrium account

If you don’t have a Cerebrium account, you can run the following in your cli:

```bash
pip install cerebrium --upgrade
cerebrium login
```

### Add Secrets to Cerebrium

In your [Cerebrium dashboard](https://dashboard.cerebrium.ai) you'll need to create add the following LiveKit secrets.
```bash
LIVEKIT_URL=wss://your-livekit-url.livekit.cloud
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret
```

### Launch your service

Run the following in your CLI to launch the service

```bash
cerebrium deploy
```

Make sure you run this command with the cerebrium.toml in the same folder as the python-agent-example-app.
If you need further help extending functionality you can look in the documentation [here](https://docs.cerebrium.ai/cerebrium/getting-started/introduction).