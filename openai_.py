import asyncio

from openai import AsyncOpenAI
from config import openai_api_key, max_tokens

client = AsyncOpenAI(api_key=openai_api_key)
# openai.api_key = openai_api_key

class AIGirlfriend:
    def __init__(self, messages) -> None:
        self.messages = messages

    async def get_completion_from_messages(self, messages, model="gpt-3.5-turbo", temperature=1):
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            temperature=temperature,  # this is the degree of randomness of the model's output
        )
        #     print(str(response.choices[0].message))
        return response.choices[0].message.content

    async def get_response(self, message):
        self.messages.append({"role": "user", "content": message})
        gf_message = await self.get_completion_from_messages(self.messages)
        self.messages.append({"role": "assistant", "content": gf_message})
        return gf_message


# x = AIGirlfriend(messages=[
#             {
#                 "role": "user",
#                 "content": "Say this is a test",
#             }
#         ],)
# asyncio.run(x.get_response("Привет! Как прошел сегодня день?" ))
# print(x.get_response("Было утомительно. Хочешь вместе посмотреть какой-нибудь фильм" ))