import os
import time
from playwright.sync_api import sync_playwright

def export_letterly_data():
    # Define paths
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    user_data_dir = os.path.join(skill_dir, "chrome_context")
    vault_dest_dir = os.path.abspath(os.path.join(os.getcwd(), "My Outputs/Transcriptions"))

    # Ensure directories exist
    os.makedirs(user_data_dir, exist_ok=True)
    os.makedirs(vault_dest_dir, exist_ok=True)

    print(f"Starting browser with persistent context at: {user_data_dir}")
    
    with sync_playwright() as p:
        # We use Playwright's bundled Chromium (installed via 'playwright install chromium')
        # This is a standalone binary that won't interfere with your Arc, Brave, or Zen.
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False, # Must be False to allow manual login if needed
            accept_downloads=True
        )
        
        page = browser.new_page()
        
        try:
            print("Navigating to https://web.letterly.app ...")
            # Relaxed wait condition to prevent timeouts on background network activity
            page.goto("https://web.letterly.app")
            
            # Check if redirected to login
            print("Checking login status...")
            # We will wait up to 120 seconds for the user to log in manually
            max_wait = 120 
            start_time = time.time()
            logged_in = False
            
            while time.time() - start_time < max_wait:
                # Check for dashboard indicators (Settings button)
                # Settings selector from below
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
                    print("\nLogin detected! Proceeding...")
                    break
                
                if "login" in page.url or page.locator("text=Sign in").count() > 0:
                    print(f"Waiting for login... ({int(max_wait - (time.time() - start_time))}s remaining) - Please log in manually in the browser window.")
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
            # User says: "bottom of that sidebar is where we have export data"
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
                print("Could not find 'Export Data' button automatically. Please find it and press Enter when ready to click (or click it yourself).")
                input()
            else:
                 # Setup download listener before clicking
                with page.expect_download() as download_info:
                    export_btn.click()
                    print("Clicked Export Data. Waiting for download...")
                
                download = download_info.value
                suggested_filename = download.suggested_filename
                
                # Move to Obsidian vault
                final_path = os.path.join(vault_dest_dir, suggested_filename)
                
                # Check if file exists, if so, append timestamp
                if os.path.exists(final_path):
                    name, ext = os.path.splitext(suggested_filename)
                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                    final_path = os.path.join(vault_dest_dir, f"{name}_{timestamp}{ext}")
                
                download.save_as(final_path)
                print(f"\nSUCCESS! File saved to: {final_path}")
                
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    export_letterly_data()