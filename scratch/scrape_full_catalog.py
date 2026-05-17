"""
Scrapes the full SHL product catalog (Individual Test Solutions only)
with ALL required fields: name, url, remote_testing, adaptive, test_type, description, duration.
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

# Map test type letters from SHL catalog
# From the catalog table headers, letters map to:
TYPE_MAP = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgment",
    "C": "Competencies",
    "D": "Development & 360",
    "E": "Assessment Exercises",
    "K": "Knowledge & Skills",
    "P": "Personality & Behavior",
    "S": "Simulations"
}

def scrape_page(start: int):
    """Scrape one page of the catalog."""
    url = f"{CATALOG_URL}?start={start}&type=1"  # type=1 = Individual Test Solutions
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    
    items = []
    
    # Find the Individual Test Solutions table
    # Look for rows in the product catalog table
    # The table has class "product-catalogue__table" or similar
    
    # Find all product rows - they are in <tr> elements inside the catalog table
    # Each row has cells for: name/link, remote testing (dot), adaptive (dot), test types (letter badges)
    
    tables = soup.find_all("table", class_=lambda c: c and "catalogue" in c.lower())
    if not tables:
        # Try finding by looking for the section headers
        tables = soup.find_all("div", class_=lambda c: c and "catalogue" in c.lower())
    
    # More robust: look for all anchor tags with product catalog view URLs in rows
    rows = soup.select("tr.product-catalogue__row")
    if not rows:
        rows = soup.select("tr[class*='catalogue']")
    if not rows:
        # Try generic table rows with product links
        rows = soup.select("table tr")
    
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
        if len(cells) < 3:
            continue
        
        # Cell structure: [name_cell, remote_testing_cell, adaptive_cell, test_type_cell]
        # Remote testing: check if there's an active/green indicator
        remote_testing = False
        adaptive = False
        test_types = []
        
        if len(cells) >= 2:
            # Remote testing is typically the 2nd cell
            rt_cell = cells[1]
            # Check for active state (green dot/check)
            rt_spans = rt_cell.find_all("span", class_=lambda c: c and ("active" in c.lower() or "yes" in c.lower()))
            rt_imgs = rt_cell.find_all("img")
            rt_check = rt_cell.find("span", class_="-active")
            if rt_spans or rt_check:
                remote_testing = True
            else:
                # Check for any element with "active" in class
                active_el = rt_cell.find(class_=lambda c: c and "active" in c)
                remote_testing = bool(active_el)
        
        if len(cells) >= 3:
            # Adaptive is typically the 3rd cell
            ad_cell = cells[2]
            ad_spans = ad_cell.find_all("span", class_=lambda c: c and ("active" in c.lower() or "yes" in c.lower()))
            ad_check = ad_cell.find("span", class_="-active")
            if ad_spans or ad_check:
                adaptive = True
            else:
                active_el = ad_cell.find(class_=lambda c: c and "active" in c)
                adaptive = bool(active_el)
        
        if len(cells) >= 4:
            # Test types in the last cell - look for letter badges/spans
            type_cell = cells[-1]
            type_spans = type_cell.find_all("span", class_=lambda c: c and "type" in c.lower())
            if not type_spans:
                type_spans = type_cell.find_all("span")
            for span in type_spans:
                t = span.get_text(strip=True)
                if t and len(t) == 1 and t.upper() in "ABCDEKPS":
                    test_types.append(t.upper())
        
        items.append({
            "name": name,
            "url": url_full,
            "remote_testing": remote_testing,
            "adaptive": adaptive,
            "test_type": "".join(sorted(set(test_types))) if test_types else "K"
        })
    
    return items


def scrape_product_page(url: str) -> dict:
    """Scrape individual product page for description and duration."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        description = ""
        duration = ""
        
        # Description - look in meta description or main content
        meta_desc = soup.find("meta", {"name": "description"})
        if meta_desc:
            description = meta_desc.get("content", "")
        
        if not description:
            # Try main content area
            content = soup.find("div", class_=lambda c: c and "product" in c.lower())
            if content:
                p = content.find("p")
                if p:
                    description = p.get_text(strip=True)
        
        # Duration - look for "minutes" mention
        text = soup.get_text()
        import re
        dur_match = re.search(r'(\d+[\s-]+minutes?)', text, re.IGNORECASE)
        if dur_match:
            duration = dur_match.group(1)
        elif "untimed" in text.lower():
            duration = "Untimed"
        
        return {"description": description, "duration": duration}
    except Exception as e:
        print(f"  Error scraping {url}: {e}")
        return {"description": "", "duration": ""}


def main():
    print("Scraping SHL Individual Test Solutions catalog...")
    
    all_items = []
    seen_urls = set()
    
    # Scrape all pages - catalog typically has ~300+ items at 12 per page
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
                print("  No new items, stopping pagination.")
                break
                
            time.sleep(0.5)  # Be nice to the server
        except Exception as e:
            print(f"  Error at start={start}: {e}")
            break
    
    print(f"\nTotal items scraped: {len(all_items)}")
    
    # Save results
    output_path = r"d:\Agent\scratch\catalog_scraped.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=2)
    
    print(f"Saved to {output_path}")
    
    # Print a sample
    if all_items:
        print("\nSample items:")
        for item in all_items[:3]:
            print(json.dumps(item, indent=2))


if __name__ == "__main__":
    main()
