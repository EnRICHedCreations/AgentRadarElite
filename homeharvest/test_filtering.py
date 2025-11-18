"""
Test tag filtering functionality
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from homeharvest import scrape_property

print("Testing Tag Filtering")
print("=" * 80)

# Test filtering for pool
print("\n[Test 1] Filter for properties with 'swimming_pool' tag...")
properties = scrape_property(
    location="Scottsdale, AZ",
    listing_type="for_sale",
    tag_filters=["swimming_pool"],
    tag_match_type="any",
    limit=100
)

print(f"Found {len(properties)} properties with swimming_pool tag")

if len(properties) > 0:
    sample = properties.iloc[0]
    print(f"\nSample property:")
    print(f"  Address: {sample.get('formatted_address', 'N/A')}")
    print(f"  Price: ${sample.get('list_price', 'N/A'):,.0f}")
    print(f"  Tags: {sample.get('tags', [])}")

# Test filtering for garage
print("\n[Test 2] Filter for properties with garage (2 or more)...")
properties = scrape_property(
    location="Phoenix, AZ",
    listing_type="for_sale",
    tag_filters=["garage_2_or_more"],
    tag_match_type="any",
    limit=100
)

print(f"Found {len(properties)} properties with garage_2_or_more tag")

if len(properties) > 0:
    sample = properties.iloc[0]
    print(f"\nSample property:")
    print(f"  Address: {sample.get('formatted_address', 'N/A')}")
    print(f"  Price: ${sample.get('list_price', 'N/A'):,.0f}")
    print(f"  Beds/Baths: {sample.get('beds', 'N/A')}/{sample.get('full_baths', 'N/A')}")
    print(f"  Tags: {sample.get('tags', [])}")

# Test with multiple tags (OR logic)
print("\n[Test 3] Filter for properties with fireplace OR hardwood_floors...")
properties = scrape_property(
    location="Phoenix, AZ",
    listing_type="for_sale",
    tag_filters=["fireplace", "hardwood_floors"],
    tag_match_type="any",
    limit=100
)

print(f"Found {len(properties)} properties with fireplace OR hardwood_floors")

# Test with ALL logic
print("\n[Test 4] Filter for properties with BOTH fireplace AND hardwood_floors...")
properties = scrape_property(
    location="Phoenix, AZ",
    listing_type="for_sale",
    tag_filters=["fireplace", "hardwood_floors"],
    tag_match_type="all",
    limit=100
)

print(f"Found {len(properties)} properties with BOTH fireplace AND hardwood_floors")

if len(properties) > 0:
    sample = properties.iloc[0]
    print(f"\nSample property:")
    print(f"  Address: {sample.get('formatted_address', 'N/A')}")
    print(f"  Tags: {sample.get('tags', [])}")

# Test exclusion
print("\n[Test 5] Filter for properties EXCLUDING fixer_upper...")
properties = scrape_property(
    location="Phoenix, AZ",
    listing_type="for_sale",
    tag_exclude=["fixer_upper"],
    limit=50
)

print(f"Found {len(properties)} properties excluding fixer_upper")

# Verify no fixer_upper tags in results
fixer_count = 0
for idx, row in properties.iterrows():
    tags = row.get('tags', [])
    if tags and 'fixer_upper' in tags:
        fixer_count += 1

print(f"Properties with fixer_upper tag (should be 0): {fixer_count}")

print("\n" + "=" * 80)
print("All tests complete!")
