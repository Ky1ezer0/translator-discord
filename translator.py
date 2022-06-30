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
        self.translate_channel_id = 990973759940878337
        self.admin_id = config.my_dc_id
        print("Logged on as", self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        # yourself and the dc owner can set channel

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
                    await message.channel.send(
                        f"Currently target channel is: {self.translate_channel_id}"
                    )
            case _:
                if (
                    message.channel.id == self.translate_channel_id
                    and message.author.bot == False
                ):
                    try:
                        translated_text = GoogleTranslator(
                            source="auto", target="en"
                        ).translate(text=message.content)
                        try:
                            # replace correct emoji in translated text
                            custom_emojis_in_raw = re.findall(
                                "<:\w*:\d*>", message.content
                            )
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
                            custom_emojis_in_raw = re.findall(
                                "<a:\w*:\d*>", message.content
                            )
                            custom_emojis_in_translated = re.findall(
                                "<a: \w*: \d*>", translated_text
                            )

                            for index, emoji in enumerate(custom_emojis_in_translated):
                                translated_text = translated_text.replace(
                                    emoji, custom_emojis_in_raw[index]
                                )
                        except TypeError:
                            pass

                        if (
                            translated_text != message.content
                            and translated_text != None
                        ):
                            if message.author.nick == None:
                                await message.channel.send(
                                    f"**{message.author.name}** : {translated_text}"
                                )
                            else:
                                await message.channel.send(
                                    f"**{message.author.nick}** : {translated_text}"
                                )
                    except exceptions.NotValidPayload:
                        pass


intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(config.TOKEN)
