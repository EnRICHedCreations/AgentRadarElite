"""
Smart filter presets for common property search scenarios.

Provides pre-configured filter combinations for typical use cases.
"""
from typing import Dict, Any, Optional


# Define filter presets for common search scenarios
FILTER_PRESETS = {
    "investor_friendly": {
        "description": "Properties ideal for investors - low HOA, good lot size, rental potential",
        "filters": {
            "hoa_fee_max": 100,
            "lot_sqft_min": 5000,
            "tag_filters": ["rental_property", "investment_opportunity"],
            "tag_match_type": "any",
        }
    },

    "luxury": {
        "description": "High-end luxury properties with premium features",
        "filters": {
            "price_min": 500000,
            "sqft_min": 2500,
            "baths_min": 2.5,
            "tag_filters": ["swimming_pool", "gourmet_kitchen", "high_ceiling", "view"],
            "tag_match_type": "any",
        }
    },

    "fixer_upper": {
        "description": "Properties needing work - good for flippers",
        "filters": {
            "tag_filters": ["fixer_upper", "investment_opportunity"],
            "tag_match_type": "any",
        }
    },

    "family_friendly": {
        "description": "Single-family homes in safe neighborhoods with good amenities",
        "filters": {
            "beds_min": 3,
            "baths_min": 2,
            "property_type": ["single_family"],
            "tag_filters": ["private_backyard", "community_park", "playground"],
            "tag_match_type": "any",
        }
    },

    "retirement": {
        "description": "Properties suitable for retirees - single story, low maintenance",
        "filters": {
            "stories_max": 1,
            "tag_filters": ["senior_community", "low_hoa", "community_security_features"],
            "tag_match_type": "any",
        }
    },

    "eco_friendly": {
        "description": "Energy-efficient and sustainable properties",
        "filters": {
            "tag_filters": ["solar_panels", "energy_efficient", "efficient"],
            "tag_match_type": "any",
        }
    },

    "waterfront": {
        "description": "Waterfront and water view properties",
        "filters": {
            "tag_filters": ["waterfront", "water_view", "lake"],
            "tag_match_type": "any",
            "waterfront": True,
        }
    },

    "golf_course": {
        "description": "Properties on or near golf courses",
        "filters": {
            "tag_filters": ["golf_course", "golf_course_view", "golf_course_lot_or_frontage"],
            "tag_match_type": "any",
        }
    },

    "new_construction": {
        "description": "Newly built properties",
        "filters": {
            "tag_filters": ["new_construction"],
            "tag_match_type": "all",
        }
    },

    "horse_property": {
        "description": "Properties with horse facilities",
        "filters": {
            "lot_sqft_min": 20000,
            "tag_filters": ["horse_facilities", "community_horse_facilities", "farm", "ranch"],
            "tag_match_type": "any",
        }
    },

    "starter_home": {
        "description": "Affordable starter homes for first-time buyers",
        "filters": {
            "price_max": 300000,
            "beds_min": 2,
            "baths_min": 1,
            "sqft_min": 1000,
        }
    },

    "no_hoa": {
        "description": "Properties without HOA fees",
        "filters": {
            "tag_filters": ["no_hoa"],
            "tag_match_type": "all",
        }
    },

    "pool_home": {
        "description": "Properties with swimming pools",
        "filters": {
            "has_pool": True,
            "tag_filters": ["swimming_pool"],
            "tag_match_type": "any",
        }
    },

    "gated_community": {
        "description": "Properties in gated communities with security",
        "filters": {
            "tag_filters": ["gated_community", "community_security_features"],
            "tag_match_type": "any",
        }
    },

    "mountain_view": {
        "description": "Properties with mountain or hill views",
        "filters": {
            "has_view": True,
            "tag_filters": ["mountain_view", "hill_or_mountain_view"],
            "tag_match_type": "any",
        }
    },

    "rv_parking": {
        "description": "Properties with RV or boat parking",
        "filters": {
            "tag_filters": ["rv_or_boat_parking", "rv_parking"],
            "tag_match_type": "any",
        }
    },

    "guest_house": {
        "description": "Properties with guest houses or ADUs",
        "filters": {
            "tag_filters": ["guest_house", "detached_guest_house"],
            "tag_match_type": "any",
        }
    },

    "corner_lot": {
        "description": "Properties on corner lots",
        "filters": {
            "tag_filters": ["corner_lot"],
            "tag_match_type": "all",
        }
    },

    "cul_de_sac": {
        "description": "Properties on quiet cul-de-sac streets",
        "filters": {
            "tag_filters": ["cul_de_sac"],
            "tag_match_type": "all",
        }
    },

    "open_floor_plan": {
        "description": "Modern properties with open floor plans",
        "filters": {
            "tag_filters": ["open_floor_plan", "open_kitchen", "modern_kitchen"],
            "tag_match_type": "any",
        }
    },

    "big_garage": {
        "description": "Properties with large garages (2+ cars)",
        "filters": {
            "garage_spaces_min": 2,
            "tag_filters": ["garage_2_or_more", "garage_3_or_more"],
            "tag_match_type": "any",
        }
    },

    "acreage": {
        "description": "Properties with large lots (1+ acre)",
        "filters": {
            "lot_sqft_min": 43560,  # 1 acre
            "tag_filters": ["big_lot", "farm", "ranch"],
            "tag_match_type": "any",
        }
    },

    "urban": {
        "description": "Urban properties with city amenities",
        "filters": {
            "tag_filters": ["city_view", "shopping", "maintenance", "groundscare"],
            "tag_match_type": "any",
        }
    },

    "quiet_neighborhood": {
        "description": "Peaceful properties away from busy areas",
        "filters": {
            "tag_filters": ["cul_de_sac", "greenbelt", "private_backyard", "fenced_yard"],
            "tag_match_type": "any",
        }
    },
}


