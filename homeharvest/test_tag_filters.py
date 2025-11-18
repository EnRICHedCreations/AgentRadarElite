"""
Test script for tag filtering functionality in HomeHarvest
"""
import sys
import io
# Set UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from homeharvest import scrape_property

def test_tag_filters():
    """Test tag filtering with various scenarios"""

    print("=" * 80)
    print("Testing HomeHarvest Tag Filtering Functionality")
    print("=" * 80)

    # Test 1: Basic tag filter with "any" match type
    print("\n[Test 1] Searching for properties with pool OR garage in San Diego, CA")
    print("-" * 80)
    try:
        properties = scrape_property(
            location="San Diego, CA",
            listing_type="for_sale",
            tag_filters=["pool", "garage"],
            tag_match_type="any",
            limit=10
        )
        print(f"✓ Found {len(properties)} properties with pool or garage")
        if len(properties) > 0:
            print(f"  Sample tags from first property: {properties.iloc[0]['tags'] if 'tags' in properties.columns else 'N/A'}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 2: Tag filter with "all" match type
    print("\n[Test 2] Searching for properties with BOTH pool AND garage in Miami, FL")
    print("-" * 80)
    try:
        properties = scrape_property(
            location="Miami, FL",
            listing_type="for_sale",
            tag_filters=["pool", "garage"],
            tag_match_type="all",
            limit=10
        )
        print(f"✓ Found {len(properties)} properties with both pool and garage")
        if len(properties) > 0:
            print(f"  Sample tags from first property: {properties.iloc[0]['tags'] if 'tags' in properties.columns else 'N/A'}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 3: Tag exclusion
    print("\n[Test 3] Searching for properties WITHOUT pool in Austin, TX")
    print("-" * 80)
    try:
        properties = scrape_property(
            location="Austin, TX",
            listing_type="for_sale",
            tag_exclude=["pool"],
            limit=10
        )
        print(f"✓ Found {len(properties)} properties without pool")
        if len(properties) > 0:
            print(f"  Sample tags from first property: {properties.iloc[0]['tags'] if 'tags' in properties.columns else 'N/A'}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 4: Combined filters with tags
    print("\n[Test 4] Searching for 3+ bed properties with new construction tag in Phoenix, AZ")
    print("-" * 80)
    try:
        properties = scrape_property(
            location="Phoenix, AZ",
            listing_type="for_sale",
            beds_min=3,
            tag_filters=["new construction"],
            tag_match_type="any",
            limit=10
        )
        print(f"✓ Found {len(properties)} properties (3+ beds, new construction)")
        if len(properties) > 0:
            print(f"  Sample property: {properties.iloc[0]['beds']} beds, tags: {properties.iloc[0]['tags'] if 'tags' in properties.columns else 'N/A'}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 5: Validation - invalid match type
    print("\n[Test 5] Testing validation - invalid tag_match_type")
    print("-" * 80)
    try:
        properties = scrape_property(
            location="Denver, CO",
            listing_type="for_sale",
            tag_filters=["pool"],
            tag_match_type="invalid",
            limit=10
        )
        print("✗ Validation failed - should have raised error")
    except ValueError as e:
        print(f"✓ Validation working correctly: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    # Test 6: Show all available tags from a sample search
    print("\n[Test 6] Displaying all unique tags from sample properties in Los Angeles, CA")
    print("-" * 80)
    try:
        properties = scrape_property(
            location="Los Angeles, CA",
            listing_type="for_sale",
            limit=50
        )
        if 'tags' in properties.columns:
            all_tags = set()
            for tags_list in properties['tags'].dropna():
                if isinstance(tags_list, list):
                    all_tags.update(tags_list)
            print(f"✓ Found {len(all_tags)} unique tags across {len(properties)} properties:")
            print(f"  {sorted(all_tags)[:20]}")  # Show first 20
        else:
            print("  Tags column not found in results")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 80)
    print("Tag Filtering Tests Complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_tag_filters()
