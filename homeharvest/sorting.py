"""
Advanced sorting utilities for property data.

Provides multi-field sorting, calculated field sorting, and custom sort functions.
"""
import pandas as pd
from typing import List, Union, Callable, Optional


# Available sort fields and their descriptions
SORTABLE_FIELDS = {
    "list_price": "Listing price",
    "sold_price": "Sold price",
    "price_per_sqft": "Price per square foot",
    "sqft": "Living area square footage",
    "lot_sqft": "Lot size",
    "beds": "Number of bedrooms",
    "full_baths": "Number of full bathrooms",
    "baths": "Total bathrooms",
    "year_built": "Year property was built",
    "days_on_mls": "Days on market",
    "list_date": "Date listed",
    "sold_date": "Date sold",
    "pending_date": "Date went pending",
    "last_sold_date": "Last sold date",
    "last_update_date": "Last update date",
    "hoa_fee": "HOA fee amount",
    "stories": "Number of stories",
    "parking_garage": "Garage spaces",
    "assessed_value": "Tax assessed value",
    "estimated_value": "Estimated value",
    "property_age": "Property age (calculated)",
    "value_per_sqft": "Value per sqft (calculated)",
}


def calculate_property_age(df: pd.DataFrame) -> pd.Series:
    """
    Calculate property age from year_built.

    Args:
        df: DataFrame with year_built column

    Returns:
        Series with property ages
    """
    from datetime import datetime
    current_year = datetime.now().year

    if 'year_built' in df.columns:
        return current_year - df['year_built']
    return pd.Series([None] * len(df))


def calculate_value_per_sqft(df: pd.DataFrame, value_field: str = 'estimated_value') -> pd.Series:
    """
    Calculate value per sqft from estimated/assessed value.

    Args:
        df: DataFrame with value and sqft columns
        value_field: Which value field to use (estimated_value or assessed_value)

    Returns:
        Series with value per sqft
    """
    if value_field in df.columns and 'sqft' in df.columns:
        return df[value_field] / df['sqft']
    return pd.Series([None] * len(df))


def calculate_price_discount(df: pd.DataFrame) -> pd.Series:
    """
    Calculate discount percentage from estimated value.

    Args:
        df: DataFrame with list_price and estimated_value

    Returns:
        Series with discount percentages (negative = below estimate)
    """
    if 'list_price' in df.columns and 'estimated_value' in df.columns:
        return ((df['list_price'] - df['estimated_value']) / df['estimated_value'] * 100)
    return pd.Series([None] * len(df))


def calculate_lot_ratio(df: pd.DataFrame) -> pd.Series:
    """
    Calculate ratio of living space to lot size.

    Args:
        df: DataFrame with sqft and lot_sqft

    Returns:
        Series with lot ratios
    """
    if 'sqft' in df.columns and 'lot_sqft' in df.columns:
        return df['sqft'] / df['lot_sqft']
    return pd.Series([None] * len(df))


# Map of calculated fields to their calculation functions
CALCULATED_FIELDS = {
    "property_age": calculate_property_age,
    "value_per_sqft": calculate_value_per_sqft,
    "price_discount": calculate_price_discount,
    "lot_ratio": calculate_lot_ratio,
}


def add_calculated_sort_fields(df: pd.DataFrame, fields: List[str]) -> pd.DataFrame:
    """
    Add calculated fields to DataFrame for sorting.

    Args:
        df: DataFrame to add fields to
        fields: List of field names that might be calculated

    Returns:
        DataFrame with calculated fields added
    """
    df_copy = df.copy()

    for field in fields:
        if field in CALCULATED_FIELDS and field not in df_copy.columns:
            df_copy[field] = CALCULATED_FIELDS[field](df_copy)

    return df_copy


def sort_properties(
    df: pd.DataFrame,
    sort_by: Union[str, List[str]],
    sort_direction: Union[str, List[str]] = "desc",
    na_position: str = "last"
) -> pd.DataFrame:
    """
    Sort properties by one or more fields with advanced options.

    Args:
        df: DataFrame to sort
        sort_by: Field name or list of field names to sort by
        sort_direction: "asc" or "desc", or list matching sort_by length
        na_position: Where to place NaN values ("first" or "last")

    Returns:
        Sorted DataFrame
    """
    if df.empty:
        return df

    # Convert single values to lists
    if isinstance(sort_by, str):
        sort_by = [sort_by]
    if isinstance(sort_direction, str):
        sort_direction = [sort_direction] * len(sort_by)

    # Validate lengths match
    if len(sort_by) != len(sort_direction):
        raise ValueError("sort_by and sort_direction must have same length")

    # Add calculated fields if needed
    df_with_calc = add_calculated_sort_fields(df, sort_by)

    # Convert directions to boolean (True = ascending)
    ascending = [d.lower() == "asc" for d in sort_direction]

    # Filter to only sort by fields that exist
    valid_fields = []
    valid_ascending = []
    for field, asc in zip(sort_by, ascending):
        if field in df_with_calc.columns:
            valid_fields.append(field)
            valid_ascending.append(asc)

    if not valid_fields:
        return df

    # Perform sort
    sorted_df = df_with_calc.sort_values(
        by=valid_fields,
        ascending=valid_ascending,
        na_position=na_position
    )

    # Remove calculated fields that weren't in original
    for field in CALCULATED_FIELDS.keys():
        if field in sorted_df.columns and field not in df.columns:
            sorted_df = sorted_df.drop(columns=[field])

    return sorted_df.reset_index(drop=True)


