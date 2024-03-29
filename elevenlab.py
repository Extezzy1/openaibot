import asyncio

import requests
import uuid
from elevenlabs import clone, set_api_key
import aiohttp
import config

set_api_key(config.elevenlab_api_key)
CHUNK_SIZE = 1024


async def conver_to_audio(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": "7d05fc27029f58ce4cc134ba4f1d9154"
    }

    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 1,
            "similarity_boost": 1
        }
    }
    id = str(uuid.uuid4()) + '.mp3'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            with open(id, "wb") as f:
                async for chunk in response.content.iter_chunked(CHUNK_SIZE):

                    if chunk:
                        f.write(chunk)
    # response = requests.post(url, json=data, headers=headers)
    # with open(id, "wb") as f:
    #     for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
    #         if chunk:
    #             f.write(chunk)

    # sound = AudioSegment.from_file(id, format="mp3")
    # export_path = f"{id.split('.')[0]}.ogg"
    # sound.export(export_path, format="ogg")
    # os.remove(id)
    return id


def add_voice(voice_name, file_name):
    voice = clone(
        name=voice_name,
        files=[file_name],
    )
    return voice.voice_id


# asyncio.run(conver_to_audio("Привет, как дела?", "7iDaRZyEP0FDK0cwoaJW"))