def get_available_presets() -> list[str]:
    """Get list of all available preset names."""
    return sorted(FILTER_PRESETS.keys())


def get_preset_info(preset_name: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a specific preset.

    Args:
        preset_name: Name of the preset

    Returns:
        Dictionary with description and filters, or None if preset doesn't exist
    """
    return FILTER_PRESETS.get(preset_name.lower())


def get_all_presets_info() -> Dict[str, str]:
    """
    Get descriptions of all available presets.

    Returns:
        Dictionary mapping preset names to descriptions
    """
    return {
        name: info["description"]
        for name, info in FILTER_PRESETS.items()
    }


def apply_preset(preset_name: str, override_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get filter parameters for a preset, with optional overrides.

    Args:
        preset_name: Name of the preset to apply
        override_params: Optional dictionary of parameters to override preset defaults

    Returns:
        Dictionary of filter parameters

    Raises:
        ValueError: If preset_name is not found
    """
    preset_name_lower = preset_name.lower()

    if preset_name_lower not in FILTER_PRESETS:
        available = ", ".join(get_available_presets())
        raise ValueError(
            f"Unknown preset '{preset_name}'. "
            f"Available presets: {available}"
        )

    # Start with preset filters
    params = FILTER_PRESETS[preset_name_lower]["filters"].copy()

    # Apply any overrides
    if override_params:
        params.update(override_params)

    return params


def combine_presets(*preset_names: str, override_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Combine multiple presets together, with later presets taking precedence.

    Args:
        *preset_names: Names of presets to combine
        override_params: Optional dictionary of parameters to override all preset defaults

    Returns:
        Dictionary of combined filter parameters

    Raises:
        ValueError: If any preset_name is not found
    """
    combined_params = {}

    for preset_name in preset_names:
        preset_params = apply_preset(preset_name)
        combined_params.update(preset_params)

    # Handle tag_filters specially - combine them instead of replacing
    if len(preset_names) > 1:
        all_tag_filters = []
        for preset_name in preset_names:
            preset_info = get_preset_info(preset_name)
            if preset_info and "tag_filters" in preset_info["filters"]:
                all_tag_filters.extend(preset_info["filters"]["tag_filters"])

        if all_tag_filters:
            combined_params["tag_filters"] = list(set(all_tag_filters))  # Remove duplicates

    # Apply overrides
    if override_params:
        combined_params.update(override_params)

    return combined_params


def list_presets_by_category() -> Dict[str, list[str]]:
    """
    Group presets by category for easier browsing.

    Returns:
        Dictionary mapping categories to lists of preset names
    """
    categories = {
        "Investment": ["investor_friendly", "fixer_upper", "rental_property"],
        "Lifestyle": ["luxury", "retirement", "family_friendly", "starter_home"],
        "Location": ["waterfront", "golf_course", "mountain_view", "urban", "gated_community"],
        "Features": ["pool_home", "no_hoa", "eco_friendly", "new_construction", "open_floor_plan"],
        "Property Type": ["horse_property", "acreage", "guest_house"],
        "Lot Features": ["corner_lot", "cul_de_sac", "quiet_neighborhood"],
        "Parking": ["rv_parking", "big_garage"],
    }

    return categories
