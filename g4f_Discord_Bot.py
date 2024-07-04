import discord
from discord.ext import commands
from g4f.client import Client
from discord import app_commands
import asyncio

intents = discord.Intents.default()
intents.typing = False
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='/', intents=intents)
        self.allowed_channels = set()

    async def setup_hook(self):
        await self.tree.sync()
        print("コマンドを同期しました。")

client = MyBot()
gpt_client = Client()

@client.event
async def on_ready():
    print(f'ボットがログインしました： {client.user}')
    await client.change_presence(activity=discord.Game(name="/gpt 今日は何曜日"))

@client.tree.command(name="gpt", description="GPT-4を使用してテキストを生成します。")
@app_commands.describe(プロンプト="あなたの質問や指示")
async def gpt(interaction: discord.Interaction, プロンプト: str):
    await interaction.response.defer()

    try:
        応答 = await asyncio.to_thread(gpt_client.chat.completions.create,
            model="gpt-4o",
            messages=[{"role": "user", "content": プロンプト}],
            language="ja",
        )
        生成されたテキスト = 応答.choices[0].message.content
        await interaction.followup.send(f"\n{生成されたテキスト}")
    except Exception as エラー:
        await interaction.followup.send(f"エラーが発生しました： {str(エラー)}")

@client.tree.command(name="ch_set", description="テキストチャンネルでGPT自動応答を有効にします。")
@app_commands.describe(チャンネル="設定するチャンネル")
async def ch_set(interaction: discord.Interaction, チャンネル: discord.TextChannel):
    client.allowed_channels.add(チャンネル.id)
    await interaction.response.send_message(f"{チャンネル.mention} でGPT自動応答が有効になりました。")

@client.tree.command(name="ch_unset", description="テキストチャンネルでGPT自動応答を無効にします。")
@app_commands.describe(チャンネル="禁止するチャンネル")
async def ch_unset(interaction: discord.Interaction, チャンネル: discord.TextChannel):
    client.allowed_channels.discard(チャンネル.id)
    await interaction.response.send_message(f"{チャンネル.mention} でGPT自動応答が無効になりました。")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id in client.allowed_channels:
        try:
            応答 = await asyncio.to_thread(gpt_client.chat.completions.create,
                model="gpt-4o",
                messages=[{"role": "user", "content": message.content}],
                language="ja",
            )
            生成されたテキスト = 応答.choices[0].message.content
            await message.channel.send(f"\n{生成されたテキスト}")
        except Exception as エラー:
            await message.channel.send(f"エラーが発生しました： {str(エラー)}")

    await client.process_commands(message)

async def main():
    async with client:
        await client.start('your_token_here')

if __name__ == "__main__":
    asyncio.run(main())
