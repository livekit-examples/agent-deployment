"""LiveKit voice agent for Amazon Bedrock AgentCore Runtime.

This is a standard LiveKit voice agent with ICE/TURN configuration
added for VPC deployment. It extends the pattern in the shared
python-agent-example-app/ with two AgentCore-specific changes:
    1. TURN server setup (required for NAT traversal in VPC)
    2. AWS voice pipeline (Transcribe STT + Nova Lite LLM + Polly TTS)

TURN options (set via TURN_PROVIDER env var):
    "kvs"    — AWS-native KVS Managed TURN (GetIceServerConfig API)
    "static" — Third-party TURN with static credentials (default)

Usage:
    Local:      python agent.py console | python agent.py dev
    Production: python agent.py start
"""

import logging
import os

from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import Agent, AgentServer, AgentSession
from livekit.plugins import aws, silero

from kvs_turn import get_kvs_ice_servers

load_dotenv()

logger = logging.getLogger("agentcore-livekit-agent")


class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "You are a helpful voice assistant running on "
                "Amazon Bedrock AgentCore Runtime. Your output will "
                "be spoken aloud, so keep responses concise and "
                "conversational. Avoid special characters, emojis, "
                "or formatting that can't be spoken naturally."
            ),
        )

    async def on_enter(self):
        await self.session.generate_reply(
            instructions="Greet the user and offer your assistance."
        )


def build_ice_servers() -> list[rtc.IceServer]:
    """Build ICE servers from KVS or static env var config.

    TURN is required when running behind a NAT Gateway in a VPC.
    """
    provider = os.getenv("TURN_PROVIDER", "static").lower()

    if provider == "kvs":
        logger.info("Using KVS Managed TURN")
        return get_kvs_ice_servers()

    turn_urls = os.getenv("TURN_SERVER_URLS", "")
    if not turn_urls:
        logger.warning(
            "No TURN server configured. Set TURN_PROVIDER=kvs or "
            "set TURN_SERVER_URLS/USERNAME/CREDENTIAL."
        )
        return []

    urls = [u.strip() for u in turn_urls.split(",") if u.strip()]
    logger.info("Using static TURN config with %d URL(s)", len(urls))

    return [
        rtc.IceServer(
            urls=urls,
            username=os.getenv("TURN_SERVER_USERNAME", ""),
            credential=os.getenv("TURN_SERVER_CREDENTIAL", ""),
        )
    ]


server = AgentServer()


@server.rtc_session(agent_name="agentcore-agent")
async def entrypoint(ctx: agents.JobContext):
    ice_servers = build_ice_servers()
    await ctx.connect(rtc_config=rtc.RtcConfiguration(ice_servers=ice_servers))

    session = AgentSession(
        stt=aws.STT(language="en-US"),
        llm=aws.LLM(model="us.amazon.nova-2-lite-v1:0"),
        tts=aws.TTS(voice="Ruth", speech_engine="generative", language="en-US"),
        vad=silero.VAD.load(),
    )

    await session.start(room=ctx.room, agent=Assistant())


if __name__ == "__main__":
    agents.cli.run_app(server)
