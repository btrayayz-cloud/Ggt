import os
import discord
import requests

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
AI_API_KEY = os.getenv("AI_API_KEY")

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        prompt = message.content.replace(f'<@{client.user.id}>', '').strip()
        if not prompt:
            prompt = "مرحباً"

        async with message.channel.typing():
            try:
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {AI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek/deepseek-r1:free",
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                res_data = response.json()
                reply = res_data['choices'][0]['message']['content']
                
                # تقطيع الرد إذا كان طويلاً جداً بالنسبة لديسكورد
                if len(reply) > 2000:
                    for i in range(0, len(reply), 2000):
                        await message.channel.send(reply[i:i+2000])
                else:
                    await message.channel.send(reply)
            except Exception as e:
                await message.channel.send("حدث خطأ أثناء معالجة الطلب.")

client.run(DISCORD_TOKEN)
