"""
Tag utilities for enhanced tag filtering and discovery.

Provides tag categorization, aliases, and discovery functions.
"""
from typing import List, Dict, Set, Optional
from difflib import SequenceMatcher


# Tag categories for better organization
TAG_CATEGORIES = {
    "outdoor": [
        "swimming_pool", "spa_or_hot_tub", "private_backyard", "fenced_yard",
        "big_yard", "outdoor_kitchen", "rv_or_boat_parking", "rv_parking",
        "park", "playground", "greenbelt", "trails"
    ],
    "interior": [
        "fireplace", "hardwood_floors", "vaulted_ceiling", "high_ceiling",
        "open_floor_plan", "modern_kitchen", "gourmet_kitchen", "granite_kitchen",
        "updated_kitchen", "large_kitchen", "open_kitchen", "dining_room",
        "laundry_room", "master_bedroom", "master_suite", "ensuite",
        "washer_dryer", "dishwasher", "central_air", "forced_air"
    ],
    "structure": [
        "single_story", "two_or_more_stories", "basement", "detached_guest_house",
        "guest_house", "hidden_room", "new_roof", "floor_plan", "new_construction"
    ],
    "garage_parking": [
        "garage_1_or_more", "garage_2_or_more", "garage_3_or_more",
        "carport", "rv_or_boat_parking", "rv_parking"
    ],
    "lot": [
        "big_lot", "corner_lot", "cul_de_sac", "golf_course_lot_or_frontage",
        "big_yard", "fenced_yard", "private_backyard"
    ],
    "view": [
        "view", "views", "city_view", "golf_course_view", "hill_or_mountain_view",
        "mountain_view", "water_view", "waterfront", "lake"
    ],
    "community": [
        "community_swimming_pool", "community_tennis_court", "community_park",
        "community_outdoor_space", "community_security_features", "community_golf",
        "community_horse_facilities", "community_center", "gated_community",
        "clubhouse", "recreation_facilities", "hoa", "low_hoa", "no_hoa"
    ],
    "special": [
        "golf_course", "golf_course_lot_or_frontage", "horse_facilities",
        "community_horse_facilities", "tennis", "tennis_court", "farm",
        "ranch", "greenhouse"
    ],
    "features": [
        "energy_efficient", "efficient", "solar_panels", "solar_system",
        "security", "maintenance", "groundscare", "medicalcare"
    ],
    "property_type": [
        "investment_opportunity", "rental_property", "fixer_upper",
        "senior_community", "new_construction"
    ]
}

# Tag aliases - map common search terms to actual tag names
TAG_ALIASES = {
    # Pool variations
    "pool": "swimming_pool",
    "pools": "swimming_pool",
    "inground_pool": "swimming_pool",
    "private_pool": "swimming_pool",

    # Spa/Hot tub variations
    "hot_tub": "spa_or_hot_tub",
    "hottub": "spa_or_hot_tub",
    "spa": "spa_or_hot_tub",
    "jacuzzi": "spa_or_hot_tub",

    # Garage variations
    "garage": "garage_1_or_more",
    "2_car_garage": "garage_2_or_more",
    "3_car_garage": "garage_3_or_more",
    "attached_garage": "garage_1_or_more",

    # Kitchen variations
    "updated_kitchen": "modern_kitchen",
    "new_kitchen": "modern_kitchen",
    "chef_kitchen": "gourmet_kitchen",

    # View variations
    "mountain": "mountain_view",
    "mountains": "mountain_view",
    "water": "water_view",
    "lake_view": "water_view",
    "ocean": "waterfront",
    "beach": "waterfront",

    # Yard variations
    "backyard": "private_backyard",
    "yard": "big_yard",
    "fenced": "fenced_yard",
    "fence": "fenced_yard",

    # Floor variations
    "one_story": "single_story",
    "1_story": "single_story",
    "multi_story": "two_or_more_stories",
    "2_story": "two_or_more_stories",

    # Community variations
    "gated": "gated_community",
    "hoa_included": "hoa",
    "no_hoa_fee": "no_hoa",

    # Energy variations
    "solar": "solar_panels",
    "green": "energy_efficient",
    "eco_friendly": "energy_efficient",

    # Special features
    "golf": "golf_course",
    "horses": "horse_facilities",
    "equestrian": "horse_facilities",
}

# Reverse mapping: actual tag -> list of aliases
TAG_REVERSE_ALIASES: Dict[str, List[str]] = {}
for alias, actual in TAG_ALIASES.items():
    if actual not in TAG_REVERSE_ALIASES:
        TAG_REVERSE_ALIASES[actual] = []
    TAG_REVERSE_ALIASES[actual].append(alias)


def normalize_tags(tags: List[str]) -> List[str]:
    """
    Normalize tag names using aliases.

    Args:
        tags: List of tag names (can be aliases or actual tags)

    Returns:
        List of normalized tag names
    """
    normalized = []
    for tag in tags:
        tag_lower = tag.lower().strip().replace(" ", "_")
        # Check if it's an alias
        normalized_tag = TAG_ALIASES.get(tag_lower, tag_lower)
        normalized.append(normalized_tag)
    return normalized


