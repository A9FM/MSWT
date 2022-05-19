import os
import psutil
import sys
import os
import re
import subprocess
import random
import platform
import cpuinfo
from pyrogram import Client, filters
from time import perf_counter

# ------------------------------------------------------------
owner = 1084116847  # Write you Telegram id
version = "1.2.1"
# ------------------------------------------------------------
api_id = 2860432
api_hash = "2fde6ca0f8ae7bb58844457a239c7214"
app = Client("my_account", api_id=api_id, api_hash=api_hash)
# ------------------------------------------------------------

with app:
    app.send_message(owner, f"Server started!\nVersion: **{version}**")


@app.on_message(filters.command(["start", "help"]) & filters.user(owner))
def help_menu(client, message):
    msg = f'''
AdminPanel by A9FM
Version: {version}
==========
1. RAM/CPU/ROM → /info
2. Bash Terminal → /sh (Команда)
3. Start Bots → /bots
4. Restart systemctl (**WARNING**) → /restart
5. Restart server (**WARNING**) → /stop
==========
'''
    app.send_message(message.chat.id, msg)


@app.on_message(filters.command("info") & filters.user(owner))
def disk(client, message):
    info = app.send_message(message.chat.id, "Loading...")

    try:
        diskTotal = int(psutil.disk_usage('/').total / (1024 * 1024 * 1024))
        diskUsed = int(psutil.disk_usage('/').used / (1024 * 1024 * 1024))
        diskPercent = psutil.disk_usage('/').percent
        disk = f"{diskUsed}GB / {diskTotal}GB ({diskPercent}%)"
    except:
        disk = "Unknown"

    info.edit("Get RAM and ROM info...")

    try:
        ramTotal = int(psutil.virtual_memory().total / (1024 * 1024))
        ramUsage = int(psutil.virtual_memory().used / (1024 * 1024))
        ramUsagePercent = psutil.virtual_memory().percent
        ram = f"{ramUsage}MB / {ramTotal} MB ({ramUsagePercent}%)"
    except:
        ram = "Unknown"

    info.edit("Test CPU...")

    try:
        cpuInfo = cpuinfo.get_cpu_info()['brand_raw']
        cpuUsage = psutil.cpu_percent(interval=1)
        cpu = f"{cpuInfo} ({cpuUsage}%)"
    except:
        cpu = "Unknown"

    info.edit("Get OS version...")

    try:
        os = f"{platform.system()} - {platform.release()} ({platform.machine()})"
    except:
        os = "Unknown"

    msg = f'''
Disk: **{disk}**
CPU: **{cpu}**
RAM: **{ram}**
OS: **{os}**
Version: **{version}**
'''
    info.edit(msg)


@app.on_message(filters.command("sh") & filters.user(owner))
async def sh(client, message):
    splitested = message.text.split(maxsplit=1)[1]

    cmd_text = (
        splitested
        if message.reply_to_message is None
        else message.reply_to_message.text
    )
    message = await app.send_message(message.chat.id, "0")
    if not message.reply_to_message and len(splitested) == 1:
        return await message.edit(
            "<b>Specify the command in message text or in reply</b>"
        )
    cmd_obj = subprocess.Popen(cmd_text, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    await message.edit("<b>Running...</b>")
    text = f"$ <code>{cmd_text}</code>\n\n"
    try:
        start_time = perf_counter()
        stdout, stderr = cmd_obj.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        text += "<b>Timeout expired (60 seconds)</b>"
    else:
        stop_time = perf_counter()
        if stdout:
            text += "<b>Output:</b>\n" f"<code>{stdout}</code>\n"
        if stderr:
            text += "<b>Error:</b>\n" f"<code>{stderr}</code>\n"
        time = round(stop_time - start_time, 3) * 1000
        text += f"<b>Completed in {time} miliseconds with code {cmd_obj.returncode}</b> "

    try:
        await message.edit(text)
    except:
        await message.edit("Result too much, send with document...")
        i = random.randint(1, 9999)
        with open(f"result{i}.txt", "w") as file:
            file.write(text)
        await app.send_document(message.chat.id, f"result{i}.txt", caption="Result")
        await message.delete()
        os.remove(f"result{i}.txt")

    cmd_obj.kill()


@app.on_message(filters.command("bots") & filters.user(owner))
async def bots(client, message):
    text = ""

    for i in os.listdir("."):
        if re.compile("(-start.sh)").search(i):
            try:
                start_botes = subprocess.Popen([f"sh {i}"], stdout=subprocess.PIPE, shell=True)
                start_botes.daemon = True
                text += f"✅ File autostart {i} started!\n"
            except:
                text += f"❌ File autostart {i} not started!\n"
    if text == "":
        text = "File autostart not found..."
    await app.send_message(message.chat.id, text)


@app.on_message(filters.command("restart") & filters.user(owner))
async def restart(client, message):
    text = "Send command to server (by systemctl)"
    await app.send_message(message.chat.id, text)
    os.system(f"sh restart_daemon.sh")


@app.on_message(filters.command("stop") & filters.user(owner))
async def st_bots(client, message):
    await app.send_message(message.chat.id, "⚠️  Restart server...")
    os.system("sudo reboot")


while True:
    app.run()
