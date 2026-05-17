"""
Merges the freshly scraped catalog (with remote_testing, adaptive, test_type)
with the existing catalog.json (which has description, duration).
Result: a comprehensive catalog.json with ALL required fields.
"""
import json

# Load scraped catalog (has remote_testing, adaptive, test_type)
scraped = json.load(open(r"d:\Agent\scratch\catalog_scraped_fixed.json", encoding="utf-8"))

# Load existing catalog (has description, duration)
existing = json.load(open(r"d:\Agent\shl-recommender\catalog.json", encoding="utf-8"))

# Build lookup for scraped by URL
scraped_by_url = {item["url"]: item for item in scraped}
scraped_by_name = {item["name"].lower(): item for item in scraped}

merged = []
for item in existing:
    url = item.get("url", item.get("link", ""))
    name = item.get("name", "")
    
    # Try to find matching scraped item
    match = scraped_by_url.get(url) or scraped_by_name.get(name.lower())
    
    description = item.get("description", "")
    duration = item.get("duration", "N/A")
    
    # Determine remote_testing and adaptive as "Yes"/"No"
    remote_testing = match.get("remote_testing", "No") if match else "No"
    adaptive = match.get("adaptive", "No") if match else "No"
    
    # Normalize test_type: take first letter for individual tests
    test_type = match.get("test_type", "K") if match else "K"
    if len(test_type) > 1 and "K" in test_type:
         test_type = "K"
    elif len(test_type) > 1:
         test_type = test_type[0]
    
    merged.append({
        "name": name,
        "url": url,
        "remote_testing": remote_testing,
        "adaptive": adaptive,
        "test_type": test_type,
        "description": description,
        "duration": duration if duration else "N/A"
    })

# Save merged catalog
output_path = r"d:\Agent\shl-recommender\catalog.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(merged, f, indent=2)

print(f"Merged catalog: {len(merged)} items")
print("\nSample items:")
for item in merged[:3]:
    print(json.dumps(item, indent=2))

# Stats
rt_yes = sum(1 for x in merged if x["remote_testing"] == "Yes")
ad_yes = sum(1 for x in merged if x["adaptive"] == "Yes")
has_desc = sum(1 for x in merged if x["description"])
print(f"\nremote_testing=Yes: {rt_yes}/{len(merged)}")
print(f"adaptive=Yes: {ad_yes}/{len(merged)}")
print(f"has description: {has_desc}/{len(merged)}")
