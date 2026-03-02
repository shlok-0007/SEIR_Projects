import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

def get_url():
    """Gets the URL from command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python filename.py <URL>")
        sys.exit(1)
    
    link = sys.argv[1].strip()
    if not link.startswith('http'):
        link = 'https://' + link
    return link

def fetch_rendered_html(link):
    print(f"Fetching the data: {link}")
    with sync_playwright() as p:
        # Launching browser
        browser = p.chromium.launch(headless=True)
        # Using a standard User-Agent to avoid being blocked
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        webpage = context.new_page()
        
        try:
            # wait_until="domcontentloaded" is the fastest way to get the HTML
            # without waiting for every single image and tracker to load.
            webpage.goto(link, wait_until="domcontentloaded")
            content = webpage.content()
            created_soup = BeautifulSoup(content, 'html.parser')
        except Exception as e:
            print(f"Error during fetch: {e}")
            sys.exit(1)
        finally:
            browser.close()
        return created_soup

def print_extracted_data(created_soup, base_url):
    """Extracts and prints the title, full continuous body, and unique links."""
    
    # 1. Extract Title
    print("\n-- TITLE --")
    print(created_soup.title.text.strip() if created_soup.title else "No Title Found")

    # 2. Extract Body (Continuous Text)
    print("\n-- FULL BODY --")
    if created_soup.body:
        # Use space separator to prevent line breaks between tags
        raw_text = created_soup.body.get_text(separator=' ', strip=True)
        # Standardize whitespace: removes all newlines (\n), tabs (\t), and extra spaces
        clean_text = " ".join(raw_text.split())
        print(clean_text)
    else:
        print("No Body Found")

    # 3. Extract Unique Links
    print("\n-- UNIQUE LINKS --")
    # Using a set comprehension to automatically remove duplicates
    unique_links = {urljoin(base_url, a['href']) for a in created_soup.find_all('a', href=True)}
    
    for link in (unique_links):
        print(link)

def main():
    # Step 1: Get URL from CLI
    link = get_url()
    
    # Step 2: Fetch HTML
    created_soup = fetch_rendered_html(link)
    
    # Step 3: Process and Print
    print_extracted_data(created_soup, link)

if __name__ == "__main__":
    main()