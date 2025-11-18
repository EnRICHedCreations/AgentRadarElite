"""
Data validation and cleaning utilities for property data.

Provides functions to validate, clean, and standardize property data.
"""
import pandas as pd
import re
from typing import Any, Optional, Union


def clean_price(price: Any) -> Optional[float]:
    """
    Clean and standardize price values.

    Args:
        price: Price value (can be string, int, float, or None)

    Returns:
        Cleaned price as float or None
    """
    if pd.isna(price) or price is None:
        return None

    if isinstance(price, (int, float)):
        return float(price) if price > 0 else None

    # Handle string prices
    if isinstance(price, str):
        # Remove currency symbols, commas, and whitespace
        cleaned = re.sub(r'[\$,\s]', '', price)
        try:
            return float(cleaned) if cleaned else None
        except ValueError:
            return None

    return None


def clean_sqft(sqft: Any) -> Optional[int]:
    """
    Clean and standardize square footage values.

    Args:
        sqft: Square footage value

    Returns:
        Cleaned sqft as int or None
    """
    if pd.isna(sqft) or sqft is None:
        return None

    if isinstance(sqft, (int, float)):
        return int(sqft) if sqft > 0 else None

    if isinstance(sqft, str):
        # Remove commas and whitespace
        cleaned = re.sub(r'[,\s]', '', sqft)
        try:
            return int(float(cleaned)) if cleaned else None
        except ValueError:
            return None

    return None


def clean_beds_baths(value: Any) -> Optional[Union[int, float]]:
    """
    Clean and standardize bedroom/bathroom counts.

    Args:
        value: Beds or baths value

    Returns:
        Cleaned value as int/float or None
    """
    if pd.isna(value) or value is None:
        return None

    if isinstance(value, (int, float)):
        return value if value > 0 else None

    if isinstance(value, str):
        cleaned = value.strip()
        try:
            # Handle fractional bathrooms
            if '.' in cleaned:
                return float(cleaned)
            return int(cleaned)
        except ValueError:
            return None

    return None


def clean_year(year: Any) -> Optional[int]:
    """
    Clean and validate year built.

    Args:
        year: Year value

    Returns:
        Cleaned year as int or None
    """
    if pd.isna(year) or year is None:
        return None

    if isinstance(year, (int, float)):
        year_int = int(year)
        # Validate reasonable year range (1800 to current year + 2)
        import datetime
        current_year = datetime.datetime.now().year
        if 1800 <= year_int <= current_year + 2:
            return year_int
        return None

    if isinstance(year, str):
        try:
            year_int = int(year.strip())
            import datetime
            current_year = datetime.datetime.now().year
            if 1800 <= year_int <= current_year + 2:
                return year_int
        except ValueError:
            pass

    return None


def clean_hoa_fee(fee: Any) -> Optional[float]:
    """
    Clean and standardize HOA fee values.

    Args:
        fee: HOA fee value

    Returns:
        Cleaned fee as float or None
    """
    return clean_price(fee)


def clean_tags(tags: Any) -> list:
    """
    Clean and standardize tag lists.

    Args:
        tags: Tags value (list, string, or None)

    Returns:
        Cleaned list of tags
    """
    if tags is None:
        return []

    # Check for pandas NA without triggering ambiguous truth value error
    try:
        if pd.isna(tags):
            return []
    except (ValueError, TypeError):
        # Skip pd.isna check for lists/arrays
        pass

    if isinstance(tags, list):
        # Remove None/empty values and strip whitespace
        return [tag.strip().lower() for tag in tags if tag and isinstance(tag, str)]

    if isinstance(tags, str):
        # Split by comma if it's a comma-separated string
        if ',' in tags:
            return [tag.strip().lower() for tag in tags.split(',') if tag.strip()]
        return [tags.strip().lower()] if tags.strip() else []

    return []


def validate_coordinates(lat: Any, lon: Any) -> tuple[Optional[float], Optional[float]]:
    """
    Validate and clean latitude/longitude coordinates.

    Args:
        lat: Latitude value
        lon: Longitude value

    Returns:
        Tuple of (cleaned_lat, cleaned_lon)
    """
    try:
        if pd.isna(lat) or pd.isna(lon) or lat is None or lon is None:
            return None, None

        lat_float = float(lat)
        lon_float = float(lon)

        # Validate coordinate ranges
        if -90 <= lat_float <= 90 and -180 <= lon_float <= 180:
            return lat_float, lon_float

        return None, None
    except (ValueError, TypeError):
        return None, None


def calculate_price_per_sqft(price: Optional[float], sqft: Optional[int]) -> Optional[float]:
    """
    Calculate price per square foot.

    Args:
        price: Property price
        sqft: Property square footage

    Returns:
        Price per sqft or None
    """
    if price and sqft and sqft > 0:
        return round(price / sqft, 2)
    return None


