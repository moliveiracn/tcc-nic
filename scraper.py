# login_and_scrape.py

import os
import time
import re
import csv
import urllib.parse
import random
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from generate_search_queries import generate_grouped_queries

# ————— Config —————
STATE_PATH = "auth.json"
TWITTER_USER = os.getenv("TWITTER_USER")
TWITTER_PASS = os.getenv("TWITTER_PASS")

female_dominated = ["knitting", "baking", "scrapbooking"]
male_dominated   = ["woodworking", "fishing", "gaming"]
demeaning        = ["dumb", "pointless", "silly", "waste of time"]
ALL_HOBBIES = female_dominated + male_dominated
QUERIES     = generate_grouped_queries(ALL_HOBBIES, demeaning)

# ————— Helpers —————
def human_delay(min_s=3, max_s=7):
    time.sleep(random.uniform(min_s, max_s))

def extract_metrics(tweet):
    metrics = {}
    for kind in ("Like", "Retweet", "Reply"):
        loc = tweet.locator(f'xpath=//div[@aria-label][contains(@aria-label, "{kind}")]')
        if loc.count():
            label = loc.first.get_attribute("aria-label")
            metrics[kind.lower()] = int(re.search(r"\d+", label).group())
        else:
            metrics[kind.lower()] = 0
    return metrics

def clean_text(text):
    text = re.sub(r"http\S+", "", text)
    return re.sub(r"\s+", " ", text).strip()

def extract_entities(text):
    return {
        "hashtags": re.findall(r"#\w+", text),
        "mentions": re.findall(r"@\w+", text),
        "urls":     re.findall(r"http\S+", text),
    }

def parse_timestamp(ts_str):
    return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))

# ————— Login Flow —————
def login_twitter(page):
    page.goto("https://x.com/i/flow/login")
    page.wait_for_load_state("networkidle")

    # STEP 1: username
    try:
        if not page.is_visible('input[name="password"]'):
            page.wait_for_selector('input[name="text"]', timeout=15000)
            page.fill('input[name="text"]', TWITTER_USER)
            page.get_by_role("button", name="Next").click()
            human_delay()
    except PlaywrightTimeoutError:
        page.goto("https://x.com/i/flow/login")
        page.wait_for_selector('input[name="text"]', timeout=15000)
        page.fill('input[name="text"]', TWITTER_USER)
        page.get_by_role("button", name="Next").click()
        human_delay()

    # STEP 2: password
    page.wait_for_selector('input[name="password"]', timeout=15000)
    page.fill('input[name="password"]', TWITTER_PASS)
    page.get_by_role("button", name="Log in").click()
    human_delay()

    # STEP 3: confirm home
    page.wait_for_url("https://x.com/home", timeout=20000)
    print("✅ Logged in successfully.")

# ————— Scraper —————
def scrape_twitter_search(page, query, max_scrolls=2, scroll_pause=2):
    page.goto(f"https://x.com/search?q={urllib.parse.quote(query)}&f=live")
    time.sleep(2)
    for _ in range(max_scrolls):
        page.mouse.wheel(0, 10000)
        time.sleep(scroll_pause)

    results = []
    locator = page.locator("article")
    for i in range(locator.count()):
        t = locator.nth(i)
        try:
            handle   = t.locator('div[dir="ltr"] > span').first.text_content().strip()
            raw_text = t.locator("div[lang]").first.text_content().strip()
            ts_str   = t.locator("time").first.get_attribute("datetime")
            parent_a = t.locator("time").first.locator("..").get_attribute("href")
            tweet_url = f"https://x.com{parent_a}"
            tweet_id  = parent_a.rsplit("/", 1)[-1]

            metrics  = extract_metrics(t)
            clean    = clean_text(raw_text)
            entities = extract_entities(raw_text)

            results.append({
                "handle":     handle,
                "tweet_id":   tweet_id,
                "url":        tweet_url,
                "raw_text":   raw_text,
                "clean_text": clean,
                "timestamp":  parse_timestamp(ts_str),
                "likes":      metrics["like"],
                "retweets":   metrics["retweet"],
                "replies":    metrics["reply"],
                **entities
            })
        except:
            continue

    return results

# ————— CSV Writer —————
def write_tweets_to_csv(filename, queries, page, scrape_fn, fieldnames):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["query"] + fieldnames)
        writer.writeheader()
        for q in queries:
            print(f"🔍 Scraping query: {q}")
            tweets = []
            try:
                tweets = scrape_fn(page, q)
            except Exception as e:
                print(f"Error on '{q}': {e}")
            for t in tweets:
                row = {"query": q, **{k: t.get(k, "") for k in fieldnames}}
                writer.writerow(row)
            time.sleep(1)

def fresh_context(browser, storage_state=None):
    kwargs = {
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        ),
        "locale": "en-US",
        "timezone_id": "America/Sao_Paulo",
        "viewport": {"width": 1280, "height": 800},
    }
    if storage_state:
        kwargs["storage_state"] = storage_state

    ctx = browser.new_context(**kwargs)
    page = ctx.new_page()
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => false});")
    page.add_init_script("""
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US','en']});
        Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
    """)
    return ctx, page

# ————— Main —————
def main():
    if not TWITTER_USER or not TWITTER_PASS:
        raise RuntimeError("Set TWITTER_USER and TWITTER_PASS env vars.")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
            ],
            ignore_default_args=["--enable-automation"],
        )

        # Load or create auth state
        if os.path.exists(STATE_PATH):
            context, page = fresh_context(browser, storage_state=STATE_PATH)
            print("🔑 Loaded existing session from", STATE_PATH)
        else:
            context, page = fresh_context(browser)
            login_twitter(page)
            context.storage_state(path=STATE_PATH)
            print("💾 Saved session to", STATE_PATH)

        # Now scrape
        campos = [
            "handle", "tweet_id", "url",
            "raw_text", "clean_text", "timestamp",
            "likes", "retweets", "replies",
            "hashtags", "mentions", "urls"
        ]
        write_tweets_to_csv(
            filename="tweets_output.csv",
            queries=QUERIES,
            page=page,
            scrape_fn=scrape_twitter_search,
            fieldnames=campos
        )

        context.close()
        browser.close()

if __name__ == "__main__":
    main()
