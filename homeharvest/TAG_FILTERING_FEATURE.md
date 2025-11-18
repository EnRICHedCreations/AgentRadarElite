# Tag Filtering Feature - HomeHarvest Enhancement

## Summary

Successfully added comprehensive tag filtering functionality to the HomeHarvest real estate scraping library. This feature allows users to filter properties from Realtor.com based on property tags (amenities, features, etc.) that are already being extracted by the API.

## What Was Added

### 1. New Parameters to `scrape_property()` API

Three new parameters were added:

- **`tag_filters`**: `list[str] | None` - List of tags to filter properties by (e.g., `["pool", "garage", "new construction"]`)
- **`tag_match_type`**: `str` - How to match tags:
  - `"any"` (default): Property has at least one of the specified tags (OR logic)
  - `"all"`: Property has all of the specified tags (AND logic)
  - `"exact"`: Property tags exactly match specified tags
- **`tag_exclude`**: `list[str] | None` - List of tags to exclude from results

### 2. Implementation Details

**Files Modified:**

1. **`homeharvest/__init__.py`**
   - Added new parameters to `scrape_property()` function
   - Added validation call for tag parameters
   - Updated docstring with tag parameter documentation

2. **`homeharvest/core/scrapers/__init__.py`**
   - Added `tag_filters`, `tag_match_type`, and `tag_exclude` to `ScraperInput` model
   - Added initialization of these parameters in `Scraper.__init__()`

3. **`homeharvest/core/scrapers/realtor/__init__.py`**
   - Implemented `_apply_tag_filters()` method for client-side tag filtering
   - Integrated filter into the `search()` method pipeline
   - Supports both raw dict and Property object formats
   - Case-insensitive tag matching

4. **`homeharvest/utils.py`**
   - Added `validate_tag_filters()` function with comprehensive validation
   - Added "tags" to `ordered_properties` list for DataFrame output

## Usage Examples

### Example 1: Filter for properties with pool (OR logic)
```python
from homeharvest import scrape_property

properties = scrape_property(
    location="San Diego, CA",
    listing_type="for_sale",
    tag_filters=["swimming_pool"],
    tag_match_type="any",
    limit=100
)
```

### Example 2: Filter for properties with BOTH pool AND garage (AND logic)
```python
properties = scrape_property(
    location="Miami, FL",
    listing_type="for_sale",
    tag_filters=["swimming_pool", "garage_2_or_more"],
    tag_match_type="all",
    limit=100
)
```

### Example 3: Exclude fixer-upper properties
```python
properties = scrape_property(
    location="Austin, TX",
    listing_type="for_sale",
    tag_exclude=["fixer_upper"],
    limit=50
)
```

### Example 4: Combined with other filters
```python
properties = scrape_property(
    location="Phoenix, AZ",
    listing_type="for_sale",
    beds_min=3,
    price_max=500000,
    tag_filters=["new_construction", "energy_efficient"],
    tag_match_type="any",
    limit=100
)
```

## Available Tags

Based on sample queries, Realtor.com provides tags including (but not limited to):

- **Outdoor**: `swimming_pool`, `spa_or_hot_tub`, `big_yard`, `private_backyard`, `outdoor_kitchen`
- **Parking**: `garage_1_or_more`, `garage_2_or_more`, `garage_3_or_more`, `carport`, `rv_or_boat_parking`
- **Interior**: `fireplace`, `hardwood_floors`, `vaulted_ceiling`, `granite_kitchen`, `gourmet_kitchen`, `modern_kitchen`
- **Community**: `community_swimming_pool`, `community_tennis_court`, `clubhouse`, `community_park`, `community_security_features`
- **Property Type**: `new_construction`, `fixer_upper`, `single_story`, `two_or_more_stories`, `corner_lot`, `cul_de_sac`
- **Views**: `city_view`, `golf_course_view`, `hill_or_mountain_view`, `view`, `views`
- **Efficiency**: `energy_efficient`, `efficient`, `solar_panels`, `solar_system`
- **Special**: `guest_house`, `detached_guest_house`, `elevator`, `farm`, `ranch`

## Test Results

All tests passed successfully:

✓ **Test 1**: Found 54 properties with `swimming_pool` tag
✓ **Test 2**: Found 65 properties with `garage_2_or_more` tag
✓ **Test 3**: Found 52 properties with `fireplace OR hardwood_floors`
✓ **Test 4**: Found 16 properties with `fireplace AND hardwood_floors`
✓ **Test 5**: Successfully excluded `fixer_upper` properties (0 in results)
✓ **Validation**: Correctly rejects invalid `tag_match_type` values

## Technical Notes

- **Client-Side Filtering**: Tag filtering is applied client-side after data retrieval, similar to other advanced filters in HomeHarvest
- **Case-Insensitive**: All tag matching is case-insensitive for better UX
- **Performance**: Filtering happens in memory after pagination, so it works efficiently with the existing architecture
- **Compatibility**: Works with all return types (pandas, pydantic, raw)
- **Data Source**: Tags come directly from Realtor.com's GraphQL API

## Benefits

1. **Precise Property Targeting**: Users can find properties with specific amenities and features
2. **Better Data Quality**: Exclude unwanted properties (e.g., fixer-uppers) from analysis
3. **Flexible Matching**: Support for OR, AND, and exact match logic
4. **Easy to Use**: Simple list-based interface consistent with HomeHarvest's design
5. **No API Changes**: Uses data already being extracted, no additional API calls needed

## Future Enhancements (Optional)

- Add tag discovery/autocomplete functionality
- Create tag category groupings (exterior, interior, community, etc.)
- Add tag count/statistics to results
- Support fuzzy tag matching

---

**Feature Status**: ✅ Complete and Tested
**Implementation Date**: 2025
**Files Modified**: 4
**Lines Added**: ~150
