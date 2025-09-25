import os
import time
import json
import random
import hashlib
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright

# -----------------------------
# 配置
# -----------------------------
GOOGLE_API_KEY = "AIzaSyC-Id2yTIB1rjddoPcdQwBoMz3B1bS6pJg"         # 替换为你的真实 API Key
SEARCH_ENGINE_ID = "c78859e23e54344a3" # 你的 CSE ID
KEYWORD = "llm hallucinations"
NUM_TOTAL = 100                          # 想抓取的总帖子数
LINKEDIN_COOKIES_FILE = "linkedin_cookies.json"
POST_FOLDER = "linkedin_posts"
MIN_DELAY = 3
MAX_DELAY = 8

# -----------------------------
# Google Custom Search API 获取帖子 URL
# -----------------------------
def get_linkedin_urls(query, total=100):
    urls = []
    for start in range(1, total+1, 10):  # 每次抓取 10 条
        params = {
            "key": GOOGLE_API_KEY,
            "cx": SEARCH_ENGINE_ID,
            "q": f"{query} site:linkedin.com/posts",
            "num": min(10, total - len(urls)),
            "start": start
        }
        resp = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
        if resp.status_code != 200:
            print(f"请求 Google API 失败: {resp.status_code}")
            break
        items = resp.json().get("items", [])
        urls.extend([item["link"] for item in items if "linkedin.com/posts" in item["link"]])
        time.sleep(random.randint(MIN_DELAY, MAX_DELAY))
        if len(urls) >= total:
            break
    return urls[:total]

# -----------------------------
# URL 转为唯一文件名
# -----------------------------
def url_to_filename(url):
    hash_id = hashlib.md5(url.encode("utf-8")).hexdigest()
    return f"{hash_id}.txt"

# -----------------------------
# Playwright 抓取帖子内容
# -----------------------------
def scrape_post(url, folder=POST_FOLDER):
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, url_to_filename(url))
    if os.path.exists(filename):
        print(f"已抓取，跳过: {url}")
        return
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        # 加载 LinkedIn cookies
        if os.path.exists(LINKEDIN_COOKIES_FILE):
            with open(LINKEDIN_COOKIES_FILE, "r") as f:
                cookies = json.load(f)
                context.add_cookies(cookies)
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(random.randint(2000, 4000))
        except Exception as e:
            print(f"访问失败: {url}", e)
            browser.close()
            return
        
        # 抓正文
        try:
            text_content = page.inner_text("div.feed-shared-update-v2__description")
        except:
            text_content = page.inner_text("body")[:2000]
        
        # 抓发布日期
        try:
            date_text = page.inner_text("span.feed-shared-actor__sub-description > span > span")
        except:
            date_text = datetime.now().strftime("%Y-%m-%d")
        
        # 抓作者
        try:
            author_text = page.inner_text("span.feed-shared-actor__name")
        except:
            author_text = "Unknown"
        
        # 保存 txt
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"URL: {url}\nDate: {date_text}\nAuthor: {author_text}\n\n{text_content}")
        print("Saved:", filename)
        
        time.sleep(random.randint(MIN_DELAY, MAX_DELAY))
        browser.close()

# -----------------------------
# 主流程
# -----------------------------
if __name__ == "__main__":
    print(f"搜索关键词: {KEYWORD}")
    urls = get_linkedin_urls(KEYWORD, NUM_TOTAL)
    print(f"找到 {len(urls)} 个帖子 URL")
    
    for url in urls:
        try:
            scrape_post(url)
        except Exception as e:
            print("抓取失败:", url, e)
