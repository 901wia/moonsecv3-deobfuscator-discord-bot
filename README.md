# MoonSec V3 Deobfuscator – Discord Bot 

This repository contains a **Discord bot wrapper** around a MoonSec V3 Lua deobfuscation pipeline. The bot accepts obfuscated Lua scripts, processes them using a native MoonSec deobfuscator executable, and returns the deobfuscated output.

> ⚠️ **Disclaimer**: This project is provided for **educational and research purposes only**. You are responsible for ensuring you have the legal right to analyze or deobfuscate any script you process.

---

## Architecture Overview

The project is composed of two main parts:

1. **Discord Bot (Python)**

   * Handles Discord interactions
   * Validates channels and permissions
   * Manages file input/output lifecycle

2. **MoonSec Deobfuscation Engine (Native)**

   * A compiled executable (`MoonsecDeobfuscator.exe`)
   * Performs the actual MoonSec V3 deobfuscation
   * Invoked by the bot via subprocess execution

The bot **does not deobfuscate Lua itself**. It orchestrates execution of the MoonSec deobfuscator and returns results.

---

## Directory Structure

```
MoonSecV3DeobfuscatorDiscordBotStable/
│
├── bot.py                  # Discord bot entry point
├── decom.lua               # Lua post-processing / cleanup script
├── requirements.txt        # Python dependencies
├── startbot.bat            # Windows startup script
├── .env                    # Environment configuration
│
├── bin/                    # Embedded Lua runtime (5.1)
│   ├── lua5.1.exe
│   ├── lua5.1.dll
│   └── lua5.1
│
└── _work/                  # Temporary working directory (auto-generated)
```

The **MoonSec deobfuscator executable itself is external** and referenced via environment variables.

---

## Requirements

* **Windows 10 / 11 (x64)**
* **Python 3.10+**
* **Discord Bot Token**
* **MoonSec V3 Deobfuscator executable**
* Lua 5.1 runtime (included in `/bin`)

---

## Installation

This repository can be used in two different ways depending on your needs:

* **A: Discord bot wrapper** — run the Python Discord bot which invokes the MoonSec deobfuscator executable.
* **B: Standalone deobfuscator** — run the MoonSec deobfuscator executable directly (no bot).

Below are clear, production-minded instructions for both workflows, including what to do if you do **not** have `git` installed.

---

### A — Install and run the Discord bot (recommended if you want automation in Discord)


```
1. Open the repository page in your browser and click **Code → Download ZIP**.
2. Extract the ZIP to a folder and `cd` into that folder in your terminal.

#### Install Python dependencies

```bash
pip install -r requirements.txt
```

*(Use a virtual environment if you prefer: `python -m venv .venv` then activate it with your shell.)*

#### Provide or point to the MoonSec executable

This project **does not** ship MoonSec itself. If you already downloaded or built the standalone deobfuscator (for example from [https://github.com/901wia/moonsecv3-deobfuscator](https://github.com/901wia/moonsecv3-deobfuscator)) you have two options:

* **Copy** the `MoonsecDeobfuscator.exe` and required files into this bot repository and set `MOON_EXECUTABLE` to the local path, or
* **Point** the bot to the executable in the other repository by setting `MOON_EXECUTABLE` to the absolute path of that executable.

Example `.env` snippet:

```
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
MOON_EXECUTABLE=C:/path/to/moonsec-repo/MoonsecDeobfuscator.exe
DECOM_SCRIPT=decom.lua
ALLOWED_CHANNEL_IDS=
```

> Note: On Windows, provide an absolute path. Forward slashes work fine in most shells.

#### Run the bot

* Using the included batch file:

```bash
startbot.bat
```

* Or run directly with Python:

```bash
python bot.py
```

The bot will read `MOON_EXECUTABLE` from your `.env` and call the deobfuscator when a user uploads a file.

---

### B — Standalone deobfuscator (no bot)

If you only want to deobfuscate files locally without the Discord automation, use the standalone repo that contains the native executable and its DLL dependencies.

#### 1. Get the standalone deobfuscator

Repository 

```
https://github.com/901wia/moonsecv3-deobfuscator
```

Clone or download that repo and open a terminal in the folder that contains `MoonsecDeobfuscator.exe` and the supporting files (examples: `Antlr4.Runtime.Standard.dll`, `KeraLua.dll`, `NLua.dll`, `MoonsecDeobfuscator.runtimeconfig.json`, `runtimes/` folder).

#### 2. Place the obfuscated code into `input.lua`

Save the obfuscated Lua source you want to analyze into `input.lua` (overwrite or create this file in the same folder as the executable).

#### 3. Run the deobfuscator from the command line

Open CMD or PowerShell in the folder and run (example):

```cmd
MoonsecDeobfuscator.exe -dev -i input.lua -o output.luac
```

* `-dev` — runs the deobfuscator in development mode (verbose output). If you do not want verbose logging, omit this flag.
* `-i <file>` — input file path (obfuscated Lua file).
* `-o <file>` — output file path (deobfuscated output).

When the process finishes, the deobfuscated result will be written to `output.luac` (or whatever path you supplied).

#### 4. Notes and troubleshooting

* Ensure the executable and DLLs are in the same folder (the runtime depends on those files).
* If `output.luac` is empty, check the console output for errors and confirm `input.lua` contains obfuscated code supported by MoonSec V3.
* For advanced options, consult the standalone repo's README (the repo above contains additional documentation and examples).

---

### Quick summary / recommended workflow

* If you want **Discord automation**, follow section **A** and set `MOON_EXECUTABLE` in `.env` to the full path of the executable (either copied into this repo or referenced from the standalone repo).
* If you want **manual, local deobfuscation**, use section **B** — place your obfuscated code into `input.lua` and run the `.exe` with `-i` and `-o`.

---

## MoonSec Deobfuscator Setup

This project **does not ship with MoonSec** itself.

You must provide your own MoonSec-compatible deobfuscator executable.

Example directory:

```
C:\Tools\MoonSec\MoonsecDeobfuscator.exe
```

The executable is treated as a **black box** by the bot and must:

* Accept an input Lua file
* Produce a deobfuscated output file
* Exit with a valid process code

---

## Environment Configuration (.env)

Create a `.env` file in the project root.

### Example `.env`

```
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN

# Absolute path to the MoonSec deobfuscator executable
MOON_EXECUTABLE=C:\Tools\MoonSec\MoonsecDeobfuscator.exe

# Lua script used for final cleanup / transformation
DECOM_SCRIPT=decom.lua

# Comma-separated Discord channel IDs allowed to use the bot
ALLOWED_CHANNEL_IDS=123456789012345678,987654321098765432
```

### Variable Explanation

| Variable              | Description                                                                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `DISCORD_TOKEN`       | Your Discord bot token obtained from the Discord Developer Portal. This is required for the bot to authenticate and connect to Discord.     |
| `MOON_EXECUTABLE`     | Absolute path to the MoonSec deobfuscator executable on your system. The bot will invoke this binary as part of the deobfuscation pipeline. |
| `DECOM_SCRIPT`        | Lua script executed after the main deobfuscation step. Used for cleanup, normalization, or final transformations.                           |
| `ALLOWED_CHANNEL_IDS` | Optional security filter. Controls which Discord channels are permitted to use the bot.                                                     |

#### `ALLOWED_CHANNEL_IDS` Behavior

* **Empty or not set**:
  The bot will accept commands and file uploads from **all channels** it has access to.

* **One or more channel IDs specified**:
  The bot will **only** respond in the listed channels. All other channels will be ignored.

* **Format**:
  Comma-separated list of numeric Discord channel IDs.

**Examples:**

```
ALLOWED_CHANNEL_IDS=
```

> Bot is enabled globally in all accessible channels.

```
ALLOWED_CHANNEL_IDS=123456789012345678
```

> Bot is restricted to a single channel.

```
ALLOWED_CHANNEL_IDS=123456789012345678,987654321098765432
```

> Bot is restricted to multiple specific channels.

Using channel restrictions is **strongly recommended** when running the bot in shared or public servers.

---

## How the Deobfuscation Pipeline Works

1. User uploads an obfuscated Lua file in Discord
2. Bot saves the file into `_work/`
3. Bot invokes:

   * MoonSec deobfuscator executable
   * Lua 5.1 runtime for post-processing
4. `decom.lua` cleans or restructures the output
5. Final Lua file is returned to Discord
6. Temporary files are deleted

All execution happens **locally** on the host machine.

---

## Running the Bot

### Option 1: Batch File

```bash
startbot.bat
```

### Option 2: Manual

```bash
python bot.py
```

You should see the bot come online in Discord.

---

## Security Notes

* Always restrict `ALLOWED_CHANNEL_IDS`
* Never expose your `DISCORD_TOKEN`
* Do **not** run the bot on untrusted machines
* Treat all uploaded Lua files as **untrusted input**

---

## Common Issues

### ❌ MoonSec executable not found

* Verify `MOON_EXECUTABLE` path
* Ensure the file has execution permission

### ❌ Lua runtime errors

* Ensure `/bin` directory is intact
* Lua version must be **5.1**

### ❌ Bot responds but returns no file

* Check console logs
* Validate MoonSec output file generation

---

## License

This project is released under the **MIT License**.

MoonSec and related technologies are property of their respective owners.

---

## Contribution

Pull requests are welcome for:

* Stability improvements
* Better error handling
* Additional MoonSec variants support

---

## Final Notes

This repository is intended for **advanced users** familiar with:

* Lua bytecode
* Obfuscation techniques
* Reverse engineering workflows

If you do not understand the implications of deobfuscation, **do not use this tool**.
