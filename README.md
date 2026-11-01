

<div align="center">

# IG DM Flood

**A Termux-native Instagram DM tool. No server. No session save. No shared IP.**

[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Termux-000000?style=for-the-badge&logo=android&logoColor=3DDC84)](https://termux.dev/)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-22c55e?style=for-the-badge)]()
[![PRs](https://img.shields.io/badge/PRs-welcome-blue?style=for-the-badge)]()

Runs entirely on your phone. Your real IP. Your account. Your rules.

</div>

---

## Table of Contents

- [What this is](#what-this-is)
- [What this is not](#what-this-is-not)
- [How it works](#how-it-works)
- [Install](#install)
- [Usage](#usage)
- [Risk model](#risk-model)
- [Rules of the road](#rules-of-the-road)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## What this is

A single-file Python tool that runs inside [Termux](https://termux.dev/) on Android. It logs into your Instagram account, resolves target usernames or group threads, and sends DMs with configurable count and pacing.

Built for **personal, low-volume use** on a **single phone, single account**. No backend, no database, no third-party server ever sees your credentials or your session.

### Core design decisions

| Decision | Why |
|---|---|
| **No session file** | Nothing written to disk. Each run logs in fresh. No leak surface. |
| **No server** | Runs on your phone. Instagram sees your real mobile IP, not a datacenter. |
| **No Telegram / webhook exfil** | The original script shipped credentials to a bot. That's gone. This tool has no network calls except Instagram's. |
| **2 threads, 30–90s delay** | Not a flood. A trickle. Behaves like a human scrolling and replying. |
| **Hard cap of 30 messages per run** | Forces small, deliberate batches. |
| **MIT licensed, no obfuscation** | You can read every line. Nothing hidden. |

---

## What this is not

- **Not a bot farm.** No multi-account automation, no parallel account switching.
- **Not ban-proof.** Any tool that sends unsolicited DMs violates Instagram's Terms of Service. Risk exists. Mitigated, not eliminated.
- **Not anonymous.** Instagram sees your phone's IP, your device fingerprint, and the account you log in with. This is by design — a phone IP is the most human-looking IP you have.
- **Not a spider.** It does not scrape followers, DMs, or any account data beyond resolving usernames to IDs.

---

## How it works

```

┌─────────────────────────────────────────────────────┐
│  Your Phone (Termux)                                │
│                                                     │
│  flood.py  ──►  instagrapi  ──►  Instagram servers  │
│       │                              ▲              │
│       │                              │              │
│       └── prompts: user, pass, OTP,  │              │
│           message, count, targets    │              │
│                                      │              │
│  IP shown to Instagram: YOUR phone   │              │
│  Session written to disk: NOTHING    │              │
│  Credentials sent anywhere: NOBODY   │              │
└─────────────────────────────────────────────────────┘

```

1. Script asks for username + password (hidden input).
2. `instagrapi` performs a real login from your device. If 2FA is on, it prompts for OTP.
3. Session lives **only in RAM** for the duration of the run.
4. Message and count are read, targets are resolved to user IDs.
5. Sends go out at 30–90s intervals with 2 workers.
6. Process exits. Session is gone. Disk is untouched.

---

## Install

### 1. Termux

**Do not use the Play Store version.** It's outdated and broken.

Install from F-Droid: **[f-droid.org/packages/com.termux](https://f-droid.org/packages/com.termux/)**

### 2. System dependencies

```bash
pkg update && pkg upgrade -y
pkg install python git rust binutils libffi openssl -y
```

rust and binutils are needed only if cryptography (a transitive dep of instagrapi) has to build from source. If prebuilt wheels work for your architecture, they may not be necessary — but installing them prevents a common failure.

3. Python dependencies

```bash
pip install --upgrade pip
pip install instagrapi requests
```

4. Clone and run

```bash
git clone https://github.com/<your-username>/ig-flood-termux.git
cd ig-flood-termux
bash setup.sh
python flood.py
```

Or skip setup.sh if dependencies are already present:

```bash
python flood.py
```

---

Usage

Interactive flow

```
=== IG DM Flood (Termux, no-save) ===

Username: my_account
Password:
[*] logging in...
[+] login successful

Mode:
  1 = send to individual users
  2 = send to a group thread
  3 = list recent threads
Choice [1/2/3]: 1
Message: hey
How many times (1-30, default 1): 10
Target usernames (comma separated): alice, bob, carol
[*] resolving targets...
  alice → 31415926535
  bob   → 27182818284
  carol → 16180339887
[*] sending to 3 users × 10 times...
[+] sent → alice
[+] sent → bob
[+] sent → carol
...
[done] 30 messages in 412.6s
```

Modes

Mode What it does
1 — Users Resolve a comma-separated list of usernames, send to each count times.
2 — Group thread Send to an existing DM thread by numeric ID, count times.
3 — List threads Print recent DM threads with thread_id, title, participants. Use this to find the ID for mode 2.

2FA

If your account has 2FA enabled, the script prompts for an OTP every run:

```
[*] logging in...
Enter OTP: 123456
[+] login successful
```

This is by design. No session is saved, so each run is treated as a fresh device login by Instagram.

Finding a group thread ID

Run mode 3:

```
thread_id=340282366920938463463374607431768211456 | title=(no title) | users=[alice, bob]
thread_id=340282366920938463463374607431768211457 | title=project_x   | users=[carol, dave]
```

Copy the thread_id and use it in mode 2.

---

Risk model

Instagram's anti-spam systems watch volume, velocity, target repetition, and account age. Shared datacenter IPs amplify every one of those signals. This tool removes the IP factor entirely by running on your phone, but the others remain.

What this tool removes

Risk Status
Shared cloud IP (Render, Vercel, Heroku) Gone — you use your phone's IP
Cross-user IP contamination Gone — one phone, one account
Session file leak Gone — nothing saved
Credential exfiltration Gone — no external calls

What this tool does not remove

Risk Mitigation
Flood volume / velocity 2 threads, 30–90s delay, 30-message cap
Target reports Rotate targets between runs; never blast the same person
New-account flag Use an aged, warmed account (1 month+)
2FA device-trust friction Expected; solve OTP each run
Termux user-agent fingerprint Minor; instagrapi sends a real Android UA

Honest expectation

Setup Expected outcome
Aged account, 10–20 DMs, distinct targets, spaced runs Survives. No challenge.
Aged account, 30 DMs, one target reporting you 24h restriction on that account. Not permanent.
New account (under 1 week), 20+ DMs Challenge likely (CAPTCHA / email verify). Solve and retry.
Any account, 100+ DMs in one run Restriction likely. The 30 cap exists to prevent this.

---

Rules of the road

1. One phone, one account, one run at a time. Switching accounts inside the same Termux session is the fastest way to get flagged.
2. Use an aged account. 1 month minimum, with real activity. A fresh account doing bulk DMs is the textbook bot signature.
3. Keep counts low. 10–20 is the safe zone. 30 is the ceiling, not the target.
4. Rotate targets. Never send the same message to the same person from two different runs. "Report spam" from multiple angles gets your account reviewed.
5. Space out runs. Back-to-back runs on the same account from the same IP spike the velocity signal. A few hours apart is fine.
6. If you get a challenge, stop. Open Instagram in your phone browser, complete the verification, wait 24 hours, then resume. Do not retry immediately.
7. Do not share your phone or your Termux with anyone. Your IP and your session are your identity to Instagram.

---

Troubleshooting

cryptography build fails

```bash
pkg install rust binutils libffi openssl -y
pip install --upgrade pip setuptools wheel
pip install cryptography
```

PleaseWaitFewMinutes on login

Instagram is rate-limiting your IP after too many recent logins. Wait 15–30 minutes, then retry.

ChallengeRequired on login

Instagram wants you to verify this device. Open Instagram in your phone browser, complete the challenge (email link, SMS code, or "it was me" prompt), then retry the script. If it persists, use a different network (Wi-Fi vs mobile data) once, complete the challenge, then switch back.

TwoFactorRequired but I don't get an OTP

The OTP goes to your 2FA method — SMS, WhatsApp, or your authenticator app. Check all three. If you use an authenticator, enter the current 6-digit code.

Script hangs after "resolving targets"

Instagram's username lookup endpoint is rate-limited too. This usually clears after 30–60 seconds. If not, kill with Ctrl+C and retry with fewer targets.

ModuleNotFoundError: No module named 'instagrapi'

```bash
pip install instagrapi
```

If pip itself is missing:

```bash
pkg install python -y
```

---

FAQ

Q: Does this save my session?
A: No. Nothing is written to disk. Every run is a fresh login.

Q: Will Instagram ban me?
A: It can. Any unsolicited DM at volume violates Instagram's ToS. The tool minimizes the signals — real IP, low volume, human pacing — but does not eliminate the risk. Read Risk model.

Q: Why does it ask for an OTP every time?
A: Because no session is saved. Instagram treats each run as a new device login. If you have 2FA enabled, that means OTP every run.

Q: Can I run this on my laptop instead of Termux?
A: Yes. The code is plain Python with instagrapi. Any machine with Python 3.10+ works. Laptop IPs are also real IPs; the shared-datacenter problem does not apply.

Q: Why 30 messages and not 500?
A: Because 500 messages is a ban. 30 is a batch you can send safely and recover from. The cap is a feature.

Q: Why 30–90s delay?
A: Human reply speed. Anything faster reads as automation.

Q: Can I add more features — auto-responses, scheduled sends, multi-account?
A: Fork it. The single-file design is intentionally minimal. Additions live in your fork, on your risk.

Q: Does this work on iOS?
A: No. Termux is Android-only. On iOS, use a-Shell or run the script on a laptop.

Q: Where do the credentials go?
A: Nowhere. The script reads them into memory, hands them to instagrapi for a login call to Instagram's servers, and discards them when the process exits. No third-party network calls exist in the code. Verify by reading flood.py.

---

Disclaimer

This tool is provided for educational and personal use only. It is not affiliated with, endorsed by, or supported by Instagram or Meta.

Using this tool to send unsolicited messages violates Instagram's Terms of Use and Community Guidelines. Accounts used with this tool may be rate-limited, restricted, or permanently banned. The authors accept no responsibility for account loss, legal consequences, or any other damage arising from use.

Do not use this tool to harass, stalk, defraud, or impersonate. Those are crimes in most jurisdictions and are outside the scope of what this project permits.

If you are the subject of unwanted messages from a user of this tool, report them through Instagram's built-in tools — that is the correct and effective channel.

---

License

Released under the MIT License. No warranty. Read the license; it is short.

---

<div align="center">

If this saved you time, star the repo. If it got you banned, you didn't read the rules.

</div>