def validate_property_data(property_dict: dict) -> dict:
    """
    Validate and clean all fields in a property dictionary.

    Args:
        property_dict: Raw property data dictionary

    Returns:
        Cleaned property dictionary
    """
    cleaned = property_dict.copy()

    # Clean price fields
    if 'list_price' in cleaned:
        cleaned['list_price'] = clean_price(cleaned['list_price'])

    if 'sold_price' in cleaned:
        cleaned['sold_price'] = clean_price(cleaned['sold_price'])

    # Clean size fields
    if 'sqft' in cleaned:
        cleaned['sqft'] = clean_sqft(cleaned['sqft'])

    if 'lot_sqft' in cleaned:
        cleaned['lot_sqft'] = clean_sqft(cleaned['lot_sqft'])

    # Clean counts
    if 'beds' in cleaned:
        cleaned['beds'] = clean_beds_baths(cleaned['beds'])

    if 'baths' in cleaned:
        cleaned['baths'] = clean_beds_baths(cleaned['baths'])

    if 'full_baths' in cleaned:
        cleaned['full_baths'] = clean_beds_baths(cleaned['full_baths'])

    if 'half_baths' in cleaned:
        cleaned['half_baths'] = clean_beds_baths(cleaned['half_baths'])

    if 'stories' in cleaned:
        cleaned['stories'] = clean_beds_baths(cleaned['stories'])

    if 'parking_garage' in cleaned:
        cleaned['parking_garage'] = clean_beds_baths(cleaned['parking_garage'])

    # Clean year
    if 'year_built' in cleaned:
        cleaned['year_built'] = clean_year(cleaned['year_built'])

    # Clean HOA
    if 'hoa_fee' in cleaned:
        cleaned['hoa_fee'] = clean_hoa_fee(cleaned['hoa_fee'])

    # Clean coordinates
    if 'latitude' in cleaned and 'longitude' in cleaned:
        cleaned['latitude'], cleaned['longitude'] = validate_coordinates(
            cleaned.get('latitude'), cleaned.get('longitude')
        )

    # Clean tags
    if 'tags' in cleaned:
        cleaned['tags'] = clean_tags(cleaned['tags'])

    # Calculate price per sqft
    if 'list_price' in cleaned and 'sqft' in cleaned:
        cleaned['price_per_sqft'] = calculate_price_per_sqft(
            cleaned.get('list_price'), cleaned.get('sqft')
        )

    return cleaned


def clean_dataframe(df: pd.DataFrame, add_derived_fields: bool = True) -> pd.DataFrame:
    """
    Clean and validate an entire DataFrame of properties.

    Args:
        df: DataFrame with property data
        add_derived_fields: Whether to add derived fields like price_per_sqft

    Returns:
        Cleaned DataFrame
    """
    if df.empty:
        return df

    cleaned_df = df.copy()

    # Clean numeric fields
    if 'list_price' in cleaned_df.columns:
        cleaned_df['list_price'] = cleaned_df['list_price'].apply(clean_price)

    if 'sold_price' in cleaned_df.columns:
        cleaned_df['sold_price'] = cleaned_df['sold_price'].apply(clean_price)

    if 'sqft' in cleaned_df.columns:
        cleaned_df['sqft'] = cleaned_df['sqft'].apply(clean_sqft)

    if 'lot_sqft' in cleaned_df.columns:
        cleaned_df['lot_sqft'] = cleaned_df['lot_sqft'].apply(clean_sqft)

    if 'beds' in cleaned_df.columns:
        cleaned_df['beds'] = cleaned_df['beds'].apply(clean_beds_baths)

    if 'baths' in cleaned_df.columns:
        cleaned_df['baths'] = cleaned_df['baths'].apply(clean_beds_baths)

    if 'full_baths' in cleaned_df.columns:
        cleaned_df['full_baths'] = cleaned_df['full_baths'].apply(clean_beds_baths)

    if 'half_baths' in cleaned_df.columns:
        cleaned_df['half_baths'] = cleaned_df['half_baths'].apply(clean_beds_baths)

    if 'stories' in cleaned_df.columns:
        cleaned_df['stories'] = cleaned_df['stories'].apply(clean_beds_baths)

    if 'parking_garage' in cleaned_df.columns:
        cleaned_df['parking_garage'] = cleaned_df['parking_garage'].apply(clean_beds_baths)

    if 'year_built' in cleaned_df.columns:
        cleaned_df['year_built'] = cleaned_df['year_built'].apply(clean_year)

    if 'hoa_fee' in cleaned_df.columns:
        cleaned_df['hoa_fee'] = cleaned_df['hoa_fee'].apply(clean_hoa_fee)

    if 'tags' in cleaned_df.columns:
        cleaned_df['tags'] = cleaned_df['tags'].apply(clean_tags)

    # Validate coordinates
    if 'latitude' in cleaned_df.columns and 'longitude' in cleaned_df.columns:
        coords = cleaned_df.apply(
            lambda row: validate_coordinates(row.get('latitude'), row.get('longitude')),
            axis=1
        )
        cleaned_df['latitude'] = coords.apply(lambda x: x[0])
        cleaned_df['longitude'] = coords.apply(lambda x: x[1])

    # Add derived fields
    if add_derived_fields:
        if 'list_price' in cleaned_df.columns and 'sqft' in cleaned_df.columns:
            cleaned_df['price_per_sqft'] = cleaned_df.apply(
                lambda row: calculate_price_per_sqft(row.get('list_price'), row.get('sqft')),
                axis=1
            )

    return cleaned_df


def get_data_quality_report(df: pd.DataFrame) -> dict:
    """
    Generate a data quality report for a DataFrame.

    Args:
        df: DataFrame with property data

    Returns:
        Dictionary with quality metrics
    """
    if df.empty:
        return {"total_properties": 0}

    total = len(df)
    report = {
        "total_properties": total,
        "completeness": {},
        "data_ranges": {},
    }

    # Calculate completeness for each column
    for col in df.columns:
        non_null = df[col].notna().sum()
        report["completeness"][col] = {
            "count": int(non_null),
            "percentage": round((non_null / total) * 100, 2)
        }

    # Calculate ranges for numeric columns
    numeric_cols = ['list_price', 'sqft', 'lot_sqft', 'beds', 'baths', 'year_built', 'hoa_fee', 'stories']
    for col in numeric_cols:
        if col in df.columns and df[col].notna().any():
            report["data_ranges"][col] = {
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "mean": round(float(df[col].mean()), 2),
                "median": float(df[col].median())
            }

    return report
