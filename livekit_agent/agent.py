import asyncio
import os
from livekit import rtc
from livekit.agents import JobContext, WorkerOptions, cli, AutoSubscribe
from livekit.plugins import silero

from dotenv import load_dotenv
load_dotenv()


# Environment variables
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://frontdesk-g6uqpour.livekit.cloud")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

print(f"🔑 API Key: {LIVEKIT_API_KEY[:15] if LIVEKIT_API_KEY else 'NOT SET'}...")
print(f"🌐 LiveKit URL: {LIVEKIT_URL}")


async def entrypoint(ctx: JobContext):
    """
    Runs when a participant joins the room.
    This agent listens, performs simple logic, and replies via voice.
    """
    print(f"🎙️ Agent job started for room: {ctx.room.name}")
    
    # Connect to the room
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    print(f"✅ Agent connected to room: {ctx.room.name}")

    # Initialize STT and TTS engines
    stt = None
    tts = None


    # Track the audio source
    audio_source = rtc.AudioSource(sample_rate=48000, num_channels=1)
    
    # Create audio track for agent's responses
    track = rtc.LocalAudioTrack.create_audio_track("agent-voice", audio_source)
    options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
    
    # Publish the agent's audio track
    publication = await ctx.room.local_participant.publish_track(track, options)
    print(f"✅ Agent audio track published: {publication.sid}")

    # Function to process user speech text
    async def handle_text(text: str):
        print(f"👤 User said: {text}")

        # Simple rule-based response
        text_lower = text.lower()
        if "time" in text_lower or "open" in text_lower:
            response = "Our salon is open from 9 AM to 7 PM every day."
        elif "location" in text_lower or "where" in text_lower:
            response = "We are located at 123 Salon Street, near City Mall."
        elif "hello" in text_lower or "hi" in text_lower:
            response = "Hello! Welcome to our salon. How can I help you today?"
        else:
            response = "Let me check with my supervisor and get back to you."

        print(f"🤖 Responding: {response}")
        
        # Generate TTS audio
        async for audio_frame in tts.synthesize(response):
            await audio_source.capture_frame(audio_frame)

    # Listen for participants joining
    @ctx.room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant):
        print(f"👤 Participant joined: {participant.identity}")

    # Listen for audio tracks
    @ctx.room.on("track_subscribed")
    def on_track_subscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        print(f"🎧 Track subscribed from {participant.identity}: {track.kind}")
        
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            print(f"🎤 Starting to listen to {participant.identity}")
            audio_stream = rtc.AudioStream(track)
            asyncio.create_task(process_audio_stream(audio_stream))

    async def process_audio_stream(audio_stream: rtc.AudioStream):
        print("🎤 Received audio stream (STT not configured).")
        try:
            async for _ in audio_stream:
                pass
        except Exception as e:
            print(f"❌ Audio processing error: {e}")


    # Subscribe to existing participants' tracks
    for participant in ctx.room.remote_participants.values():
        print(f"👤 Found existing participant: {participant.identity}")
        for publication in participant.track_publications.values():
            if publication.track:
                print(f"🎧 Already has track: {publication.track.kind}")

    print("🎧 Agent is now listening for audio...")
    
    # Keep the agent alive
    await asyncio.Future()


if __name__ == "__main__":
    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        print("❌ ERROR: LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set!")
        exit(1)
    
    print("🚀 Starting LiveKit Agent Worker...")
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET,
            ws_url=LIVEKIT_URL,
        )
    )