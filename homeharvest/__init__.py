import warnings
import pandas as pd
from datetime import datetime, timedelta, date
from .core.scrapers import ScraperInput
from .utils import (
    process_result, ordered_properties, validate_input, validate_dates, validate_limit,
    validate_offset, validate_datetime, validate_filters, validate_sort, validate_last_update_filters,
    validate_tag_filters, convert_to_datetime_string, extract_timedelta_hours, extract_timedelta_days, detect_precision_and_convert
)
from .core.scrapers.realtor import RealtorScraper
from .core.scrapers.models import ListingType, SearchPropertyType, ReturnType, Property
from .tag_utils import (
    discover_tags, normalize_tags, get_tag_category, get_tags_by_category,
    fuzzy_match_tag, expand_tag_search, get_all_categories, get_category_info,
    TAG_CATEGORIES, TAG_ALIASES
)
from .presets import (
    get_available_presets, get_preset_info, get_all_presets_info,
    apply_preset, combine_presets, list_presets_by_category,
    FILTER_PRESETS
)
from .data_cleaning import (
    clean_dataframe, validate_property_data, get_data_quality_report,
    clean_price, clean_sqft, clean_beds_baths, clean_year, clean_tags
)
from .sorting import (
    sort_properties, get_best_deals, get_newest_listings, get_recently_updated,
    rank_by_investment_potential, create_custom_score, get_available_sort_fields,
    SORTABLE_FIELDS
)
from .agent_broker import (
    get_agent_activity, get_broker_activity, get_office_activity,
    find_most_active_agents, find_properties_by_agent, find_properties_by_broker,
    get_contact_export, analyze_agent_specialization, get_wholesale_friendly_agents,
    filter_by_agent_contact, format_contact_info, extract_phone_numbers
)
from typing import Union, Optional, List, Dict