def get_tag_category(tag: str) -> Optional[str]:
    """
    Get the category of a tag.

    Args:
        tag: Tag name

    Returns:
        Category name or None if not categorized
    """
    tag_lower = tag.lower()
    for category, category_tags in TAG_CATEGORIES.items():
        if tag_lower in category_tags:
            return category
    return None


def get_tags_by_category(category: str) -> List[str]:
    """
    Get all tags in a specific category.

    Args:
        category: Category name (outdoor, interior, structure, etc.)

    Returns:
        List of tags in that category
    """
    return TAG_CATEGORIES.get(category.lower(), [])


def discover_tags(properties_data) -> Dict[str, any]:
    """
    Discover and analyze tags from property data.

    Args:
        properties_data: DataFrame or list of properties with tags

    Returns:
        Dictionary with tag statistics and information
    """
    import pandas as pd

    # Convert to DataFrame if needed
    if isinstance(properties_data, list):
        df = pd.DataFrame(properties_data)
    else:
        df = properties_data

    # Collect all tags
    all_tags = []
    tag_counts = {}

    for tags in df.get('tags', []):
        if isinstance(tags, list):
            for tag in tags:
                all_tags.append(tag)
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Get unique tags
    unique_tags = sorted(set(all_tags))

    # Categorize tags
    categorized = {}
    uncategorized = []

    for tag in unique_tags:
        category = get_tag_category(tag)
        if category:
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(tag)
        else:
            uncategorized.append(tag)

    # Get most common tags
    most_common = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20]

    return {
        "total_unique_tags": len(unique_tags),
        "all_tags": unique_tags,
        "tag_counts": tag_counts,
        "most_common": most_common,
        "by_category": categorized,
        "uncategorized": uncategorized,
        "total_properties": len(df),
    }


def fuzzy_match_tag(search_term: str, threshold: float = 0.6) -> List[tuple]:
    """
    Find tags that fuzzy match a search term.

    Args:
        search_term: The term to search for
        threshold: Minimum similarity ratio (0.0 to 1.0)

    Returns:
        List of (tag, similarity_score) tuples, sorted by score
    """
    search_lower = search_term.lower().strip().replace(" ", "_")

    # First check for exact alias match
    if search_lower in TAG_ALIASES:
        return [(TAG_ALIASES[search_lower], 1.0)]

    # Collect all possible tags (from categories)
    all_tags = set()
    for category_tags in TAG_CATEGORIES.values():
        all_tags.update(category_tags)

    # Add all aliases
    all_tags.update(TAG_ALIASES.keys())
    all_tags.update(TAG_ALIASES.values())

    # Calculate similarity scores
    matches = []
    for tag in all_tags:
        ratio = SequenceMatcher(None, search_lower, tag).ratio()
        if ratio >= threshold:
            # If it's an alias, return the actual tag
            actual_tag = TAG_ALIASES.get(tag, tag)
            matches.append((actual_tag, ratio))

    # Sort by similarity score (highest first)
    matches.sort(key=lambda x: x[1], reverse=True)

    # Remove duplicates (keep highest score)
    seen = set()
    unique_matches = []
    for tag, score in matches:
        if tag not in seen:
            seen.add(tag)
            unique_matches.append((tag, score))

    return unique_matches


def expand_tag_search(tags: List[str], use_aliases: bool = True, use_fuzzy: bool = False,
                     fuzzy_threshold: float = 0.6) -> List[str]:
    """
    Expand a tag search to include aliases and fuzzy matches.

    Args:
        tags: List of tag search terms
        use_aliases: Whether to normalize using aliases
        use_fuzzy: Whether to include fuzzy matches
        fuzzy_threshold: Minimum similarity for fuzzy matching

    Returns:
        Expanded list of tags to search for
    """
    expanded = set()

    for tag in tags:
        tag_lower = tag.lower().strip().replace(" ", "_")

        if use_aliases:
            # Normalize to actual tag name
            normalized = TAG_ALIASES.get(tag_lower, tag_lower)
            expanded.add(normalized)

            # Also add any aliases that map to this tag
            if normalized in TAG_REVERSE_ALIASES:
                expanded.update(TAG_REVERSE_ALIASES[normalized])
        else:
            expanded.add(tag_lower)

        if use_fuzzy:
            # Add fuzzy matches
            fuzzy_matches = fuzzy_match_tag(tag_lower, fuzzy_threshold)
            for match_tag, score in fuzzy_matches[:3]:  # Top 3 matches only
                expanded.add(match_tag)

    return list(expanded)


def get_all_categories() -> List[str]:
    """Get list of all available tag categories."""
    return list(TAG_CATEGORIES.keys())


def get_category_info() -> Dict[str, int]:
    """Get information about all categories."""
    return {
        category: len(tags)
        for category, tags in TAG_CATEGORIES.items()
    }
