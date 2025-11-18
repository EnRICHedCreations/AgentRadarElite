"""
Simple test to verify tag filtering works and display available tags
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from homeharvest import scrape_property

# Test 1: Get a small sample to see what tags are available
print("Fetching sample properties to see available tags...")
print("=" * 80)

properties = scrape_property(
    location="Phoenix, AZ",
    listing_type="for_sale",
    limit=20
)

print(f"\nFound {len(properties)} properties")
print(f"Columns: {list(properties.columns)}")

if 'tags' in properties.columns:
    print("\n✓ Tags column is present!")

    # Show unique tags
    all_tags = set()
    for tags_list in properties['tags'].dropna():
        if isinstance(tags_list, list):
            all_tags.update(tags_list)

    print(f"\nUnique tags found ({len(all_tags)}):")
    for tag in sorted(all_tags)[:30]:  # Show first 30
        print(f"  - {tag}")

    # Show sample property with tags
    props_with_tags = properties[properties['tags'].notna()]
    if len(props_with_tags) > 0:
        sample = props_with_tags.iloc[0]
        print(f"\nSample property:")
        print(f"  Address: {sample.get('formatted_address', 'N/A')}")
        print(f"  Price: ${sample.get('list_price', 'N/A'):,.0f}")
        print(f"  Tags: {sample.get('tags', [])}")
else:
    print("\n✗ Tags column not found")

print("\n" + "=" * 80)
print("Done!")
