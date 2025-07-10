from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import sys
import time
import logging
import urllib
import traceback
import re
from selenium.common.exceptions import (
    WebDriverException, 
    NoSuchWindowException,
    SessionNotCreatedException,
    TimeoutException
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configure Chrome options (visible GUI mode)
print("Configuring Chrome options for visible GUI mode...")
logging.info("Setting up Chrome with visible browser window")
chrome_options = Options()
# Removed --headless to make browser visible
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--start-maximized')  # Start with maximized window

# Browser management functions
def initialize_browser():
    """Initialize and return a new browser instance."""
    print("Initializing WebDriver...")
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=chrome_options
        )
        # Load a blank page to ensure valid initial state
        driver.get("about:blank")
        print("Browser initialized successfully")
        return driver
    except Exception as e:
        print(f"❌ Failed to initialize browser: {e}")
        raise

def is_browser_alive(driver):
    """Check if the browser is still responsive."""
    try:
        # A simple operation to check browser responsiveness
        _ = driver.current_url
        return True
    except Exception:
        return False
        
def get_first_line(text):
    """Extract the first line from a multi-line error message."""
    if not text:
        return ""
    # Split by newline and return first non-empty line
    lines = re.split(r'[\r\n]+', str(text))
    return next((line for line in lines if line.strip()), str(text))

# Initialize WebDriver with automatic ChromeDriver management
driver = initialize_browser()

# Initialize the interactive browser control
print("Starting interactive browser control...")
def interactive_loop(driver):
    """Interactively control the web browser."""
    def print_usage():
        print("\nAvailable commands:")
        print("  visit <url>  - Go to a website (e.g., visit https://www.example.com)")
        print("  title        - Display the current page title")
        print("  url          - Display the current page URL")
        print("  back         - Go back to the previous page")
        print("  forward      - Go forward to the next page")
        print("  refresh      - Refresh the current page")
        print("  status       - Check browser health status")
        print("  restart      - Restart the browser if it's not responding")
        print("  help         - Show this help message")
        print("  quit         - Exit the browser\n")

    print("\nInteractive browser control. Type 'help' for available commands.\n")
    print_usage()

    browser_working = True
    
    while True:
        command = input("Enter command: ").strip()
        
        # Commands that should work even if browser is down
        if command == "quit":
            break
        elif command == "help":
            print_usage()
            continue
        elif command == "restart":
            try:
                print("Attempting to restart browser...")
                if driver:
                    try:
                        driver.quit()
                    except Exception:
                        pass  # Ignore errors on quit
                driver = initialize_browser()
                browser_working = True
                print("✅ Browser restarted successfully")
                continue
            except Exception as e:
                print(f"❌ Failed to restart browser: {e}")
                browser_working = False
                continue
        elif command == "status":
            alive = is_browser_alive(driver)
            browser_working = alive
            if alive:
                print("✅ Browser is healthy and responding")
                print(f"   Current URL: {driver.current_url}")
            else:
                print("❌ Browser is not responding")
                print("   Try using the 'restart' command")
            continue
        
        # Check browser health before executing other commands
        if not is_browser_alive(driver):
            print("❌ Browser is not responding. Use 'restart' to reconnect or 'quit' to exit.")
            browser_working = False
            continue
        
        # Browser is healthy, execute command
        try:
            if command.startswith("visit"):
                try:
                    parts = command.split(" ", 1)
                    if len(parts) < 2:
                        print("❌ Please provide a URL (e.g., visit https://www.example.com)")
                        continue
                        
                    url = parts[1].strip()
                    
                    # Add https:// if missing but looks like a domain
                    if not (url.startswith("http://") or url.startswith("https://")):
                        if "." in url and " " not in url:
                            url = "https://" + url
                            print(f"Adding https:// prefix. Using: {url}")
                        else:
                            print("❌ Invalid URL format. Make sure it starts with http:// or https://")
                            continue
                            
                    print(f"Navigating to {url}...")
                    logging.info(f"Navigating to {url}")
                    
                    # Set a page load timeout
                    driver.set_page_load_timeout(30)
                    driver.get(url)
                    
                    # Reset timeout
                    driver.set_page_load_timeout(300)
                    print(f"✅ Successfully loaded: {url}")
                except TimeoutException:
                    print(f"⚠️ Page load timed out. The site might be slow or unavailable.")
                except Exception as e:
                    print(f"❌ Failed to load URL: {get_first_line(e)}")
            elif command == "title":
                title = driver.title
                print(f"Current page title: {title if title else '(No title)'}")
            elif command == "url":
                url = driver.current_url
                print(f"Current page URL: {url if url != 'data:,' else 'about:blank'}")
            elif command == "back":
                try:
                    print("Going back to previous page...")
                    logging.info("Navigating back")
                    driver.back()
                    time.sleep(0.5)  # Brief pause to let page load start
                    print(f"✅ Now at: {driver.current_url}")
                except Exception as e:
                    print(f"❌ Failed to go back: {get_first_line(e)}")
            elif command == "forward":
                try:
                    print("Going forward to next page...")
                    logging.info("Navigating forward")
                    driver.forward()
                    time.sleep(0.5)  # Brief pause to let page load start
                    print(f"✅ Now at: {driver.current_url}")
                except Exception as e:
                    print(f"❌ Failed to go forward: {get_first_line(e)}")
            elif command == "refresh":
                try:
                    print("Refreshing current page...")
                    logging.info("Refreshing page")
                    driver.refresh()
                    print(f"✅ Page refreshed: {driver.current_url}")
                except Exception as e:
                    print(f"❌ Failed to refresh page: {get_first_line(e)}")
            else:
                print(f"❌ Unknown command: {command}")
                print("Type 'help' to see available commands.")
        except IndexError:
            print("❌ Please provide the required information for this command.")
        except NoSuchWindowException:
            print("❌ Browser window was closed. Use 'restart' to create a new session.")
            browser_working = False
        except WebDriverException as e:
            print(f"❌ Browser error: {get_first_line(e)}")
            error_text = str(e)
            if "no such window" in error_text or "target window already closed" in error_text:
                print("   The browser window appears to be closed. Try using 'restart'.")
                browser_working = False
        except Exception as e:
            print(f"❌ An error occurred: {get_first_line(e)}")
            if "url" in locals():
                print(f"   While trying to navigate to: {url}")
            logging.error(f"Exception: {e}")
            logging.debug(traceback.format_exc())

# Enter the interactive control loop
try:
    interactive_loop(driver)
except KeyboardInterrupt:
    print("\nBrowser control interrupted by user.")
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")
    logging.error(f"Unexpected error: {e}")
    logging.debug(traceback.format_exc())
finally:
    # Clean up
    print("\nClosing browser...")
    logging.info("Shutting down browser")
    try:
        if driver:
            driver.quit()
    except Exception as e:
        logging.error(f"Error closing browser: {e}")
    print("Script completed successfully!")
    logging.info("Browser automation completed")
