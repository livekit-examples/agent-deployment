# Render.com LiveKit Agent Deployment Example

Render.com is setup is best configured in your (Render Dashboard)[https://dashboard.render.com]

## Steps

In your render dashboard:
- Create a new project
- In that project create a new `Private Service`
- Connect a GitHub provider and give it access to your repo
- Set the root directory to `python-agent-example-app` (or if using your own repo, the directory containing the Dockerfile)
- Add `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET` environment variables
- Deploy the service
