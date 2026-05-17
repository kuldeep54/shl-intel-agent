"""
Fixed scraper - uses correct CSS class 'catalogue__circle -yes' to detect
remote_testing and adaptive fields from the SHL product catalog.
"""

import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def has_yes(cell):
    """Check if a catalog cell has the '-yes' active indicator."""
    span = cell.find("span", class_="catalogue__circle")
    if span:
        classes = span.get("class", [])
        return "-yes" in classes
    return False


def scrape_page(start: int):
    """Scrape one page of the catalog."""
    url = f"{CATALOG_URL}?start={start}"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    items = []

    rows = soup.select("tr.product-catalogue__row")
    if not rows:
        rows = soup.select("tr[class*='catalogue']")
    if not rows:
        rows = soup.select("tr")

    for row in rows:
        # Skip header rows
        if row.find("th"):
            continue
        # Find the product link
        link = row.find("a", href=lambda h: h and "/product-catalog/view/" in h)
        if not link:
            continue

        name = link.get_text(strip=True)
        href = link.get("href", "")
        url_full = href if href.startswith("http") else BASE_URL + href

        # Find all cells
        cells = row.find_all("td")
        if len(cells) < 4:
            continue

        # Cell 0: name/link
        # Cell 1: remote testing (catalogue__circle -yes or not)
        # Cell 2: adaptive/IRT (catalogue__circle -yes or not)
        # Cell 3: test type key badges
        remote_testing = has_yes(cells[1])
        adaptive = has_yes(cells[2])

        # Test type badges
        type_spans = cells[3].find_all("span", class_="product-catalogue__key")
        test_types = [s.get_text(strip=True) for s in type_spans if s.get_text(strip=True)]

        items.append({
            "name": name,
            "url": url_full,
            "remote_testing": "Yes" if remote_testing else "No",
            "adaptive": "Yes" if adaptive else "No",
            "test_type": "".join(sorted(set(test_types))) if test_types else "K"
        })

    return items


def main():
    print("Scraping SHL product catalog (fixed)...")

    all_items = []
    seen_urls = set()

    for start in range(0, 500, 12):
        print(f"  Page start={start}...")
        try:
            items = scrape_page(start)
            if not items:
                print(f"  No items found at start={start}, stopping.")
                break

            new_items = 0
            for item in items:
                if item["url"] not in seen_urls:
                    seen_urls.add(item["url"])
                    all_items.append(item)
                    new_items += 1

            print(f"  Got {new_items} new items (total: {len(all_items)})")

            if new_items == 0:
                print("  No new items, stopping.")
                break

            time.sleep(0.4)
        except Exception as e:
            print(f"  Error at start={start}: {e}")
            break

    print(f"\nTotal items: {len(all_items)}")

    # Stats
    rt_yes = sum(1 for x in all_items if x["remote_testing"] == "Yes")
    ad_yes = sum(1 for x in all_items if x["adaptive"] == "Yes")
    print(f"remote_testing=Yes: {rt_yes}  No: {len(all_items)-rt_yes}")
    print(f"adaptive=Yes:       {ad_yes}  No: {len(all_items)-ad_yes}")

    output_path = r"d:\Agent\scratch\catalog_scraped_fixed.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=2)
    print(f"Saved to {output_path}")

    # Preview
    print("\nSample:")
    for item in all_items[:5]:
        print(json.dumps(item, indent=2))


if __name__ == "__main__":
    main()
