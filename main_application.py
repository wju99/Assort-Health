import asyncio
import signal
from pydantic_settings import BaseSettings, SettingsConfigDict
from vocode.helpers import create_streaming_microphone_input_and_speaker_output
from vocode.logging import configure_pretty_logging
from vocode.streaming.streaming_conversation import StreamingConversation
from vocode.streaming.synthesizer.azure_synthesizer import AzureSynthesizer
from vocode.streaming.transcriber.deepgram_transcriber import DeepgramTranscriber
from vocode.streaming.models.transcriber import DeepgramTranscriberConfig, PunctuationEndpointingConfig
from vocode.streaming.models.synthesizer import AzureSynthesizerConfig
from vocode.streaming.models.message import BaseMessage

from medical_appointment_agent import MedicalAppointmentAgent, MedicalAppointmentAgentConfig

configure_pretty_logging()

class Settings(BaseSettings):
    openai_api_key: str
    azure_speech_key: str
    deepgram_api_key: str
    azure_speech_region: str = "eastus"
    twilio_account_sid: str
    twilio_auth_token: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

async def main():
    microphone_input, speaker_output = create_streaming_microphone_input_and_speaker_output(
        use_default_devices=False,
    )

    conversation = StreamingConversation(
        output_device=speaker_output,
        transcriber=DeepgramTranscriber(
            DeepgramTranscriberConfig.from_input_device(
                microphone_input,
                endpointing_config=PunctuationEndpointingConfig(),
                api_key=settings.deepgram_api_key,
            ),
        ),
        agent=MedicalAppointmentAgent(
            MedicalAppointmentAgentConfig(
                openai_api_key=settings.openai_api_key,
                initial_message=BaseMessage(text="Welcome to our medical appointment service. How can I assist you today?"),
                prompt_preamble="You are a medical appointment scheduling assistant. Be professional and courteous.",
            )
        ),
        synthesizer=AzureSynthesizer(
            AzureSynthesizerConfig.from_output_device(speaker_output),
            azure_speech_key=settings.azure_speech_key,
            azure_speech_region=settings.azure_speech_region,
        ),
    )

    await conversation.start()
    print("Conversation started, press Ctrl+C to end")
    signal.signal(signal.SIGINT, lambda *args: asyncio.create_task(conversation.terminate()))

    while conversation.is_active():
        chunk = await microphone_input.get_audio()
        print("Received audio chunk")
        conversation.receive_audio(chunk)
        print("Processed audio chunk")

    print("Conversation ended")

if __name__ == "__main__":
    asyncio.run(main())
