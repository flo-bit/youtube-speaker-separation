import os
import json
from pytube import YouTube
from pytube.innertube import _default_clients

from pydub import AudioSegment
import replicate
from dotenv import load_dotenv

import argparse

# Load environment variables from .env file
load_dotenv()

# fix for youtube downloader
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]


def download_video(video):
    yt = YouTube(video)

    print("Step 1/3. Downloading " + yt.title + "...")
    # extract only audio
    video = yt.streams.filter(only_audio=True).first()

    # download the file
    out_file = video.download(output_path='temp')

    folder = yt.title
    folder = ''.join(e for e in folder if e.isalnum() or e.isspace())
    folder = folder.replace(" ", "_")
    # shorten __ to _
    folder = folder.replace("__", "_")

    # Create the output folder
    os.makedirs(folder, exist_ok=True)

    # Rename the file to audio.mp4
    new_file = 'complete.mp4'
    new_file = os.path.join(folder, new_file)
    # Save as mp4 first in folder
    os.rename(out_file, new_file)

    # Convert to WAV for better compatibility
    audio = AudioSegment.from_file(new_file)
    converted_file = os.path.join(folder, "complete.wav")
    audio.export(converted_file, format="wav")

    # result of success
    print("Step 1/3 done. Successfully downloaded.")

    return folder


def whisper_speech_to_text(folder):
    print("Step 2/3. Running text-to-speech with speaker diarization using whisper...")
    file_path = os.path.join(folder, "complete.mp4")
    file = open(file_path, "rb")

    inputs = {
        "file": file,
    }

    output = replicate.run(
        "thomasmol/whisper-diarization:b9fd8313c0d492bf1ce501b3d188f945389327730773ec1deb6ef233df6ea119",
        input=inputs
    )

    transcription_file_path = os.path.join(folder, "transcription.json")
    with open(transcription_file_path, "w") as f:
        f.write(json.dumps(output, indent=4))

    print("Step 2/3 done. Successfully ran text-to-speech with speaker diarization.")


def split_audio_into_speaker_parts(folder):
    print("Step 3/3. Splitting audio into individual files for each speaker...")
    # Load the audio file
    file_path = os.path.join(folder, "complete.wav")
    audio = AudioSegment.from_mp3(file_path)

    transcription_file_path = os.path.join(folder, "transcription.json")
    # Load the JSON output
    with open(transcription_file_path) as f:
        output = json.load(f)

    # Parse the JSON output
    segments = output['segments']

    # Create a dictionary to store audio segments for each speaker
    speaker_audio = {}

    for segment in segments:
        speaker = segment['speaker']
        start = float(segment['start']) * 1000  # pydub works in milliseconds
        end = float(segment['end']) * 1000
        text = segment['text']

        # Extract the segment
        segment_audio = audio[start:end]

        if speaker not in speaker_audio:
            speaker_audio[speaker] = segment_audio
        else:
            speaker_audio[speaker] += segment_audio

    # Export each speaker's audio to a file
    for speaker, audio_segment in speaker_audio.items():
        speaker_file_path = os.path.join(folder, f"{speaker}.mp3")

        audio_segment.export(speaker_file_path, format="mp3")

    print("Step 3/3 done. Successfully split audio into individual files for each speaker. Number of speakers: " + str(len(speaker_audio)))

    print("Saved files to ./" + folder + "/")


def process_video(video_url):
    folder = download_video(video_url)
    whisper_speech_to_text(folder)
    split_audio_into_speaker_parts(folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="downloads audio from a youtube url and splits the audio into speaker parts.")
    parser.add_argument("url", type=str, help="the youtube url to process")
    args = parser.parse_args()
    process_video(args.url)
