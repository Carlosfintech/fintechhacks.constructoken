#!/usr/bin/env python3
"""
Test script for Recurring Payments (Caso 1)

This script tests the complete flow of recurring payments following the
Open Payments specification.

Usage:
    python test_recurring_payments.py
"""

import requests
import json
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

# Configuration
BASE_URL = "http://localhost/v1"
# BASE_URL = "https://1270-193-32-126-143.ngrok-free.app/v1"  # Use ngrok if needed

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_step(step_num, title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}")
    print(f"STEP {step_num}: {title}")
    print(f"{'='*80}{Colors.END}\n")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ {message}{Colors.END}")

def format_json(data):
    return json.dumps(data, indent=2)


def test_recurring_payments():
    """
    Test the complete recurring payments flow.
    
    Based on: https://openpayments.dev/guides/recurring-subscription-incoming-amount/
    """
    
    print(f"\n{Colors.BOLD}{'='*80}")
    print("TESTING RECURRING PAYMENTS - CASO 1")
    print("Based on Open Payments Specification")
    print(f"{'='*80}{Colors.END}\n")
    
    # Calculate a start date/time for the interval (1 day from now)
    start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # ==========================================================================
    # STEP 6: Request Interactive Outgoing Payment Grant
    # ==========================================================================
    print_step(6, "Request Interactive Outgoing Payment Grant")
    
    # Example: Customer wants to pay $15.00 USD monthly for 12 months
    # Amount in cents: 1500 = $15.00
    payload = {
        "incoming_amount": "1500",  # $15.00 USD per payment
        "interval": f"R12/{start_date}/P1M"  # 12 monthly payments
    }
    
    print_info(f"Requesting grant with:")
    print(f"  - Incoming amount: $15.00 USD per payment")
    print(f"  - Interval: 12 monthly payments starting {start_date}")
    print(f"\nPOST {BASE_URL}/payments/recurring/start")
    print(format_json(payload))
    
    try:
        response = requests.post(
            f"{BASE_URL}/payments/recurring/start",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        grant_response = response.json()
        
        print_success("Grant request successful!")
        print(format_json(grant_response))
        
        redirect_url = grant_response.get("redirect_url")
        grant_id = grant_response.get("grant_id")
        
        if not redirect_url or not grant_id:
            print_error("Missing redirect_url or grant_id in response")
            return False
            
        print_info(f"Grant ID: {grant_id}")
        print_info(f"Redirect URL: {redirect_url}")
        
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to request grant: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False
    
    # ==========================================================================
    # STEP 7-8: User Interaction (Simulated)
    # ==========================================================================
    print_step("7-8", "User Authorization (Simulated)")
    
    print_info("In a real scenario:")
    print("  1. User would be redirected to: " + redirect_url)
    print("  2. User would authorize the payment in their wallet")
    print("  3. Authorization server would redirect back with interact_ref and hash")
    
    print(f"\n{Colors.YELLOW}⚠ MANUAL STEP REQUIRED ⚠{Colors.END}")
    print(f"\n{Colors.BOLD}Please follow these steps:{Colors.END}")
    print(f"1. Open this URL in your browser:")
    print(f"   {Colors.BLUE}{redirect_url}{Colors.END}")
    print(f"2. Authorize the payment in your wallet")
    print(f"3. After authorization, you'll be redirected to a URL like:")
    print(f"   http://localhost:3000/fulfil/recurring/{grant_id}?interact_ref=XXX&hash=YYY")
    print(f"4. Copy the values of interact_ref and hash from the URL")
    
    # Wait for user input
    print(f"\n{Colors.BOLD}Enter the callback parameters:{Colors.END}")
    interact_ref = input("interact_ref: ").strip()
    hash_value = input("hash: ").strip()
    
    if not interact_ref or not hash_value:
        print_error("interact_ref and hash are required to continue")
        return False
    
    # ==========================================================================
    # STEP 9: Grant Continuation
    # ==========================================================================
    print_step(9, "Grant Continuation")
    
    callback_url = f"{BASE_URL}/payments/recurring/callback"
    callback_params = {
        "interact_ref": interact_ref,
        "hash": hash_value,
        "grant_id": grant_id
    }
    
    print(f"GET {callback_url}")
    print(f"Parameters: {format_json(callback_params)}")
    
    try:
        response = requests.get(callback_url, params=callback_params)
        response.raise_for_status()
        callback_response = response.json()
        
        print_success("Grant continuation successful!")
        print(format_json(callback_response))
        
        if not callback_response.get("success"):
            print_error("Grant continuation failed")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to complete grant: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False
    
    # ==========================================================================
    # STEP 10: Execute First Recurring Payment (Steps 2-5, 10)
    # ==========================================================================
    print_step("2-5,10", "Execute First Recurring Payment")
    
    payment_payload = {
        "grant_id": grant_id
    }
    
    print_info("Executing first payment...")
    print(f"POST {BASE_URL}/payments/recurring/trigger")
    print(format_json(payment_payload))
    
    try:
        response = requests.post(
            f"{BASE_URL}/payments/recurring/trigger",
            json=payment_payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        payment_response = response.json()
        
        print_success("Payment executed successfully!")
        print(format_json(payment_response))
        
        # Verify payment details
        if payment_response.get("success"):
            print(f"\n{Colors.GREEN}{'='*80}")
            print("PAYMENT DETAILS:")
            print(f"  Outgoing Payment ID: {payment_response.get('outgoing_payment_id')}")
            print(f"  Incoming Payment ID: {payment_response.get('incoming_payment_id')}")
            print(f"  Quote ID: {payment_response.get('quote_id')}")
            print(f"  Debit Amount: {payment_response.get('quote_debit_amount')}")
            print(f"  Receive Amount: {payment_response.get('quote_receive_amount')}")
            print(f"  Payments Made: {payment_response.get('payments_made')}")
            print(f"  Payments Remaining: {payment_response.get('payments_remaining')}")
            print(f"{'='*80}{Colors.END}\n")
        else:
            print_error("Payment execution reported failure")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to execute payment: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False
    
    # ==========================================================================
    # Optional: Execute Additional Payments
    # ==========================================================================
    print(f"\n{Colors.BOLD}Would you like to execute additional payments? (y/n): {Colors.END}", end="")
    if input().strip().lower() == 'y':
        num_payments = int(input("How many additional payments? (max 11): ").strip())
        num_payments = min(num_payments, 11)  # Max 11 more (12 total)
        
        for i in range(num_payments):
            print_step(f"10.{i+2}", f"Execute Payment {i+2}")
            
            try:
                response = requests.post(
                    f"{BASE_URL}/payments/recurring/trigger",
                    json=payment_payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                payment_response = response.json()
                
                print_success(f"Payment {i+2} executed successfully!")
                print(f"  Payments Made: {payment_response.get('payments_made')}")
                print(f"  Payments Remaining: {payment_response.get('payments_remaining')}")
                
            except requests.exceptions.RequestException as e:
                print_error(f"Failed to execute payment {i+2}: {e}")
                break
    
    # ==========================================================================
    # Summary
    # ==========================================================================
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*80}")
    print("✓ RECURRING PAYMENTS TEST COMPLETED SUCCESSFULLY!")
    print(f"{'='*80}{Colors.END}\n")
    
    print(f"{Colors.BOLD}Summary:{Colors.END}")
    print(f"  - Grant ID: {grant_id}")
    print(f"  - Setup: Customer authorized 12 monthly payments of $15.00 USD")
    print(f"  - Executed: At least 1 payment successfully")
    print(f"  - Pattern: Fixed incoming amount recurring subscription")
    print(f"  - Reference: https://openpayments.dev/guides/recurring-subscription-incoming-amount/")
    
    return True


if __name__ == "__main__":
    print(f"\n{Colors.BOLD}Constructoken Hackathon - Recurring Payments Test{Colors.END}")
    print(f"Testing implementation based on Open Payments specification\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/payments/health", timeout=5)
        print_success(f"Server is running at {BASE_URL}")
    except requests.exceptions.RequestException:
        print_error(f"Cannot connect to server at {BASE_URL}")
        print_info("Make sure the backend is running:")
        print("  docker-compose up backend")
        print("  or")
        print("  cd backend/app && uvicorn app.main:app --reload")
        exit(1)
    
    # Run the test
    success = test_recurring_payments()
    
    if success:
        print(f"\n{Colors.GREEN}✓ All tests passed!{Colors.END}\n")
        exit(0)
    else:
        print(f"\n{Colors.RED}✗ Tests failed!{Colors.END}\n")
        exit(1)