def scrape_property(
    location: str,
    listing_type: str | list[str] | None = None,
    return_type: str = "pandas",
    preset: str = None,
    property_type: Optional[List[str]] = None,
    radius: float = None,
    mls_only: bool = False,
    past_days: int | timedelta = None,
    proxy: str = None,
    date_from: datetime | date | str = None,
    date_to: datetime | date | str = None,
    foreclosure: bool = None,
    extra_property_data: bool = True,
    exclude_pending: bool = False,
    limit: int = 10000,
    offset: int = 0,
    # New date/time filtering parameters
    past_hours: int | timedelta = None,
    # New last_update_date filtering parameters
    updated_since: datetime | str = None,
    updated_in_past_hours: int | timedelta = None,
    # New property filtering parameters
    beds_min: int = None,
    beds_max: int = None,
    baths_min: float = None,
    baths_max: float = None,
    sqft_min: int = None,
    sqft_max: int = None,
    price_min: int = None,
    price_max: int = None,
    lot_sqft_min: int = None,
    lot_sqft_max: int = None,
    year_built_min: int = None,
    year_built_max: int = None,
    # New sorting parameters
    sort_by: Union[str, List[str]] = None,
    sort_direction: Union[str, List[str]] = "desc",
    enable_advanced_sort: bool = False,
    # Tag filtering parameters
    tag_filters: Optional[List[str]] = None,
    tag_match_type: str = "any",
    tag_exclude: Optional[List[str]] = None,
    tag_use_aliases: bool = True,
    tag_use_fuzzy: bool = False,
    tag_fuzzy_threshold: float = 0.6,
    # Additional property filters
    hoa_fee_min: int = None,
    hoa_fee_max: int = None,
    stories_min: int = None,
    stories_max: int = None,
    garage_spaces_min: int = None,
    garage_spaces_max: int = None,
    has_pool: bool = None,
    has_garage: bool = None,
    waterfront: bool = None,
    has_view: bool = None,
    # Data quality control
    clean_data: bool = True,
    add_derived_fields: bool = True,
    # Agent/Broker filtering
    require_agent_email: bool = False,
    require_agent_phone: bool = False,
    # Pagination control
    parallel: bool = True,
) -> Union[pd.DataFrame, list[dict], list[Property]]:
    """
    Scrape properties from Realtor.com based on a given location and listing type.

    :param location: Location to search (e.g. "Dallas, TX", "85281", "2530 Al Lipscomb Way")
    :param listing_type: Listing Type - can be a string, list of strings, or None.
        Options: for_sale, for_rent, sold, pending, off_market, new_community, other, ready_to_build
        Examples: "for_sale", ["for_sale", "pending"], None (returns all types)
    :param return_type: Return type (pandas, pydantic, raw)
    :param preset: Apply a predefined filter preset. Options include: investor_friendly, luxury, fixer_upper,
        family_friendly, retirement, eco_friendly, waterfront, golf_course, new_construction, horse_property,
        starter_home, no_hoa, pool_home, gated_community, mountain_view, rv_parking, guest_house, corner_lot,
        cul_de_sac, open_floor_plan, big_garage, acreage, urban, quiet_neighborhood.
        Use get_available_presets() to see all presets or get_all_presets_info() for descriptions.
        Individual parameters will override preset values.
    :param property_type: Property Type (single_family, multi_family, condos, condo_townhome_rowhome_coop, condo_townhome, townhomes, duplex_triplex, farm, land, mobile)
    :param radius: Get properties within _ (e.g. 1.0) miles. Only applicable for individual addresses.
    :param mls_only: If set, fetches only listings with MLS IDs.
    :param proxy: Proxy to use for scraping
    :param past_days: Get properties sold or listed (dependent on your listing_type) in the last _ days.
        - PENDING: Filters by pending_date. Contingent properties without pending_date are included.
        - SOLD: Filters by sold_date (when property was sold)
        - FOR_SALE/FOR_RENT: Filters by list_date (when property was listed)
    :param date_from, date_to: Get properties sold or listed (dependent on your listing_type) between these dates.
        Accepts multiple formats for flexible precision:
        - Date strings: "2025-01-20" (day-level precision)
        - Datetime strings: "2025-01-20T14:30:00" (hour-level precision)
        - date objects: date(2025, 1, 20) (day-level precision)
        - datetime objects: datetime(2025, 1, 20, 14, 30) (hour-level precision)
        The precision is automatically detected based on the input format.
        Timezone handling: Naive datetimes are treated as local time and automatically converted to UTC.
        Timezone-aware datetimes are converted to UTC. For best results, use timezone-aware datetimes.
    :param foreclosure: If set, fetches only foreclosure listings.
    :param extra_property_data: Increases requests by O(n). If set, this fetches additional property data (e.g. agent, broker, property evaluations etc.)
    :param exclude_pending: If true, this excludes pending or contingent properties from the results, unless listing type is pending.
    :param limit: Limit the number of results returned. Maximum is 10,000.
    :param offset: Starting position for pagination within the 10k limit (offset + limit cannot exceed 10,000). Use with limit to fetch results in chunks (e.g., offset=200, limit=200 fetches results 200-399). Should be a multiple of 200 (page size) for optimal performance. Default is 0. Note: Cannot be used to bypass the 10k API limit - use date ranges (date_from/date_to) to narrow searches and fetch more data.

    New parameters:
    :param past_hours: Get properties in the last _ hours (requires client-side filtering). Accepts int or timedelta.
    :param updated_since: Filter by last_update_date (when property was last updated). Accepts datetime object or ISO 8601 string (client-side filtering).
        Timezone handling: Naive datetimes (like datetime.now()) are treated as local time and automatically converted to UTC.
        Timezone-aware datetimes are converted to UTC. Examples:
        - datetime.now() - uses your local timezone
        - datetime.now(timezone.utc) - uses UTC explicitly
    :param updated_in_past_hours: Filter by properties updated in the last _ hours. Accepts int or timedelta (client-side filtering)
    :param beds_min, beds_max: Filter by number of bedrooms
    :param baths_min, baths_max: Filter by number of bathrooms
    :param sqft_min, sqft_max: Filter by square footage
    :param price_min, price_max: Filter by listing price
    :param lot_sqft_min, lot_sqft_max: Filter by lot size
    :param year_built_min, year_built_max: Filter by year built
    :param sort_by: Sort results by field or list of fields. Supports: list_date, sold_date, list_price, sqft, beds, baths,
        last_update_date, price_per_sqft, days_on_mls, hoa_fee, lot_sqft, year_built, and calculated fields like property_age.
        Can be a single field or list of fields for multi-level sorting.
    :param sort_direction: Sort direction "asc" or "desc", or list matching sort_by for multi-field sorts.
    :param enable_advanced_sort: If True, use advanced sorting with calculated fields. Default is False.
    :param tag_filters: List of tags to filter properties by (e.g. ["pool", "garage", "new construction"]). Client-side filtering.
        Supports aliases (e.g. "pool" → "swimming_pool") and fuzzy matching for flexibility.
    :param tag_match_type: How to match tags - "any" (has at least one tag), "all" (has all tags), or "exact" (tags exactly match). Default is "any".
    :param tag_exclude: List of tags to exclude from results. Properties with any of these tags will be filtered out.
    :param tag_use_aliases: If True, automatically normalize tag names using aliases (e.g. "pool" → "swimming_pool"). Default is True.
    :param tag_use_fuzzy: If True, include fuzzy matches for tags (e.g. "pools" matches "swimming_pool"). Default is False.
    :param tag_fuzzy_threshold: Minimum similarity ratio (0.0-1.0) for fuzzy tag matching. Default is 0.6.
    :param hoa_fee_min, hoa_fee_max: Filter by HOA fee range
    :param stories_min, stories_max: Filter by number of stories
    :param garage_spaces_min, garage_spaces_max: Filter by number of garage spaces
    :param has_pool: Filter for properties with pool (True) or without pool (False)
    :param has_garage: Filter for properties with garage (True) or without garage (False)
    :param waterfront: Filter for waterfront properties
    :param has_view: Filter for properties with views (ocean, mountain, city, etc.)
    :param clean_data: If True, automatically clean and validate property data (prices, sqft, dates, etc.). Default is True.
    :param add_derived_fields: If True, add calculated fields like price_per_sqft. Default is True.
    :param require_agent_email: If True, only return properties with agent email addresses. Default is False.
    :param require_agent_phone: If True, only return properties with agent phone numbers. Default is False.
    :param parallel: Controls pagination strategy. True (default) = fetch all pages in parallel for maximum speed.
        False = fetch pages sequentially with early termination checks (useful for rate limiting or narrow time windows).
        Sequential mode will stop paginating as soon as time-based filters indicate no more matches are possible.

    Note: past_days and past_hours also accept timedelta objects for more Pythonic usage.
    """
    # Apply preset if specified
    preset_params = {}
    if preset:
        preset_params = apply_preset(preset)

        # Apply preset parameters if not explicitly overridden
        # Build a dictionary of all explicit parameters
        explicit_params = {
            k: v for k, v in locals().items()
            if v is not None and k not in ['location', 'listing_type', 'return_type', 'preset', 'preset_params']
        }

        # For each preset parameter, use it if not explicitly provided
        for param_name, param_value in preset_params.items():
            if param_name not in explicit_params:
                locals()[param_name] = param_value

        # Update the local variables with preset values
        if 'property_type' in preset_params and property_type is None:
            property_type = preset_params['property_type']
        if 'beds_min' in preset_params and beds_min is None:
            beds_min = preset_params['beds_min']
        if 'beds_max' in preset_params and beds_max is None:
            beds_max = preset_params['beds_max']
        if 'baths_min' in preset_params and baths_min is None:
            baths_min = preset_params['baths_min']
        if 'baths_max' in preset_params and baths_max is None:
            baths_max = preset_params['baths_max']
        if 'sqft_min' in preset_params and sqft_min is None:
            sqft_min = preset_params['sqft_min']
        if 'sqft_max' in preset_params and sqft_max is None:
            sqft_max = preset_params['sqft_max']
        if 'price_min' in preset_params and price_min is None:
            price_min = preset_params['price_min']
        if 'price_max' in preset_params and price_max is None:
            price_max = preset_params['price_max']
        if 'lot_sqft_min' in preset_params and lot_sqft_min is None:
            lot_sqft_min = preset_params['lot_sqft_min']
        if 'lot_sqft_max' in preset_params and lot_sqft_max is None:
            lot_sqft_max = preset_params['lot_sqft_max']
        if 'year_built_min' in preset_params and year_built_min is None:
            year_built_min = preset_params['year_built_min']
        if 'year_built_max' in preset_params and year_built_max is None:
            year_built_max = preset_params['year_built_max']
        if 'hoa_fee_min' in preset_params and hoa_fee_min is None:
            hoa_fee_min = preset_params['hoa_fee_min']
        if 'hoa_fee_max' in preset_params and hoa_fee_max is None:
            hoa_fee_max = preset_params['hoa_fee_max']
        if 'stories_min' in preset_params and stories_min is None:
            stories_min = preset_params['stories_min']
        if 'stories_max' in preset_params and stories_max is None:
            stories_max = preset_params['stories_max']
        if 'garage_spaces_min' in preset_params and garage_spaces_min is None:
            garage_spaces_min = preset_params['garage_spaces_min']
        if 'garage_spaces_max' in preset_params and garage_spaces_max is None:
            garage_spaces_max = preset_params['garage_spaces_max']
        if 'has_pool' in preset_params and has_pool is None:
            has_pool = preset_params['has_pool']
        if 'has_garage' in preset_params and has_garage is None:
            has_garage = preset_params['has_garage']
        if 'waterfront' in preset_params and waterfront is None:
            waterfront = preset_params['waterfront']
        if 'has_view' in preset_params and has_view is None:
            has_view = preset_params['has_view']
        if 'tag_filters' in preset_params and tag_filters is None:
            tag_filters = preset_params['tag_filters']
        if 'tag_match_type' in preset_params and tag_match_type == "any":  # Only override if default
            tag_match_type = preset_params['tag_match_type']
        if 'tag_exclude' in preset_params and tag_exclude is None:
            tag_exclude = preset_params['tag_exclude']

    validate_input(listing_type)
    validate_limit(limit)
    validate_offset(offset, limit)
    validate_filters(
        beds_min, beds_max, baths_min, baths_max, sqft_min, sqft_max,
        price_min, price_max, lot_sqft_min, lot_sqft_max, year_built_min, year_built_max,
        hoa_fee_min, hoa_fee_max, stories_min, stories_max, garage_spaces_min, garage_spaces_max
    )
    validate_sort(sort_by, sort_direction)
    validate_tag_filters(tag_filters, tag_match_type, tag_exclude)

    # Expand tag filters using aliases and fuzzy matching if enabled
    expanded_tag_filters = None
    expanded_tag_exclude = None

    if tag_filters:
        expanded_tag_filters = expand_tag_search(
            tag_filters,
            use_aliases=tag_use_aliases,
            use_fuzzy=tag_use_fuzzy,
            fuzzy_threshold=tag_fuzzy_threshold
        )

    if tag_exclude:
        expanded_tag_exclude = expand_tag_search(
            tag_exclude,
            use_aliases=tag_use_aliases,
            use_fuzzy=False  # Don't use fuzzy for exclusions to avoid accidental exclusions
        )

    # Validate new last_update_date filtering parameters
    validate_last_update_filters(
        convert_to_datetime_string(updated_since),
        extract_timedelta_hours(updated_in_past_hours)
    )

    # Convert listing_type to appropriate format
    if listing_type is None:
        converted_listing_type = None
    elif isinstance(listing_type, list):
        converted_listing_type = [ListingType(lt.upper()) for lt in listing_type]
    else:
        converted_listing_type = ListingType(listing_type.upper())

    # Convert date_from/date_to with precision detection
    converted_date_from, date_from_precision = detect_precision_and_convert(date_from)
    converted_date_to, date_to_precision = detect_precision_and_convert(date_to)

    # Validate converted dates
    validate_dates(converted_date_from, converted_date_to)

    # Convert datetime/timedelta objects to appropriate formats
    converted_past_days = extract_timedelta_days(past_days)
    converted_past_hours = extract_timedelta_hours(past_hours)
    converted_updated_since = convert_to_datetime_string(updated_since)
    converted_updated_in_past_hours = extract_timedelta_hours(updated_in_past_hours)

    # Auto-apply optimal sort for time-based filters (unless user specified different sort)
    if (converted_updated_since or converted_updated_in_past_hours) and not sort_by:
        sort_by = "last_update_date"
        if not sort_direction:
            sort_direction = "desc"  # Most recent first

    # Auto-apply optimal sort for PENDING listings with date filters
    # PENDING API filtering is broken, so we rely on client-side filtering
    # Sorting by pending_date ensures efficient pagination with early termination
    elif (converted_listing_type == ListingType.PENDING and
          (converted_past_days or converted_past_hours or converted_date_from) and
          not sort_by):
        sort_by = "pending_date"
        if not sort_direction:
            sort_direction = "desc"  # Most recent first

    scraper_input = ScraperInput(
        location=location,
        listing_type=converted_listing_type,
        return_type=ReturnType(return_type.lower()),
        property_type=[SearchPropertyType[prop.upper()] for prop in property_type] if property_type else None,
        proxy=proxy,
        radius=radius,
        mls_only=mls_only,
        last_x_days=converted_past_days,
        date_from=converted_date_from,
        date_to=converted_date_to,
        date_from_precision=date_from_precision,
        date_to_precision=date_to_precision,
        foreclosure=foreclosure,
        extra_property_data=extra_property_data,
        exclude_pending=exclude_pending,
        limit=limit,
        offset=offset,
        # New date/time filtering
        past_hours=converted_past_hours,
        # New last_update_date filtering
        updated_since=converted_updated_since,
        updated_in_past_hours=converted_updated_in_past_hours,
        # New property filtering
        beds_min=beds_min,
        beds_max=beds_max,
        baths_min=baths_min,
        baths_max=baths_max,
        sqft_min=sqft_min,
        sqft_max=sqft_max,
        price_min=price_min,
        price_max=price_max,
        lot_sqft_min=lot_sqft_min,
        lot_sqft_max=lot_sqft_max,
        year_built_min=year_built_min,
        year_built_max=year_built_max,
        # New sorting
        sort_by=sort_by,
        sort_direction=sort_direction,
        # Tag filtering (use expanded tags)
        tag_filters=expanded_tag_filters,
        tag_match_type=tag_match_type,
        tag_exclude=expanded_tag_exclude,
        # Additional property filters
        hoa_fee_min=hoa_fee_min,
        hoa_fee_max=hoa_fee_max,
        stories_min=stories_min,
        stories_max=stories_max,
        garage_spaces_min=garage_spaces_min,
        garage_spaces_max=garage_spaces_max,
        has_pool=has_pool,
        has_garage=has_garage,
        waterfront=waterfront,
        has_view=has_view,
        # Pagination control
        parallel=parallel,
    )

    site = RealtorScraper(scraper_input)
    results = site.search()

    if scraper_input.return_type != ReturnType.pandas:
        return results

    properties_dfs = [df for result in results if not (df := process_result(result)).empty]
    if not properties_dfs:
        return pd.DataFrame()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)

        result_df = pd.concat(properties_dfs, ignore_index=True, axis=0)[ordered_properties].replace(
            {"None": pd.NA, None: pd.NA, "": pd.NA}
        )

        # Apply data cleaning if enabled
        if clean_data:
            result_df = clean_dataframe(result_df, add_derived_fields=add_derived_fields)

        # Apply agent/broker contact filtering if enabled
        if require_agent_email or require_agent_phone:
            result_df = filter_by_agent_contact(result_df, require_agent_email, require_agent_phone)

        # Apply advanced sorting if enabled and sort_by is specified
        if enable_advanced_sort and sort_by:
            result_df = sort_properties(result_df, sort_by, sort_direction)

        return result_df
