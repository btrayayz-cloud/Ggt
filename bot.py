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

    # التفاعل عند الإشارة للبوت أو في الرسائل الخاصة
    if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        prompt = message.content.replace(f'<@{client.user.id}>', '').strip()
        if not prompt:
            prompt = "مرحباً"

        async with message.channel.typing():
            try:
                headers = {
                    "Authorization": f"Bearer {AI_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://discord.com",
                    "X-Title": "Discord AI Bot"
                }
                
                # استخدام نموذج مجاني ممتاّز وسريع ويدعم اللغة العربية
                data = {
                    "model": "google/gemini-2.0-flash-lite-001:free",
                    "messages": [
                        {
                            "role": "system", 
                            "content": "أنت مساعد ذكي وتتحدث وتفهم اللغة العربية بطلاقة. أجب دائماً باللغة العربية بأسلوب واضح وودود."
                        },
                        {"role": "user", "content": prompt}
                    ]
                }
                
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions", 
                    headers=headers, 
                    json=data,
                    timeout=30
                )
                
                res_data = response.json()
                
                if response.status_code == 200 and "choices" in res_data and len(res_data["choices"]) > 0:
                    reply = res_data['choices'][0]['message']['content']

                    # تقطيع الرد إذا كان أطول من حد ديسكورد (2000 حرف)
                    if len(reply) > 2000:
                        for i in range(0, len(reply), 2000):
                            await message.channel.send(reply[i:i+2000])
                    else:
                        await message.channel.send(reply)
                else:
                    error_msg = res_data.get("error", {}).get("message", f"كود الاستجابة: {response.status_code}")
                    await message.channel.send(f"⚠️ خطأ من سيرفر الذكاء الاصطناعي: {error_msg}")
                    
            except Exception as e:
                await message.channel.send(f"⚠️ حدث خطأ في النظام: {str(e)}")

client.run(DISCORD_TOKEN)
