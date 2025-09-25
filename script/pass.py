from playwright.sync_api import sync_playwright
import json

USERNAME = "SOKIWchio163@163.com"
PASSWORD = "Zql5xLINKENpark"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  
    context = browser.new_context()
    page = context.new_page()
    
    page.goto("https://www.linkedin.com/login")
    
    page.fill('input[name="session_key"]', USERNAME)
    page.fill('input[name="session_password"]', PASSWORD)
    page.click('button[type="submit"]')
    
    page.wait_for_timeout(5000)  
    
    
    cookies = context.cookies()
    with open("linkedin_cookies.json", "w") as f:
        json.dump(cookies, f)
    
    print("ok")
    browser.close()


# GOOGLE_API_KEY = "AIzaSyC-Id2yTIB1rjddoPcdQwBoMz3B1bS6pJg"   # Google Custom Search API Key
# SEARCH_ENGINE_ID = "c78859e23e54344a3"        # Google Custom Search Engine ID
