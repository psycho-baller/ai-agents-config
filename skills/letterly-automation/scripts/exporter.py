import os
import time
import sys
from playwright.sync_api import sync_playwright

# Import centralized utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.browser import get_shared_context_path, get_vault_root

def export_letterly_data(vault_root):
    # Use centralized browser context
    user_data_dir = get_shared_context_path()
    unprocessed_dir = os.path.join(vault_root, "unprocessed")
    os.makedirs(unprocessed_dir, exist_ok=True)

    print(f"Starting browser with CENTRALIZED context at: {user_data_dir}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            accept_downloads=True
        )
        
        page = browser.new_page()
        
        try:
            print("Navigating to https://web.letterly.app ...")
            page.goto("https://web.letterly.app")
            
            print("Checking login status...")
            max_wait = 120 
            start_time = time.time()
            logged_in = False
            
            while time.time() - start_time < max_wait:
                settings_selectors = [
                    "text=Settings",
                    "button[aria-label='Settings']",
                    "svg[data-icon='settings']",
                    "a[href='/settings']"
                ]
                
                found_settings = False
                for selector in settings_selectors:
                    if page.locator(selector).is_visible():
                        found_settings = True
                        break
                
                if found_settings:
                    logged_in = True
                    print("
Login detected! Proceeding...")
                    break
                
                if "login" in page.url or page.locator("text=Sign in").count() > 0:
                    print(f"Waiting for login... ({int(max_wait - (time.time() - start_time))}s remaining)")
                else:
                    print(f"Waiting for dashboard... ({int(max_wait - (time.time() - start_time))}s remaining)")
                
                time.sleep(3)
            
            if not logged_in:
                print("Timeout waiting for login. Exiting.")
                browser.close()
                return

            print("Looking for 'Settings' button...")
            settings_btn = None
            for selector in settings_selectors:
                if page.locator(selector).is_visible():
                    settings_btn = page.locator(selector)
                    break
            
            if settings_btn:
                settings_btn.click()
                print("Clicked Settings.")
            else:
                print("Error: Settings button lost.")
                return
            
            print("Looking for 'Export Data'...")
            export_selectors = [
                "text=Export Data",
                "text=Export CSV",
                "button:has-text('Export')"
            ]
            
            export_btn = None
            for selector in export_selectors:
                if page.locator(selector).is_visible():
                    export_btn = page.locator(selector)
                    break
            
            if not export_btn:
                print("Could not find 'Export Data' button automatically.")
                return
            else:
                with page.expect_download() as download_info:
                    export_btn.click()
                    print("Clicked Export Data. Waiting for download...")
                
                download = download_info.value
                suggested_filename = download.suggested_filename
                
                final_path = os.path.join(unprocessed_dir, suggested_filename)
                
                if os.path.exists(final_path):
                    name, ext = os.path.splitext(suggested_filename)
                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                    final_path = os.path.join(unprocessed_dir, f"{name}_{timestamp}{ext}")
                
                download.save_as(final_path)
                print(f"
SUCCESS! CSV saved to: {final_path}")
                
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    v_root = sys.argv[1] if len(sys.argv) > 1 else get_vault_root()
    export_letterly_data(v_root)
