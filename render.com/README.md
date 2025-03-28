# Render.com LiveKit Agents Deployment Example

This directory demonstrates how to deploy LiveKit Agents to [Render.com](https://render.com).

You also need a working agents app and Dockerfile. See the examples for [Python](/python-agent-example-app) or [Node.js](/node-agent-example-docker) if necessary.

## Getting Started

### Copy the `render.yaml` file

Copy the `render.yaml` file to the root of your project (wherever your `Dockerfile` is located).

### Create environment group

In your [Render.com dashboard](https://dashboard.render.com) you'll need to create an environment group to store LiveKit secrets.
Create an environment group with the name `agent-example-env-group` with the variables:
```bash
LIVEKIT_URL=wss://your-livekit-url.livekit.cloud
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret
```

### Launch your service

To launch your service, create a blueprint in your Render.com dashboard
pointing to your repo.

This will find the `render.yaml` file and apply it's changes. You can use
the provided render.yaml here as reference. Comments have been placed where
you're likely to need your own configuration.
