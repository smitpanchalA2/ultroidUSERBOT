# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -


• `{i}mtoi <reply to media>`
    media to image conversion

• `{i}mtos <reply to media>`
    convert media to sticker.

• `{i}doc <filename.ext>`
    Reply to a text msg to save it in a file.

• `{i}open`
    Reply to a file to reveal it's text.

• `{i}rename <file name with extension>`
    rename the file

"""

import asyncio
import os

import cv2
import requests
from PIL import Image

from . import *

opn = []


@ultroid_cmd(pattern="rename ?(.*)")
async def imak(event):
    reply = await event.get_reply_message()
    if not reply:
        await eor(event, "Reply to any media/Document.")
        return
    inp = event.pattern_match.group(1)
    if not inp:
        await eor(event, "Give The name nd extension of file")
        return
    xx = await eor(event, "`Processing...`")
    image = await ultroid_bot.download_media(reply)
    os.rename(image, inp)
    await ultroid_bot.send_file(event.chat_id, inp, force_document=True, reply_to=reply)
    os.remove(inp)
    await xx.delete()


@ultroid_cmd(pattern="mtoi$")
async def imak(event):
    reply = await event.get_reply_message()
    if not (reply and (reply.media)):
        await eor(event, "Reply to any media.")
        return
    xx = await eor(event, "`Processing...`")
    image = await ultroid_bot.download_media(reply)
    file = "ult.png"
    if image.endswith((".webp", ".png")):
        c = Image.open(image)
        c.save(file)
    else:
        img = cv2.VideoCapture(image)
        ult, roid = img.read()
        cv2.imwrite(file, roid)
    await ultroid_bot.send_file(event.chat_id, file, reply_to=reply)
    await xx.delete()
    os.remove(file)
    os.remove(image)


@ultroid_cmd(pattern="mtos$")
async def smak(event):
    reply = await event.get_reply_message()
    if not (reply and (reply.media)):
        await eor(event, "Reply to any media.")
        return
    xx = await eor(event, "`Processing...`")
    image = await ultroid_bot.download_media(reply)
    file = "ult.webp"
    if image.endswith((".webp", ".png", ".jpg")):
        c = Image.open(image)
        c.save(file)
    else:
        img = cv2.VideoCapture(image)
        ult, roid = img.read()
        cv2.imwrite(file, roid)
    await ultroid_bot.send_file(event.chat_id, file, reply_to=reply)
    await xx.delete()
    os.remove(file)
    os.remove(image)


@ultroid_cmd(
    pattern="doc",
)
async def _(event):
    input_str = event.text[5:]
    xx = await eor(event, get_string("com_1"))
    if event.reply_to_msg_id:
        a = await event.get_reply_message()
        if not a.message:
            return await xx.edit("`Reply to a message`")
        else:
            b = open(input_str, "w")
            b.write(str(a.message))
            b.close()
            await xx.edit(f"**Packing into** `{input_str}`")
            await asyncio.sleep(2)
            await xx.edit(f"**Uploading** `{input_str}`")
            await asyncio.sleep(2)
            await event.client.send_file(event.chat_id, input_str)
            await xx.delete()
            os.remove(input_str)


@ultroid_cmd(
    pattern="open$",
)
async def _(event):
    xx = await eor(event, get_string("com_1"))
    if event.reply_to_msg_id:
        a = await event.get_reply_message()
        if a.media:
            b = await a.download_media()
            c = open(b)
            d = c.read()
            c.close()
            try:
                await xx.edit(f"```{d}```")
            except BaseException:
                key = (
                    requests.post(
                        "https://nekobin.com/api/documents", json={"content": d}
                    )
                    .json()
                    .get("result")
                    .get("key")
                )
                await xx.edit(
                    f"**MESSAGE EXCEEDS TELEGRAM LIMITS**\n\nSo Pasted It On [NEKOBIN](https://nekobin.com/{key})"
                )
        else:
            return await eod(xx, "`Reply to a readable file`", time=5)
    else:
        return await eod(xx, "`Reply to a readable file`", time=5)


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
