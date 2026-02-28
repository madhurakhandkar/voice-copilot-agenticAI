import boto3
import pygame
import time
import wave


polly = boto3.client("polly", region_name="us-east-1")

def speak(content):
    response = polly.synthesize_speech(
        Text=content,
        OutputFormat="pcm",
        VoiceId="Matthew"
    )

    # Save as WAV properly
    with wave.open("speech.wav", "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(response["AudioStream"].read())

    # Play it
    pygame.mixer.init()
    pygame.mixer.music.load("speech.wav")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.1)