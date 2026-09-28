import os
import subprocess
import tempfile
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = "gemini-3.5-transcribe"


def convert_to_wav(
    input_path: str,
    output_path: str,
) -> None:
    """
    Convert browser-recorded WebM/Opus audio to
    mono 16 kHz PCM WAV using FFmpeg.
    """

    command = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        output_path,
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg audio conversion failed:\n"
            f"{result.stderr}"
        )


def transcribe_audio(
    audio_bytes: bytes,
    mime_type: str,
) -> str:

    input_path = None
    wav_path = None
    audio_file = None

    try:
        # --------------------------------------------------
        # 1. Save browser audio
        # --------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".webm",
        ) as input_file:

            input_file.write(audio_bytes)
            input_path = input_file.name

        print(
            "[Voice Transcription] "
            f"Received audio: {len(audio_bytes)} bytes"
        )

        print(
            "[Voice Transcription] "
            f"Browser MIME type: {mime_type}"
        )

        # --------------------------------------------------
        # 2. Convert WebM/Opus -> WAV
        # --------------------------------------------------

        wav_path = tempfile.mktemp(
            suffix=".wav"
        )

        print(
            "[Voice Transcription] "
            "Converting WebM/Opus -> WAV..."
        )

        convert_to_wav(
            input_path=input_path,
            output_path=wav_path,
        )

        wav_size = os.path.getsize(wav_path)

        print(
            "[Voice Transcription] "
            f"WAV created: {wav_size} bytes"
        )

        # --------------------------------------------------
        # 3. Upload WAV to Gemini
        # --------------------------------------------------

        print(
            "[Voice Transcription] "
            "Uploading WAV to Gemini..."
        )

        audio_file = client.files.upload(
            file=wav_path
        )

        print(
            "[Voice Transcription] "
            f"Uploaded file: {audio_file.name}"
        )

        # --------------------------------------------------
        # 4. Wait for Gemini file processing
        # --------------------------------------------------

        max_attempts = 30

        for attempt in range(max_attempts):

            audio_file = client.files.get(
                name=audio_file.name
            )

            state = getattr(
                audio_file.state,
                "name",
                None,
            )

            print(
                "[Voice Transcription] "
                f"File state: {state}"
            )

            if state == "ACTIVE":
                break

            if state == "FAILED":

                error_message = getattr(
                    audio_file,
                    "error",
                    None,
                )

                raise RuntimeError(
                    "Gemini failed to process the WAV file. "
                    f"File error: {error_message}"
                )

            time.sleep(1)

        else:
            raise TimeoutError(
                "Timed out waiting for Gemini "
                "to process the audio file."
            )

        # --------------------------------------------------
        # 5. Transcribe
        # --------------------------------------------------

        print(
            "[Voice Transcription] "
            "Sending WAV to transcription model..."
        )

        response = client.models.generate_content(
            model=MODEL,
            contents=[audio_file],
        )

        print(
            "[Voice Transcription] "
            f"Response: {response}"
        )

        transcript = ""

        for candidate in response.candidates or []:
            content = candidate.content

            if not content:
                continue

            for part in content.parts or []:

                # Gemini 3.5 Transcribe can return the
                # transcription as an audio_transcription
                # structured response part.
                audio_transcription = getattr(
                    part,
                    "audio_transcription",
                    None,
                )

                if audio_transcription:
                    transcript = (
                        getattr(audio_transcription, "text", "")
                        or ""
                    ).strip()

                    if transcript:
                        break

                # Fallback for normal text responses
                text = getattr(
                    part,
                    "text",
                    None,
                )

                if text:
                    transcript = text.strip()
                    break

            if transcript:
                break

        if not transcript:
            raise ValueError(
                "Gemini returned a response, "
                "but no transcription text was found."
            )

        print(
            "[Voice Transcription] "
            f"Transcript: {transcript}"
        )

        return transcript

        print(
            "[Voice Transcription] "
            f"Transcript: {transcript}"
        )

        return transcript

    finally:

        if input_path and os.path.exists(input_path):
            os.remove(input_path)

        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)