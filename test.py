import ollama
from gtts import gTTS
import os
import re
import asyncio
import speech_recognition as sr
import threading
import sounddevice as sd

exclude_chars = ["`", "*", "#"]
stop_program = False
model_processing = False


def listen_for_exit():
    """Listen for the words 'quit' or 'exit' from the microphone to terminate the program."""
    global stop_program
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        # print(
        #     "Voice command listener activated. Say 'quit' or 'exit' to terminate the program."
        # )

    while not stop_program:
        try:
            with mic as source:
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
            command = recognizer.recognize_google(audio).lower()
            if command in ["quit", "exit"]:
                stop_program = True
                print("Exit command received. Terminating program...")
                exit()
                break
        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            break


async def speak_text(text, exclude_chars=None):
    """Use gTTS to speak the given text without saving to a file."""
    if exclude_chars:
        # Create a regex pattern to match any of the excluded characters or sequences
        pattern = f"[{re.escape(''.join(exclude_chars))}]"
        text = re.sub(pattern, "", text)
    tts = gTTS(text)
    tts.save("temp.mp3")
    os.system("mpg123 -q temp.mp3")
    os.remove("temp.mp3")


def listen_for_speech():
    """Continuously listen for user speech and update the response_text variable when model is not processing."""
    global response_text, stop_program, model_processing
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Speak your prompt.")

    while not stop_program:
        if not model_processing:
            try:
                with mic as source:
                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
                spoken_text = recognizer.recognize_google(audio)
                response_text = spoken_text
                print(f"You said: {spoken_text}")
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
                break


async def stream_and_speak(exclude_chars):
    """Stream text from Ollama and speak it asynchronously."""
    global stop_program, response_text, model_processing

    # Process the response with streaming enabled
    print("Response:")
    response_text = ""
    try:
        while not stop_program:
            if response_text:
                prompt = response_text
                response_text = ""  # Clear after processing
                response_full_text = ""

                model_processing = True

                async for response in ollama.chat(
                    model="llama3.2",
                    stream=True,
                    messages=[{"role": "user", "content": prompt}],
                ):
                    if stop_program:
                        break
                    text_chunk = response["message"]["content"]
                    response_full_text += text_chunk
                    print(text_chunk, end="", flush=True)
                    await speak_text(text_chunk, exclude_chars=exclude_chars)
                print()  # New line after the full response
                model_processing = False
    except Exception as e:
        print(f"An error occurred: {e}")
        model_processing = False


async def main():
    global stop_program

    # Start the voice command listener in a separate thread
    exit_listener_thread = threading.Thread(target=listen_for_exit)
    exit_listener_thread.start()

    speech_listener_thread = threading.Thread(target=listen_for_speech)
    speech_listener_thread.start()

    # Get user input
    # user_input = input("Enter your text: ")

    # Configure Ollama to enable streaming
    # prompt = user_input

    # Stream and speak the response
    await stream_and_speak(exclude_chars)

    # Wait for the listener thread to finish
    stop_program = True
    exit_listener_thread.join()
    speech_listener_thread.join()


if __name__ == "__main__":
    asyncio.run(main())
