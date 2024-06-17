# youtube speaker separation

this script uses whisper on [replicate](https://replicate.com/) to download the audio and then separate the speakers from a youtube video.

- input: youtube url

- output: audio files for each speaker, with all spoken parts of that speaker cut together.

this output can then be used to create ai voices for each speaker, for example with instant voice cloning by [elevenlabs](https://elevenlabs.io/) (note: elevenlabs only official allows this for voices that you own the rights to, i don't take any responsibility for any illegal use of this software.)

## how to use

create a virtual environment and install the requirements:

```bash
python3 -m venv .myenv
source .myenv/bin/activate
pip3 install -r requirements.txt
```

copy and rename `.env.sample` to `.env` and fill the `REPLICATE_API_TOKEN` field with your replicate api token.

run the script with a youtube url as argument:

```bash
python3 script.py "youtube_url"
```

## license

mit