import os
import time
import sys
from playwright.sync_api import sync_playwright

# Import centralized utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.browser import get_shared_context_path, get_vault_root

def manage_letterly_subscription():
    # Use centralized browser context
    user_data_dir = get_shared_context_path()
    
    print(f"Starting browser with CENTRALIZED context at: {user_data_dir}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            accept_downloads=True
        )
        
        page = browser.new_page()
        
        try:
            # STEP 1: START TRIAL
            print("
--- Phase 1: Starting 7-Day Free Trial ---")
            print("Navigating to https://web.letterly.app ...")
            page.goto("https://web.letterly.app")
            
            # Wait for user to be logged in if needed
            print("Checking login status...")
            max_wait = 60 
            start_time = time.time()
            logged_in = False
            while time.time() - start_time < max_wait:
                if page.locator("text=Settings").or_(page.locator("button[aria-label='Settings']")).is_visible():
                    logged_in = True
                    break
                time.sleep(2)
            
            if not logged_in:
                print("Please log in manually if prompted. Press Enter when you see the dashboard...")
                input()

            # Look for the 7-day trial pop-up
            print("Looking for '7-day trial' pop-up...")
            trial_selectors = [
                "text=Start 7-day trial",
                "text=Claim 7-day trial",
                "button:has-text('Trial')",
                "text=Start trial"
            ]
            
            trial_btn = None
            for selector in trial_selectors:
                if page.locator(selector).is_visible():
                    trial_btn = page.locator(selector)
                    break
            
            if not trial_btn:
                print("Trial pop-up not found automatically. Waiting 10 seconds for user action...")
                time.sleep(10)
            else:
                print("Trial pop-up found! Clicking...")
                trial_btn.click()
            
            # Stripe Checkout
            print("Waiting for Stripe Checkout page...")
            try:
                page.wait_for_url("**/checkout.stripe.com/**", timeout=15000)
                print("On Stripe Checkout. Looking for 'Start trial' confirmation...")
                checkout_btn = page.locator("button:has-text('Start trial')").or_(page.locator("button:has-text('Subscribe')"))
                
                if checkout_btn.is_visible():
                    checkout_btn.click()
                    print("Trial checkout confirmed.")
                    page.wait_for_url("**/web.letterly.app/**", timeout=30000)
                else:
                    print("Checkout button not found. Please complete checkout manually. Press Enter when back on Letterly.")
                    input()
            except Exception as e:
                print(f"Stripe Checkout check: {e}. Press Enter when back on Letterly dashboard.")
                input()

            # STEP 2: CANCEL SUBSCRIPTION
            print("
--- Phase 2: Canceling Subscription ---")
            print("Navigating back to Settings...")
            page.goto("https://web.letterly.app/settings")
            
            print("Looking for Stripe Billing Portal link...")
            billing_selectors = [
                "text=Manage Subscription",
                "text=Billing",
                "text=Manage billing",
                "a:has-text('Subscription')",
                "button:has-text('Subscription')"
            ]
            
            billing_btn = None
            for selector in billing_selectors:
                if page.locator(selector).is_visible():
                    billing_btn = page.locator(selector)
                    break
            
            if not billing_btn:
                print("Could not find Billing link automatically. Press Enter once you are on the Stripe Billing page.")
                input()
            else:
                billing_btn.click()
                print("Clicked Billing link. Waiting for Stripe Portal...")
            
            # Stripe Billing Portal
            try:
                page.wait_for_url("**/billing.stripe.com/**", timeout=20000)
                print("On Stripe Billing Portal. Attempting cancellation...")
                cancel_btn = page.locator("button:has-text('Cancel plan')")
                if cancel_btn.is_visible():
                    cancel_btn.click()
                    print("Clicked 'Cancel plan'.")
                    confirm_btn = page.locator("button:has-text('Cancel plan')").last
                    if confirm_btn.is_visible():
                        confirm_btn.click()
                        print("Cancellation confirmed successfully!")
                    else:
                        print("Confirmation button not found. Complete manually and press Enter.")
                        input()
                else:
                    print("'Cancel plan' button not found. Verify manually and press Enter.")
                    input()
            except Exception as e:
                print(f"Stripe Portal navigation: {e}. Complete manually and press Enter.")
                input()

            print("
SUCCESS! Trial started and Subscription canceled.")
            
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    manage_letterly_subscription()
