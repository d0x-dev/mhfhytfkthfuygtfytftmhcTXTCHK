from flask import Flask, request, jsonify
import requests
import re
import time

app = Flask(__name__)
session = requests.Session()

def normalize_url(url):
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

def is_valid_url(url):
    try:
        url = normalize_url(url)
        regex = re.compile(
            r'^(?:http|ftp)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None
    except:
        return False

def find_payment_gateways(response_text):
    gateways = [
        "paypal", "stripe", "braintree", "square", "cybersource", "authorize.net", "2checkout",
        "adyen", "worldpay", "sagepay", "checkout.com", "shopify", "razorpay", "bolt", "paytm",
        "venmo", "pay.google.com", "revolut", "eway", "woocommerce", "upi", "apple.com", "payflow",
        "payeezy", "paddle", "payoneer", "recurly", "klarna", "paysafe", "webmoney", "payeer",
        "payu", "skrill", "affirm", "afterpay", "dwolla", "global payments", "moneris", "nmi",
        "payment cloud", "paysimple", "paytrace", "stax", "alipay", "bluepay", "paymentcloud",
        "clover", "zelle", "google pay", "cashapp", "wechat pay", "transferwise", "stripe connect",
        "mollie", "sezzle", "payza", "gocardless", "bitpay", "sureship", "conekta", 
        "fatture in cloud", "payzaar", "securionpay", "paylike", "nexi", "forte", "worldline", "payu latam"
    ]
    return [g.capitalize() for g in gateways if g in response_text.lower()]

def check_captcha(response_text):
    keywords = {
        'recaptcha': ['recaptcha', 'google recaptcha'],
        'image selection': ['click images', 'identify objects', 'select all'],
        'text-based': ['enter the characters', 'type the text', 'solve the puzzle'],
        'verification': ['prove you are not a robot', 'human verification', 'bot check'],
        'hcaptcha': [
            'hcaptcha', 'verify you are human', 'select images', 'cloudflare challenge',
            'anti-bot verification', 'hcaptcha.com', 'hcaptcha-widget'
        ]
    }

    detected = []
    for typ, keys in keywords.items():
        for key in keys:
            if re.search(rf'\b{re.escape(key)}\b', response_text, re.IGNORECASE):
                if typ not in detected:
                    detected.append(typ)

    if re.search(r'<iframe.*?src=".*?hcaptcha.*?".*?>', response_text, re.IGNORECASE):
        if 'hcaptcha' not in detected:
            detected.append('hcaptcha')

    return detected if detected else ['No captcha detected']

def detect_cloudflare(response):
    headers = response.headers
    if 'cf-ray' in headers or 'cloudflare' in headers.get('server', '').lower():
        return "Cloudflare"
    if '__cf_bm' in response.cookies or '__cfduid' in response.cookies:
        return "Cloudflare"
    if 'cf-chl' in response.text.lower() or 'cloudflare challenge' in response.text.lower():
        return "Cloudflare"
    return "None"

def detect_3d_secure(response_text):
    keywords = [
        "3d secure", "3ds", "3-d secure", "threeds", "acs", 
        "authentication required", "secure authentication", 
        "secure code", "otp verification", "verified by visa",
        "mastercard securecode", "3dsecure"
    ]
    for keyword in keywords:
        if keyword in response_text.lower():
            return "3D (3D Secure Enabled)"
    return "2D (No 3D Secure Found)"

def check_url(url):
    try:
        url = normalize_url(url)
        if not is_valid_url(url):
            return {
                "error": "Invalid URL",
                "status": "failed",
                "status_code": 400
            }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Referer': 'https://www.google.com'
        }

        response = session.get(url, headers=headers, timeout=10)

        if response.status_code == 403:
            for attempt in range(3):
                time.sleep(2 ** attempt)
                response = session.get(url, headers=headers, timeout=10)
                if response.status_code != 403:
                    break

        if response.status_code == 403:
            return {
                "error": "403 Forbidden: Access Denied",
                "status": "failed",
                "status_code": 403
            }

        response.raise_for_status()

        detected_gateways = find_payment_gateways(response.text)
        captcha_type = check_captcha(response.text)
        cloudflare_status = detect_cloudflare(response)
        secure_type = detect_3d_secure(response.text)
        cvv_present = "cvv" in response.text.lower() or "cvc" in response.text.lower()
        system = "WooCommerce" if "woocommerce" in response.text.lower() else (
                 "Shopify" if "shopify" in response.text.lower() else "Not Detected")

        return {
            "url": url,
            "status": "success",
            "status_code": response.status_code,
            "payment_gateways": detected_gateways or ["None Detected"],
            "captcha": captcha_type,
            "cloudflare": cloudflare_status,
            "security": secure_type,
            "cvv_cvc_status": "Requested" if cvv_present else "Unknown",
            "inbuilt_system": system
        }

    except requests.exceptions.HTTPError as http_err:
        return {
            "error": f"HTTP Error: {str(http_err)}",
            "status": "failed",
            "status_code": 500
        }
    except requests.exceptions.RequestException as req_err:
        return {
            "error": f"Request Error: {str(req_err)}",
            "status": "failed",
            "status_code": 500
        }

@app.route('/gatechk', methods=['GET'])
def gatechk():
    site = request.args.get('site')
    if not site:
        return jsonify({
            "error": "Missing site parameter",
            "status": "failed",
            "status_code": 400
        }), 400

    result = check_url(site)
    return jsonify(result)

@app.route('/gatechk/multiple', methods=['POST'])
def gatechk_multiple():
    data = request.get_json()
    if not data or 'sites' not in data:
        return jsonify({
            "error": "Missing sites array in request body",
            "status": "failed",
            "status_code": 400
        }), 400

    if not isinstance(data['sites'], list):
        return jsonify({
            "error": "sites must be an array of URLs",
            "status": "failed",
            "status_code": 400
        }), 400

    results = [check_url(site) for site in data['sites']]

    return jsonify({
        "results": results,
        "count": len(results),
        "status": "success",
        "status_code": 200
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4444)
