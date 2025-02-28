# from base64 import standard_b64encode
import speech_recognition as sr
import pyttsx3
import sounddevice
from ollama import AsyncClient
from gtts import gTTS

# import pyaudio
from io import BytesIO
import pygame

from pydub import AudioSegment
import asyncio

from loading_anim import Loader

# Initialize the recognizer
r = sr.Recognizer()
pygame.init()
pygame.mixer.init()

num_of_chunks = 0
text_chunks = ""

# engine = pyttsx3.init()
# engine.setProperty("rate", 100)

# Constants for PyAudio
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 44100  # Sample rate
# CHUNK = 1024  # Buffer size


def record_text():
    loader = Loader("Recording...", end="Done Recording!").start()
    # Loop in case of errors
    while 1:
        try:
            # use the microphone as source for input
            with sr.Microphone() as source2:
                # Prepare recognizer to receive input
                r.adjust_for_ambient_noise(source2, duration=0.2)
                # listens for the user's input
                audio2 = r.listen(source2)

                MyText = r.recognize_google(audio2)

                loader.stop()

                return MyText

        except sr.RequestError as e:
            print("\nCould not request results; {0}".format(e))
        except sr.UnknownValueError:
            print("\nunknown error occurred")


async def get_chat_response(text):
    async for stream in await AsyncClient().chat(
        model="llama3.2", messages=[{"role": "user", "content": text}], stream=True
    ):
        return stream

    # audio_stream = None
    # py_audio = None
    #
    # text_chunks "= ""
    # num_of_chunks = 0
    # tasks = []

    # for chunk in stream:
    # num_of_chunks += 1
    # print(chunk["message"]["content"], end="", flush=True)
    # text_chunks += chunk["message"]["content"]

    #     if num_of_chunks % 40 == 0:
    #         audio_segment = create_speech_audio_segment(text_chunks)
    #
    #         if not audio_stream or not py_audio:
    #             initialized_py_audio, initialized_audio_stream = open_audio_stream(
    #                 audio_segment.frame_rate
    #             )
    #
    #             audio_stream = initialized_audio_stream
    #             py_audio = initialized_py_audio
    #
    #         play_audio_stream(audio_segment, audio_stream)
    #
    #         text_chunks = ""
    #
    # stop_stream(audio_stream, py_audio)


async def print_chat(chunk):
    print(chunk["message"]["content"], end="", flush=True)
    global text_chunks
    text_chunks += chunk["message"]["content"]


async def speak_chat(chunk):
    global text_chunks

    text = chunk["message"]["content"] if text_chunks == "" else text_chunks
    if num_of_chunks % 20 == 0:
        try:
            fp = BytesIO()
            wav_fp = BytesIO()
            tts = gTTS(text=text)
            tts.write_to_fp(fp)
            fp.seek(0)
            sound = AudioSegment.from_file(fp)
            wav_fp = sound.export(fp, format="wav")
            pygame.mixer.music.load(wav_fp)
            pygame.mixer.music.play()
            while pygame.mixer.get_busy():
                await asyncio.sleep(0.1)
            text_chunks = ""
        except Exception:
            return


async def main():
    while True:
        text = record_text()

        if text in ["quit", "exit", "stop"]:
            exit()

        chat_response = await get_chat_response(text)

        tasks = []

        global num_of_chunks

        async with asyncio.TaskGroup() as tg:
            for chunk in chat_response:
                num_of_chunks += 1
                task1 = tg.create_task(print_chat(chunk))
                task2 = tg.create_task(speak_chat(chunk))
                tasks.append(task1)
                tasks.append(task2)

        print("\nWrote prompt")
        tasks.clear()


asyncio.run(main())

## text to speech
# from gtts import gTTS
#
#
# def speak(text):
#     # Create a synthesizer object
#     audio = gTTS(text=text, lang="en")
#     # Save the audio file to a temporary location
#     voice_file = "voice.mp3"
#     audio.save(voice_file)
#
#
# # Get user input and convert it to speech
# text = input("Please enter some text: ")
# speak(text)


## Speech to file
# import pyaudio
# import wave
#
#
# CHUNK = 1024
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 44100
# p = pyaudio.PyAudio()
# stream = p.open(
#     format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
# )
#
# print("start recording...")
#
# frames = []
# seconds = 10
# for i in range(0, int(RATE / CHUNK * seconds)):
#     data = stream.read(CHUNK)
#     frames.append(data)
#
# print("recording stopped")
#
# stream.stop_stream()
# stream.close()
# p.terminate()
#
# wf = wave.open("output.wav", "wb")
# wf.setnchannels(CHANNELS)
# wf.setsampwidth(p.get_sample_size(FORMAT))
# wf.setframerate(RATE)
# wf.writeframes(b"".join(frames))
# wf.close()


# Commented functions
# def create_speech_audio_segment(text):
#     print(f"Creating google audio speech stream: {text}")
#
#     audio_stream = BytesIO()
#     tts = gTTS(text=text, lang="en")
#     tts.write_to_fp(audio_stream)
#     audio_stream.seek(0)
#
#     audio_segment = AudioSegment.from_file(
#         audio_stream, format="mp3"
#     )  # Change for"mat as needed
#
#     return audio_segment
#
#
# def open_audio_stream(audio_frame_rate):
#     print("is opening audio stream")
#     # Initialize PyAudio
#     p = pyaudio.PyAudio()
#
#     # Open a stream with the appropriate settings
#     stream = p.open(
#         format=pya"udio.paInt16, channels=1, rate=audio_frame_rate, output=True
#     )
#
#     return (p, stream)
#
#
# def play_audio_stream(audio_segment, audio_stream):
#     print("is playin the audio stream")
#     chunk_size = 1024
#     for i in range(0, len(audio_segment.raw_data), chunk_size):
#         chunk = audio_segment.raw_data[i : i + chunk_size]
#         audio_stream.write(chunk)
#
#
# def stop_stream(stream, py_audio):
#     print("is stopping the stream")
#     stream.stop_stream()
#     stream.close()
#     py_audio.terminate()


## Speech to text
