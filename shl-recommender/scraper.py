import requests
from bs4 import BeautifulSoup
import json

def scrape_shl_catalog():
    url = "https://www.shl.com/solutions/products/product-catalog/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    assessments = []

    # The SHL catalog has links in the format: [Name](https://www.shl.com/products/product-catalog/view/...)
    for link in soup.select("a[href*='/products/product-catalog/view/']"):
        name = link.get_text(strip=True)
        href = link.get("href", "")
        
        if name and href:
            assessments.append({
                "name": name,
                "url": href if href.startswith("http") else "https://www.shl.com" + href,
                "test_type": "A",
                "description": ""
            })

    with open("catalog.json", "w") as f:
        json.dump(assessments, f, indent=2)

    print(f"Scraped {len(assessments)} assessments")
    return assessments

if __name__ == "__main__":
    scrape_shl_catalog()
