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
            print("\n--- Phase 1: Starting 7-Day Free Trial ---")
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
                if page.locator(selector).first.is_visible():
                    trial_btn = page.locator(selector).first
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
                page.wait_for_url("**/checkout.stripe.com/**", timeout=25000)
                print("On Stripe Checkout. Looking for 'Start trial' button...")
                
                # Precise selector using data-testid provided by user
                # Using wait_for instead of is_visible to handle loading states
                checkout_btn = page.locator("button[data-testid='hosted-payment-submit-button']").filter(has_text="Start trial")
                
                print("Waiting for button to become ready...")
                checkout_btn.wait_for(state="visible", timeout=15000)
                
                print("Clicking 'Start trial' button...")
                checkout_btn.click()
                print("Trial checkout initiated. Waiting for redirect...")
                page.wait_for_url("**/web.letterly.app/**", timeout=45000)
            except Exception as e:
                print(f"Stripe Checkout error: {e}")
                print("Please complete checkout manually. Press Enter when back on Letterly dashboard.")
                input()

            # STEP 2: CANCEL SUBSCRIPTION
            print("\n--- Phase 2: Canceling Subscription ---")
            print("Navigating to Dashboard...")
            page.goto("https://web.letterly.app")
            
            # Explicitly click settings to ensure sidebar/menu is open
            print("Opening Settings...")
            settings_selectors = [
                "text=Settings",
                "button[aria-label='Settings']",
                "a[href='/settings']"
            ]
            
            settings_btn = None
            for selector in settings_selectors:
                if page.locator(selector).first.is_visible():
                    settings_btn = page.locator(selector).first
                    break
            
            if settings_btn:
                settings_btn.click()
                print("Clicked Settings.")
            else:
                print("Navigating directly to settings URL...")
                page.goto("https://web.letterly.app/settings")
            
            print("Looking for 'Manage Subscription' link...")
            billing_selectors = [
                "text=Manage Subscription",
                "text=Manage billing",
                "button:has-text('Subscription')",
                "a:has-text('Subscription')"
            ]
            
            billing_link = None
            # Allow time for dynamic settings to load
            page.wait_for_timeout(3000)
            for selector in billing_selectors:
                loc = page.locator(selector).first
                if loc.is_visible():
                    billing_link = loc
                    break
            
            if not billing_link:
                print("Could not find Billing link automatically. Complete manually on Stripe. Press Enter when done.")
                input()
            else:
                billing_link.click()
                print("Clicked link. Waiting for Stripe Portal...")
            
            # Stripe Billing Portal
            try:
                page.wait_for_url("**/billing.stripe.com/**", timeout=25000)
                print("On Stripe Billing Portal. Attempting cancellation...")
                
                cancel_btn = page.locator("button:has-text('Cancel plan')").first
                cancel_btn.wait_for(state="visible", timeout=15000)
                cancel_btn.click()
                print("Clicked 'Cancel plan'.")
                
                # Confirm step
                confirm_btn = page.locator("button[data-testid='cancel-button']").or_(page.locator("button:has-text('Cancel plan')").last)
                confirm_btn.wait_for(state="visible", timeout=15000)
                confirm_btn.click()
                print("Cancellation confirmed successfully!")
            except Exception as e:
                print(f"Stripe Portal error: {e}. Complete manually and press Enter.")
                input()

            print("\nSUCCESS! Trial started and Subscription canceled.")
            
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    manage_letterly_subscription()
