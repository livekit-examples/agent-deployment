# Render.com LiveKit Agent Deployment Example

This directory demonstrates how to deploy a LiveKit agent to Render.com. 

Deployment configuration lives mostly in the `render.yaml` file. Documentation for chosen configuration can be found as comments in-line in that file.

## Getting Started

### Create environment group

In your (Render.com dashboard)[dashboard.render.com] you'll need to create an environment group to store LiveKit secrets.
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