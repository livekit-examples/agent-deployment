# Render.com LiveKit Agent Deployment Example

This directory demonstrates how to deploy the `agent-example` to a fly.io environment. 

Deployment configuration lives mostly in the `fly.toml` file. Documentation for chosen configuration can be found as comments in-line in that file.

## Getting Started

### Create resources in Render Dashboard

In your render dashboard:
- Create a new project
- In that project create a new `Private Service`
- Connect a GitHub provider and give it access to your repo
- Set the root directory to `python-agent-example-app` (or if using your own repo, the directory containing the Dockerfile)
- Add `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET` environment variables
- Deploy the service
