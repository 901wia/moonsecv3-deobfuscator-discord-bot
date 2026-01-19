import discord
import subprocess
import os
import shutil
import random
import string
import platform
import asyncio
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
MOON_EXECUTABLE = os.getenv("MOON_EXECUTABLE")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DECOM_SCRIPT = os.path.join(BASE_DIR, os.getenv("DECOM_SCRIPT"))

ALLOWED_CHANNEL_IDS = {
    int(x.strip())
    for x in os.getenv("ALLOWED_CHANNEL_IDS", "").split(",")
    if x.strip().isdigit()
}

SUPPORTED_EXTENSIONS = (".lua", ".luau", ".txt")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

LUA_BIN = os.path.join(BASE_DIR, "bin", "lua5.1.exe")
WORK_DIR = os.path.join(BASE_DIR, "_work")
os.makedirs(WORK_DIR, exist_ok=True)

def rand_id(length=12):
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))

def startupinfo():
    if platform.system() == "Windows":
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        return info
    return None

async def run_process(cmd, cwd):
    return await asyncio.to_thread(
        subprocess.run,
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        startupinfo=startupinfo()
    )

async def process_attachment(channel, user, attachment):
    job_dir = os.path.join(WORK_DIR, rand_id())
    os.makedirs(job_dir, exist_ok=True)

    input_file = os.path.join(job_dir, "input.lua")
    output_luac = os.path.join(job_dir, "compiled.luac")
    output_lua = os.path.join(job_dir, "decompiled.lua")

    try:
        await attachment.save(input_file)

        compile_result = await run_process(
            [
                MOON_EXECUTABLE,
                "-dev",
                "-i", input_file,
                "-o", output_luac
            ],
            cwd=job_dir
        )

        if compile_result.returncode != 0 or not os.path.exists(output_luac):
            await channel.send("Compilation stage failed. Bytecode was not produced.")
            return

        decompile_result = await run_process(
            [LUA_BIN, DECOM_SCRIPT, output_luac, output_lua],
            cwd=job_dir
        )

        if not os.path.exists(output_lua):
            await channel.send("Decompilation stage failed. No Lua output generated.")
            return

        dm = await user.create_dm()
        await dm.send(
            "Original input file",
            file=discord.File(input_file, filename=attachment.filename)
        )

        await channel.send(
            f"Decompiled output for `{attachment.filename}`",
            file=discord.File(output_lua, filename="Decompiled.lua")
        )

    except Exception as exc:
        await channel.send("Unhandled system exception occurred.")
        try:
            await user.send(f"System exception:\n```{exc}```")
        except:
            pass

    finally:
        shutil.rmtree(job_dir, ignore_errors=True)

@client.event
async def on_ready():
    print("Bot online")
    print("Moon executable:", MOON_EXECUTABLE)
    print("Lua binary:", LUA_BIN)
    print("Decompiler script:", DECOM_SCRIPT)

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if ALLOWED_CHANNEL_IDS and message.channel.id not in ALLOWED_CHANNEL_IDS:
        return

    valid_attachments = [
        a for a in message.attachments
        if a.filename.lower().endswith(SUPPORTED_EXTENSIONS)
    ]

    if not valid_attachments:
        return

    status = await message.channel.send(
        f"Processing {len(valid_attachments)} file(s)"
    )

    for attachment in valid_attachments:
        await process_attachment(message.channel, message.author, attachment)

    try:
        await message.delete()
    except:
        pass

    await status.edit(content="Processing complete")

client.run(TOKEN)
