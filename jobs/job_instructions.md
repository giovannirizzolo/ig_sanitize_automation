# Instagram Data Automation

Automate the end-to-end process of requesting your Instagram account data (followers, followings, etc.), retrieving and parsing it, filtering with a whitelist, sending reports via Telegram, and optionally unfollowing users. This project is designed to run as a series of modular scripts (cron-friendly), with all secrets stored in a single `.env` file.

---

## Table of Contents

1. [Features](#features)  
2. [Getting Started](#getting-started)  
   - [Prerequisites](#prerequisites)  
   - [Clone & Install Dependencies](#clone--install-dependencies)  
   - [Configure `.env`](#configure-env)  
   - [Create & Edit Whitelist](#create--edit-whitelist)  
3. [How It Works](#how-it-works)  
   1. [Submit Data Request](#submit-data-request)  
   2. [Poll for Email & Download ZIP](#poll-for-email--download-zip)  
   3. [Parse Followers/Following JSON](#parse-followersfollowing-json)  
   4. [Filter with Whitelist](#filter-with-whitelist)  
   5. [Send Telegram Report](#send-telegram-report)  
   6. [Selenium Unfollow Automation](#selenium-unfollow-automation)  
4. [Scripts & Usage](#scripts--usage)  
5. [Cron Job Configuration](#cron-job-configuration)  
6. [Logging](#logging)  
7. [Future Extensions](#future-extensions)  
8. [Troubleshooting](#troubleshooting)  
9. [License & Acknowledgments](#license--acknowledgments)  

---

## Features

- **Automated “Download Your Data” Request** using Selenium (clicks through Meta Account Center → “Download Your Data”).
- **Email Polling** (IMAP) to detect when Instagram has sent your data-download link.
- **Archive Download** of the ZIP file (JSON-formatted follower/following data).
- **JSON Parsing** to extract followers/following lists.
- **Whitelist Filtering** to exclude protected accounts from any further action.
- **Telegram Notifications** to send filtered follower lists (or other status messages).
- **Selenium “Unfollow” Automation** to remove unwanted followers one-by-one.
- **Cron-friendly architecture**: lightweight runner scripts that can be scheduled into cron (or systemd timers).

---

## Getting Started

### Prerequisites

1. **Python 3.8+**  
2. **Google Chrome** (or Chromium) installed on your system.  
3. **pip** (Python package manager).  
4. Recommended: a Linux server (e.g., Ubuntu) or any Unix-like environment if you plan to use cron.  
5. Internet connectivity (for Selenium to navigate Instagram, and for IMAP access).

### Clone & Install Dependencies

```bash
# 1. Clone (or create) project folder
git clone <repository_url> instagram_data_automation
cd instagram_data_automation

# 2. Create a Python virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# 3. Install required packages
pip install -r requirements.txt

Configure .env
Copy the template (or create) .env in the project root.

Populate it with your own secrets. Example:

ini
Copy
Edit
# .env
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password

TELEGRAM_BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ
TELEGRAM_CHAT_ID=987654321

EMAIL_IMAP_HOST=imap.gmail.com
EMAIL_ADDRESS=youremail@example.com
EMAIL_PASSWORD=your_email_password
Important: Do not commit .env. Add it to .gitignore if using Git.

Create & Edit Whitelist
The file whitelist/whitelist.json contains a JSON array of usernames you never want to unfollow.

Example content:

json
Copy
Edit
{
  "whitelist": [
    "friend_one",
    "family_member_two",
    "favorite_brand"
  ]
}
You can edit this file at any time. The WhitelistFilter module will read it each run.
```

## How It Works
This project is built around a pipeline of discrete steps. Each step is implemented in its own module (under modules/) and invoked by a corresponding script (under scripts/). You can run them manually or schedule them via cron.

### 1. Submit Data Request
Module: modules/meta_requester.py

Script: scripts/run_request.py

#### What It Does

Launches a Chrome browser (using Selenium and webdriver_manager).

Navigates to Instagram’s login page, fills in username/password (from .env), and logs in.

Directly navigates to the “Download Your Data” page (/accounts/privacy/download_data/).

Locates and clicks the “Request Download” button.

Waits for a confirmation message (“We’ll email you when your data is ready”).

Exits the browser.

Usage

bash
Copy
Edit
python3 scripts/run_request.py
Expected Output (stdout or logs/request.log)

pgsql
Copy
Edit
[+] Logged into Instagram successfully.
[+] Clicked 'Request Download' button.
[+] Data request confirmed. Check your email soon.

### 2. Poll for Email & Download ZIP
Module: modules/email_poller.py

Script: scripts/run_email_poll.py

#### What It Does

Connects to your IMAP server (e.g., Gmail) using credentials in .env.

Enters a loop, polling every X minutes (default: 5 minutes) for an email from “no-reply@mail.instagram.com” or a subject containing “Your Instagram Data”.

When found, extracts the download link from the HTML body.

Downloads the ZIP file to data/downloads/ under a timestamped or unique name.

Stores the last seen email UID, so subsequent polls do not re-download the same link.

Usage

bash
Copy
Edit
python3 scripts/run_email_poll.py
Expected Output (stdout or logs/email_poll.log)

bash
Copy
Edit
[+] Found download link: https://instagram-data-download-link.zip
[+] Downloaded ZIP to: data/downloads/IG_data_2025-05-31.zip
3. Parse Followers/Following JSON
Module: modules/data_parser.py

Script: scripts/run_parser.py

What It Does

Locates the most recent ZIP file in data/downloads/ (you can modify to accept a path argument).

Unzips it into data/processed/.

Reads followers.json and following.json from the extracted folder.

Builds a combined JSON object like:

json
Copy
Edit
{
  "followers": [ { ... }, { ... }, … ],
  "following": [ { … }, { … }, … ]
}
Writes combined_data.json to data/processed/combined_data.json.

Usage

bash
Copy
Edit
python3 scripts/run_parser.py
Expected Output (stdout or logs/parser.log)

css
Copy
Edit
[+] Unzipped IG_data_2025-05-31.zip to data/processed/
[+] Combined data written to: data/processed/combined_data.json
4. Filter with Whitelist
Module: modules/whitelist_filter.py

Script: scripts/run_notify.py (as part of notify step)

What It Does

Reads data/processed/combined_data.json.

Reads whitelist/whitelist.json (an array of usernames).

Filters out any follower whose "username" appears in the whitelist.

Writes the filtered list to data/processed/filtered_followers.json.

Usage

bash
Copy
Edit
python3 scripts/run_notify.py
(Note: The same script also sends a Telegram report—see next section.)

Expected Output (stdout or logs/notify.log)

css
Copy
Edit
[+] Filtered followers written to: data/processed/filtered_followers.json
[+] Telegram notification sent.
5. Send Telegram Report
Module: modules/telegram_notifier.py

Script: scripts/run_notify.py

What It Does

Reads data/processed/filtered_followers.json.

Extracts usernames into a newline-separated string.

Sends a Telegram message (via Bot API) containing either:

A notice that there are no non-whitelisted followers (“✅ No followers to unfollow…”), or

A bulleted newline list of usernames to consider unfollowing.

Usage

bash
Copy
Edit
python3 scripts/run_notify.py
Expected Telegram Message

arduino
Copy
Edit
*Followers to potentially remove:*
username_one
username_two
username_three
6. Selenium Unfollow Automation
Module: modules/selenium_unfollower.py

Script: scripts/run_unfollow.py

What It Does

Launches Chrome (via Selenium) and logs into Instagram (reuse of login logic).

Loads data/processed/filtered_followers.json, iterates through each "username".

Navigates to each profile URL (https://www.instagram.com/<username>/).

Clicks the “Following” button, then confirms “Unfollow” in the modal.

Pauses briefly (e.g., 1 second) between each to reduce rate-limiting risk.

Logs success or failure for each username.

Usage

bash
Copy
Edit
python3 scripts/run_unfollow.py
Expected Output (stdout or logs/unfollow.log)

less
Copy
Edit
[+] Unfollowed user_one
[+] Unfollowed user_two
[!] Could not unfollow user_three: button not found or timeout.
Warning: Use this step carefully. Once executed, it will actively unfollow accounts from your Instagram.

Scripts & Usage
All launcher scripts live in the scripts/ folder. Each can be called from the command line. Examples:

bash
Copy
Edit
# 1. Submit Data Request
python3 scripts/run_request.py

# 2. Poll for Email & Download ZIP
python3 scripts/run_email_poll.py

# 3. Parse Followers/Following JSON
python3 scripts/run_parser.py

# 4. Filter with Whitelist & Send Telegram Report
python3 scripts/run_notify.py

# 5. Selenium Unfollow Automation
python3 scripts/run_unfollow.py
If you prefer, make each script executable (chmod +x scripts/*.py) and add a Unix “shebang” (e.g. #!/usr/bin/env python3) at the top.

Always run these inside your virtual environment (if you created one).

Cron Job Configuration
To run steps automatically, use cron (or systemd timers). Below is an example crontab.sample—copy it into your crontab (crontab -e), adjusting paths to match your system.

bash
Copy
Edit
# ────────────────────────────────────────────────────────────────────
# Example Cron Jobs for Instagram Data Automation
# (Adjust /path/to/instagram_data_automation to your actual path)
# ────────────────────────────────────────────────────────────────────

# 1) Every 15 days at 02:00 AM UTC: Submit “Download Your Data” request
0 2 */15 * * cd /path/to/instagram_data_automation && /usr/bin/env python3 scripts/run_request.py >> logs/request.log 2>&1

# 2) Every hour at minute 05: Poll email for download link
5 * * * * cd /path/to/instagram_data_automation && /usr/bin/env python3 scripts/run_email_poll.py >> logs/email_poll.log 2>&1

# 3) Once per day at 03:30 AM UTC: Parse the most recent archive
30 3 * * * cd /path/to/instagram_data_automation && /usr/bin/env python3 scripts/run_parser.py >> logs/parser.log 2>&1

# 4) Once per day at 04:00 AM UTC: Filter & Notify via Telegram
0 4 * * * cd /path/to/instagram_data_automation && /usr/bin/env python3 scripts/run_notify.py >> logs/notify.log 2>&1

# 5) Once per day at 05:00 AM UTC: Run Selenium Unfollow on filtered list
0 5 * * * cd /path/to/instagram_data_automation && /usr/bin/env python3 scripts/run_unfollow.py >> logs/unfollow.log 2>&1
Ensure that python3 points to the same interpreter where you installed dependencies (or use the full path to your virtual environment’s python).

Log files are appended (>>) so you can diagnose any issues later.

Use absolute paths everywhere (cron’s default PATH is minimal).

Logging
Each step writes its standard output and standard error to a dedicated log file under logs/.

Format of logs is plain text—consider using Python’s logging module if you want timestamps or log levels.

Example log files:

logs/request.log

logs/email_poll.log

logs/parser.log

logs/notify.log

logs/unfollow.log

Future Extensions
Rate Limiting & Exponential Backoff

If Instagram starts blocking or rate-limiting Selenium clicks, implement automatic backoff (e.g., sleep 10-60 seconds between actions, randomize sleep times).

Enhanced Email Parsing

Support multiple mail providers (Gmail vs. Outlook).

Retry on IMAP errors; archive old emails into an “Archive” folder to avoid re-processing.

Data Analytics Dashboard

Generate CSV/Excel reports of follower growth/decline over time (e.g., by saving daily combined_data.json and computing deltas).

Integrate with a Jupyter notebook or Plotly/Matplotlib graphs.

Error Notifications

If any step fails, send a Telegram alert (“⚠️ Job X failed: <error message>”).

Implement exponential retry for transient failures (network hiccups, IMAP timeouts, etc.).

Modular API Integration

Instead of Selenium, swap in direct calls to Instagram’s private APIs (if reverse-engineered or via an SDK).

Expand to handle additional Instagram endpoints (e.g., story archives, likes, saved posts).

Web Interface or CLI

Add a small Flask or FastAPI service so you can trigger steps on-demand from a web dashboard.

Provide commands to manage the whitelist (add-whitelist <username>, remove-whitelist <username>).

Troubleshooting
“Element not found” Errors in Selenium

Instagram UI changes frequently; inspect the “Download Your Data” page in your browser, update the XPath/CSS selectors in modules/meta_requester.py accordingly.

Add more generous WebDriverWait timeouts if your network is slow.

IMAP Login Failures

Double-check email/IMAP credentials in .env.

Gmail may require an “App Password” or enabling “Less secure apps” (if not using OAuth).

Ensure IMAP is enabled in your email settings.

Telegram Bot Not Responding

Make sure you’ve started a conversation with your bot (so it can send and receive messages).

Verify TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env.

Use curl https://api.telegram.org/bot<token>/getUpdates to debug.

Cron Jobs Not Running

Cron’s environment is minimal; always use absolute paths to python3 and project directory.

Redirect logs (>> logs/…) so you can see errors.

Check chmod +x if you made scripts executable.

Confirm you’re editing the correct user’s crontab (crontab -e vs. system crontab).

Rate Limiting / Login Blocks

Instagram may prompt for suspicious login verification if logging in too frequently from the same IP.

Consider adding random delays, using a consistent Chrome profile (cookies), or using a VPN/proxy if needed.

License & Acknowledgments
This project is provided “as-is” under the MIT License (feel free to adapt as needed).

Inspired by Instagram’s privacy data request flow and various open-source examples of Selenium automation and IMAP polling.