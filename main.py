import asyncio
import os
import logging
from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import deepgram, openai, silero

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def entrypoint(ctx: JobContext):
    logger.info(f"Entrypoint called for room: {ctx.room.name}")
    
    # Create an initial chat context with a system prompt
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are a voice assistant created by LiveKit. Your interface with users will be voice. "
            "You should use short and concise responses, and avoiding usage of unpronounceable punctuation."
        ),
    )

    # Connect to the LiveKit room
    logger.info(f"Connecting to room: {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    logger.info(f"Connected to room: {ctx.room.name}")

    # VoiceAssistant is a class that creates a full conversational AI agent.
    assistant = VoiceAssistant(
        vad=silero.VAD.load(),
        stt=deepgram.STT(),
        llm=openai.LLM(),
        tts=openai.TTS(),
        chat_ctx=initial_ctx,
    )

    # Start the voice assistant with the LiveKit room
    logger.info("Starting voice assistant")
    assistant.start(ctx.room)

    await asyncio.sleep(1)

    # Greets the user with an initial message
    logger.info("Attempting to say greeting")
    await assistant.say("Hey, how can I help you today?", allow_interruptions=True)
    logger.info("Greeting sent")

    # Keep the agent running
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    logger.info("Starting LiveKit AI Agent")
    # Initialize the worker with the entrypoint
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))