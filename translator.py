import re
import discord
from deep_translator import GoogleTranslator
from deep_translator import exceptions
import config


class MyClient(discord.Client):
    async def on_ready(self):
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name="Namin")
        )
        self.translate_channel_id = 977017340065620048
        self.admin_id = config.my_dc_id
        print("Logged on as", self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        # yourself and the dc owner can set channel
        if len(message.content > 0):
            match message.content:
                case "!set":
                    if (
                        message.author.id == self.admin_id
                        or message.author.guild_permissions.administrator
                    ):
                        self.translate_channel_id = message.channel.id
                        await message.channel.send(
                            f"This channel has been enabled translation"
                        )
                case "!check":
                    if (
                        message.author.id == self.admin_id
                        or message.author.guild_permissions.administrator
                    ):
                        channel = await self.fetch_channel(self.translate_channel_id)
                        await message.channel.send(
                            f"Currently target channel is: {channel.name} in {channel.guild.name}"
                        )
                case _:
                    if (
                        message.content[0] != "!"
                        and message.channel.id == self.translate_channel_id
                        and message.author.bot == False
                    ):
                        translated_text = await self.translate(message)
                        if (
                            translated_text != message.content
                            and translated_text != None
                        ):
                            if message.author.nick == None:
                                await message.channel.send(
                                    f"**`{message.author.name}`** : {translated_text}"
                                )
                            else:
                                await message.channel.send(
                                    f"**`{message.author.nick}`*`* : {translated_text}"
                                )

    async def on_message_edit(self, before_msg, after_msg):
        if before_msg.channel.id == self.translate_channel_id:
            translated_text = await self.translate(before_msg)
            if translated_text != after_msg.content:
                translated_text = await self.translate(after_msg)
                if after_msg.author.nick == None:
                    await after_msg.channel.send(
                        f"**`{after_msg.author.name}`** : {translated_text}"
                    )
                else:
                    await after_msg.channel.send(
                        f"**`{after_msg.author.nick}`** : {translated_text}"
                    )

    async def translate(self, message):
        try:
            translated_text = GoogleTranslator(source="auto", target="en").translate(
                text=message.content
            )
            try:
                # replace correct emoji in translated text
                custom_emojis_in_raw = re.findall("<:\w*:\d*>", message.content)
                custom_emojis_in_translated = re.findall(
                    "<: \w*: \d*>", translated_text
                )

                for index, emoji in enumerate(custom_emojis_in_translated):
                    translated_text = translated_text.replace(
                        emoji, custom_emojis_in_raw[index]
                    )
            except TypeError:
                pass

            try:
                # animation emoji also
                custom_emojis_in_raw = re.findall("<a:\w*:\d*>", message.content)
                custom_emojis_in_translated = re.findall(
                    "<a: \w*: \d*>", translated_text
                )

                for index, emoji in enumerate(custom_emojis_in_translated):
                    translated_text = translated_text.replace(
                        emoji, custom_emojis_in_raw[index]
                    )
            except TypeError:
                pass

            try:
                # user also
                custom_emojis_in_raw = re.findall("<@\d*>", message.content)
                custom_emojis_in_translated = re.findall("<@ \d*>", translated_text)

                for index, emoji in enumerate(custom_emojis_in_translated):
                    translated_text = translated_text.replace(
                        emoji, custom_emojis_in_raw[index]
                    )
            except TypeError:
                pass

            try:
                # channel also
                custom_emojis_in_raw = re.findall("<#\d*>", message.content)
                custom_emojis_in_translated = re.findall("<# \d*>", translated_text)

                for index, emoji in enumerate(custom_emojis_in_translated):
                    translated_text = translated_text.replace(
                        emoji, custom_emojis_in_raw[index]
                    )
            except TypeError:
                pass

            return translated_text
        except exceptions.NotValidPayload:
            return


intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(config.TOKEN)