def get_best_deals(
    df: pd.DataFrame,
    limit: int = 10,
    criteria: str = "price_discount"
) -> pd.DataFrame:
    """
    Get the best deals based on various criteria.

    Args:
        df: DataFrame with property data
        limit: Number of results to return
        criteria: How to determine "best" (price_discount, price_per_sqft, value_per_sqft)

    Returns:
        DataFrame with best deals
    """
    if df.empty:
        return df

    # Add calculated field if needed
    df_with_calc = add_calculated_sort_fields(df, [criteria])

    # Sort based on criteria (lower is better for most)
    if criteria in ["price_discount"]:
        # For discount, most negative is best (furthest below estimate)
        sorted_df = df_with_calc.sort_values(by=criteria, ascending=True)
    else:
        # For price per sqft, lower is better
        sorted_df = df_with_calc.sort_values(by=criteria, ascending=True)

    result = sorted_df.head(limit)

    # Remove calculated field if it wasn't in original
    if criteria in CALCULATED_FIELDS and criteria not in df.columns:
        result = result.drop(columns=[criteria])

    return result.reset_index(drop=True)


def get_newest_listings(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """
    Get the newest listings by list_date.

    Args:
        df: DataFrame with property data
        limit: Number of results to return

    Returns:
        DataFrame with newest listings
    """
    return sort_properties(df, "list_date", "desc").head(limit)


def get_recently_updated(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """
    Get recently updated properties by last_update_date.

    Args:
        df: DataFrame with property data
        limit: Number of results to return

    Returns:
        DataFrame with recently updated properties
    """
    return sort_properties(df, "last_update_date", "desc").head(limit)


def get_price_drops(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """
    Get properties with recent price changes (if available).

    Args:
        df: DataFrame with property data
        limit: Number of results to return

    Returns:
        DataFrame with properties that may have price drops
    """
    # Sort by last_update_date to find recently changed properties
    return get_recently_updated(df, limit)


def create_custom_score(
    df: pd.DataFrame,
    score_function: Callable[[pd.Series], float],
    score_name: str = "custom_score"
) -> pd.DataFrame:
    """
    Create a custom scoring function for properties.

    Args:
        df: DataFrame with property data
        score_function: Function that takes a row and returns a score
        score_name: Name for the score column

    Returns:
        DataFrame with custom score added
    """
    df_copy = df.copy()
    df_copy[score_name] = df_copy.apply(score_function, axis=1)
    return df_copy


def rank_by_investment_potential(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rank properties by investment potential using multiple factors.

    Considers:
    - Price per sqft (lower is better)
    - Price vs estimated value (discount is better)
    - Days on market (longer may indicate motivated seller)
    - Lot size (bigger is better for investment)

    Args:
        df: DataFrame with property data

    Returns:
        DataFrame with investment_score column added
    """
    if df.empty:
        return df

    df_copy = df.copy()

    # Calculate individual scores (0-100 scale)
    scores = pd.DataFrame(index=df_copy.index)

    # Price per sqft score (lower is better, so invert)
    if 'price_per_sqft' in df_copy.columns:
        ppsf = df_copy['price_per_sqft'].fillna(df_copy['price_per_sqft'].median())
        scores['ppsf_score'] = 100 - ((ppsf - ppsf.min()) / (ppsf.max() - ppsf.min()) * 100)
    else:
        scores['ppsf_score'] = 50

    # Price discount score
    if 'list_price' in df_copy.columns and 'estimated_value' in df_copy.columns:
        discount = calculate_price_discount(df_copy).fillna(0)
        # Negative discount (below estimate) is good
        scores['discount_score'] = discount.apply(lambda x: min(100, max(0, -x)))
    else:
        scores['discount_score'] = 50

    # Days on market score (longer is better for negotiation)
    if 'days_on_mls' in df_copy.columns:
        dom = df_copy['days_on_mls'].fillna(0)
        scores['dom_score'] = (dom / dom.max() * 100) if dom.max() > 0 else 50
    else:
        scores['dom_score'] = 50

    # Lot size score (bigger is better)
    if 'lot_sqft' in df_copy.columns:
        lot = df_copy['lot_sqft'].fillna(df_copy['lot_sqft'].median())
        scores['lot_score'] = ((lot - lot.min()) / (lot.max() - lot.min()) * 100)
    else:
        scores['lot_score'] = 50

    # Calculate weighted average (you can adjust weights)
    weights = {
        'ppsf_score': 0.3,
        'discount_score': 0.4,
        'dom_score': 0.2,
        'lot_score': 0.1
    }

    df_copy['investment_score'] = sum(
        scores[col] * weight for col, weight in weights.items()
    )

    return df_copy.sort_values('investment_score', ascending=False).reset_index(drop=True)


def get_available_sort_fields() -> dict:
    """Get dictionary of all available sort fields and their descriptions."""
    return SORTABLE_FIELDS.copy()
