import httpx
import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from aiohttp import web
import os
import time
import json

# Configuration
GATEWAY = "3DS Lookup"
WEB_PORT = 5202
WEB_KEY = "darkwaslost"  # Your secret key
VBVBIN_GITHUB_URL = "https://raw.githubusercontent.com/BL4CKH4T336/num/refs/heads/main/vbvbin.txt"

async def download_vbvbin():
    """Download the latest vbvbin.txt from GitHub"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(VBVBIN_GITHUB_URL)
            if response.status_code == 200:
                with open("vbvbin.txt", "wb") as f:
                    f.write(response.content)
                print("Successfully updated vbvbin.txt from GitHub")
                return True
    except Exception as e:
        print(f"Error downloading vbvbin.txt: {e}")
    return False

async def get_bin_info(bin_number):
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://bins.antipublic.cc/bins/{bin_number}"
            response = await client.get(url)
            if response.status_code == 200:
                return response.json()
            return None
    except Exception:
        return None

async def check_vbv_bin(bin_number):
    try:
        if not os.path.exists("vbvbin.txt"):
            if not await download_vbvbin():
                return {
                    "status": "3D FALSE",
                    "response": "BIN Database Not Found"
                }

        with open("vbvbin.txt", "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith(bin_number[:6]):
                    parts = line.strip().split('|')
                    if len(parts) >= 3:
                        return {
                            "status": parts[1],
                            "response": parts[2]
                        }

        return {
            "status": "3D FALSE",
            "response": "BIN Not Found in Database"
        }
    except Exception as e:
        print(f"Error reading BIN database: {e}")
        return {
            "status": "3D FALSE",
            "response": "Lookup Error"
        }

async def handle_request(request):
    key = request.match_info.get('key', '')
    if key != WEB_KEY:
        return web.Response(text="Invalid access key", status=403)

    cc = request.match_info.get('cc', '')
    if not cc:
        return web.Response(text="CC parameter is required", status=400)

    parts = cc.split('|')
    if len(parts) != 4:
        return web.Response(text="Invalid CC format. Use CC|MM|YYYY|CVV", status=400)

    cc_num, mes, ano, cvv = parts
    bin_number = cc_num[:6]

    if bin_number.startswith('3'):
        data = {
            "cc": cc,
            "response": "❌ Unsupported card type (AMEX)",
            "status": "❌ Rejected",
            "gateway": GATEWAY
        }
        return web.Response(
            text=json.dumps(data, ensure_ascii=False),
            content_type="application/json"
        )

    start_time = time.time()
    vbv_status = await check_vbv_bin(bin_number)
    bin_info = await get_bin_info(bin_number)

    if "FALSE ✅" in vbv_status["status"]:
        status = "✅ Passed"
        response_emoji = "✅"
    else:
        status = "❌ Rejected"
        response_emoji = "❌"

    response = f"{response_emoji} {vbv_status['response']}"

    brand = bin_info.get("brand", "N/A") if bin_info else "N/A"
    card_type = bin_info.get("type", "N/A") if bin_info else "N/A"
    level = bin_info.get("level") if bin_info else None
    bank = bin_info.get("bank", "N/A") if bin_info else "N/A"
    country = bin_info.get("country_name", "N/A") if bin_info else "N/A"
    flag = bin_info.get("country_flag", "") if bin_info else ""

    time_taken = f"{time.time() - start_time:.2f}"

    data = {
        "cc": cc,
        "response": response,
        "status": status,
        "bin_info": {
            "brand": brand,
            "type": card_type,
            "level": level,
            "bank": bank,
            "country": f"{country} {flag}".strip()
        },
        "time_taken": f"{time_taken}s",
        "gateway": GATEWAY
    }

    return web.Response(
        text=json.dumps(data, ensure_ascii=False),
        content_type="application/json"
    )

async def start_background_tasks(app):
    await download_vbvbin()

app = web.Application()
app.add_routes([
    web.get('/key={key}/cc={cc}', handle_request),
])
app.on_startup.append(start_background_tasks)

if __name__ == '__main__':
    print(f"""
╔════════════════════════════╗
║       VBV CHECKER WEB      ║
║     Running on port {WEB_PORT}   ║
╚════════════════════════════╝
""")
    web.run_app(app, port=WEB_PORT)
