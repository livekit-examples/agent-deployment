import modal

image = (
    modal.Image.debian_slim()

    .uv_pip_install(
        "fastapi",
        "livekit-agents[openai,turn-detector,silero,cartesia,deepgram]",
        "livekit-plugins-noise-cancellation",
        "pytest",
        "pytest-asyncio",
        "ruff",
    )
    .add_local_dir("tests", "/root/tests")
)

app = modal.App("livekit-modal-deployment", image=image)

# Create a persisted dict - the data gets retained between app runs
room_dict = modal.Dict.from_name("room-dict", create_if_missing=True)

with image.imports():
    import asyncio

    from fastapi import FastAPI, Request, Response
    from livekit import api
    from livekit.agents import (
        NOT_GIVEN,
        Agent,
        AgentFalseInterruptionEvent,
        AgentSession,
        JobContext,
        JobProcess,
        MetricsCollectedEvent,
        RoomInputOptions,
        RunContext,
        WorkerOptions,
        cli,
        metrics,
    )
    from livekit.agents.llm import function_tool
    from livekit.plugins import cartesia, deepgram, noise_cancellation, openai, silero
    from livekit.plugins.turn_detector.multilingual import MultilingualModel

    from src.agent import entrypoint, prewarm

@app.cls(
    timeout=3000,
    secrets=[modal.Secret.from_name("livekit-voice-agent")],
    enable_memory_snapshot=True,
    min_containers=1,
)
@modal.concurrent(max_inputs=10)
class LiveKitAgentServer:

    @modal.enter(snap=True)
    def enter(self):
        import subprocess
        print("Downloading files...")
        subprocess.run(["python", "src/server.py", "download-files"], cwd="/root")

    @modal.enter(snap=False)
    def start_agent_server(self):
        import subprocess
        import threading
        print("Starting agent server...")
        def run_dev():
            subprocess.run(["python", "src/server.py", "dev"], cwd="/root")
        thread = threading.Thread(target=run_dev, daemon=True)
        thread.start()

    @modal.asgi_app()
    def webhook_app(self):

        web_app = FastAPI()

        @web_app.post("/")
        async def webhook(request: Request):

            token_verifier = api.TokenVerifier()
            webhook_receiver = api.WebhookReceiver(token_verifier)

            auth_token = request.headers.get("Authorization")
            if not auth_token:
                return Response(status_code=401)

            body = await request.body()
            event = webhook_receiver.receive(body.decode("utf-8"), auth_token)
            print("received event:", event)

            room_name = event.room.name
            event_type = event.event

            # ## check whether the room is already in the room_dict
            if room_name in room_dict and event_type == "room_started":
                print(
                    f"Received web event for room {room_name} that already has a worker running"
                )
                return

            if event_type == "room_started":
                room_dict[room_name] = True
                print(f"Worker for room {room_name} spawned")
                while room_dict[room_name]:
                    await asyncio.sleep(1)

                del room_dict[room_name]

            elif event_type in ["room_finished", "participant_left"]:
                if room_name in room_dict and room_dict[room_name]:
                    room_dict[room_name] = False
                    print(f"Worker for room {room_name} spun down")
                elif room_name not in room_dict:
                    print(f"Worker for room {room_name} not found")
                elif room_name in room_dict and not room_dict[room_name]:
                    print(f"Worker for room {room_name} already spun down")

            return Response(status_code=200)

        return web_app

    @modal.method()
    def run_tests(self):
        import subprocess
        subprocess.run(["pytest"], cwd="/root")


@app.local_entrypoint()
def run_tests():
    LiveKitAgentServer().run_tests.remote()


if __name__ == "__main__":

    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        )
    )