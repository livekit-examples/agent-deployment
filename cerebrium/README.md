# Cerebrium.ai LiveKit Agents Deployment Example

This directory demonstrates how to deploy LiveKit Agents to [Cerebrium](https://www.cerebrium.ai) using a sample  `cerebrium.toml` file.

You also need a working agents app and Dockerfile. See the examples for [Python](/python-agent-example-app) or [Node.js](/node-agent-example-docker) if necessary.

## Getting Started

### Create Cerebrium account

If you don't have a Cerebrium account, you can easily signup with the CLI:

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

### Add your cerebrium.toml file

Copy the `cerebrium.toml` file to the root of your project (wherever your `Dockerfile` is located).

### Launch your service

Run the following in your CLI to launch the service

```bash
cerebrium deploy
```

If you need further help extending functionality you can look in the documentation [here](https://docs.cerebrium.ai/cerebrium/getting-started/introduction).