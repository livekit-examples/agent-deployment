# Modal LiveKit Agents Deployment Example

This directory contains a [LiveKit](https://livekit.com) voice AI agent deployed on [Modal](https://www.modal.com?utm_source=partner&utm_medium=github&utm_campaign=livekit), a serverless platform for running Python applications. The agent is based on [LiveKit's `agent-starter-python` project](https://github.com/livekit-examples/agent-starter-python)

## Getting Started

Before deploying, ensure you have:

- **Modal Account**: Sign up at [modal.com](https://www.modal.com?utm_source=partner&utm_medium=github&utm_campaign=livekit) and get $30/month of free compute.
- **LiveKit Account**: Set up a [LiveKit](https://livekit.com) account
- **API Keys**:
    - [OpenAI](https://openai.com)
    - [Cartesia](https://cartesia.com)
    - [Deepgram](https://deepgram.com)

### Install Dependencies

The project uses `uv` for dependency management. That said, the only local dependency you need is `modal`. To setup the environment, run

```bash
uv sync
```

### Authenticate Modal

```bash
modal setup
```

### Set Up Secrets on Modal

**Using the Modal dashboard**

Navigate to the Secrets section in the Modal dashboard and add the following secrets:

- `LIVEKIT_URL` - Your LiveKit WebRTC server URL
- `LIVEKIT_API_KEY` - API key for authenticating LiveKit requests
- `LIVEKIT_API_SECRET` - API secret for LiveKit authentication
- `OPENAI_API_KEY` - API key for OpenAI's GPT-based processing
- `CARTESIA_API_KEY` - API key for Cartesia's TTS services
- `DEEPGRAM_API_KEY` - API key for Deepgram's STT services

You can find your LiveKit URL and API keys under **Settings** > **Project** and **Settings** > **Keys** in the LiveKit dashboard.

![Modal Secrets](https://modal-cdn.com/cdnbot/modal-livekit-secretsndip6awa_78ed94b0.webp)

**Using the Modal CLI:**

```bash
modal secret create livekit-voice-agent \
  --env LIVEKIT_URL=your_livekit_url \
  --env LIVEKIT_API_KEY=your_api_key \
  --env LIVEKIT_API_SECRET=your_api_secret \
  --env OPENAI_API_KEY=your_openai_key \
  --env DEEPGRAM_API_KEY=your_deepgram_key \
  --env CARTESIA_API_KEY=your_cartesia_key
```

Once added, you can reference these secrets in your Modal functions.

### Configure LiveKit Webhooks

In your LiveKit project dashboard, create a new Webhook using the URL created when you deploy your Modal app. This URL will be printed to stdout and is also available in your Modal dashboard. It will look something like the URL in the screenshot below:

![settings webhooks](https://modal-cdn.com/cdnbot/livekit-webhooksiceyins6_203427cc.webp)

## Deployment

Run the following command to deploy your Modal app. 
```bash
modal deploy -m src.server
```
You can interact with your agent using the hosted [LiveKit Agent Playground](https://docs.livekit.io/agents/start/playground/). When you connect to the room, the `room_started` webhook event will spawn your agent to the room.

## Developing

During development in case be helpful to launch the application using
```
modal serve -m src.server
```
which will reload the app when changes are made to the source code.

## Testing

### Test the Agent

Use the following command to launch your app remotely and execute the tests using `pytest`:
```
modal run -m src.server
```

### Test the Webhook Endpoint

Test the webhook endpoint with a sample LiveKit event from the command line:

```bash
curl -X POST {MODAL_AGENT_WEB_ENDPOINT_URL} \
  -H "Authorization: Bearer your_livekit_token" \
  -H "Content-Type: application/json" \
  -d '{"event": "room_started", "room": {"name": "test-room"}}'
```

Or you can trigger Webhook events from LiveKit Webhooks setting page (the same place you created the new Webhook).

