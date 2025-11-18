"""
Agent and broker data extraction and analysis utilities.

Provides enhanced agent/broker filtering, contact extraction, and activity analysis.
"""
import pandas as pd
from typing import Dict, List, Optional, Tuple
import re


def extract_phone_numbers(phone_data) -> List[str]:
    """
    Extract and format phone numbers from various formats.

    Args:
        phone_data: Phone data (can be list, dict, or string)

    Returns:
        List of formatted phone numbers
    """
    # Handle None first
    if phone_data is None:
        return []

    # Check for pandas NA (skip for lists to avoid ValueError)
    if not isinstance(phone_data, list):
        try:
            if pd.isna(phone_data):
                return []
        except (ValueError, TypeError):
            pass

    phones = []

    # Handle list of phone objects
    if isinstance(phone_data, list):
        for item in phone_data:
            if isinstance(item, dict):
                number = item.get('number') or item.get('phone')
                if number:
                    phones.append(str(number))
            elif isinstance(item, str):
                phones.append(item)

    # Handle single phone string
    elif isinstance(phone_data, str):
        # Split multiple numbers if comma/semicolon separated
        if ',' in phone_data or ';' in phone_data:
            phones = [p.strip() for p in re.split(r'[,;]', phone_data)]
        else:
            phones = [phone_data]

    # Clean and format
    formatted = []
    for phone in phones:
        if phone:
            # Remove non-digit characters except +
            cleaned = re.sub(r'[^\d+]', '', str(phone))
            if cleaned and len(cleaned) >= 10:
                formatted.append(cleaned)

    return formatted


def extract_primary_phone(phone_data) -> Optional[str]:
    """
    Extract the primary/first phone number.

    Args:
        phone_data: Phone data

    Returns:
        Primary phone number or None
    """
    phones = extract_phone_numbers(phone_data)
    return phones[0] if phones else None


def format_contact_info(row: pd.Series) -> Dict[str, any]:
    """
    Format contact information from a property row.

    Args:
        row: Property row with agent/broker/office data

    Returns:
        Dictionary with formatted contact info
    """
    contact = {
        "agent": {
            "name": row.get('agent_name'),
            "email": row.get('agent_email'),
            "phone": extract_primary_phone(row.get('agent_phones')),
            "phones": extract_phone_numbers(row.get('agent_phones')),
            "id": row.get('agent_id'),
        },
        "broker": {
            "name": row.get('broker_name'),
            "id": row.get('broker_id'),
        },
        "office": {
            "name": row.get('office_name'),
            "email": row.get('office_email'),
            "phone": extract_primary_phone(row.get('office_phones')),
            "phones": extract_phone_numbers(row.get('office_phones')),
            "id": row.get('office_id'),
        }
    }

    return contact


def has_agent_contact(row: pd.Series) -> bool:
    """
    Check if property has agent contact information.

    Args:
        row: Property row

    Returns:
        True if has agent email or phone
    """
    has_email = pd.notna(row.get('agent_email')) and row.get('agent_email')
    has_phone = bool(extract_phone_numbers(row.get('agent_phones')))
    return has_email or has_phone


def filter_by_agent_contact(df: pd.DataFrame, require_email: bool = False, require_phone: bool = False) -> pd.DataFrame:
    """
    Filter properties that have agent contact information.

    Args:
        df: DataFrame with property data
        require_email: Only include if has agent email
        require_phone: Only include if has agent phone

    Returns:
        Filtered DataFrame
    """
    if df.empty:
        return df

    filtered = df.copy()

    if require_email:
        filtered = filtered[filtered['agent_email'].notna() & (filtered['agent_email'] != '')]

    if require_phone:
        filtered = filtered[filtered['agent_phones'].notna()]
        # Additional check for valid phones
        filtered = filtered[filtered.apply(lambda row: bool(extract_phone_numbers(row['agent_phones'])), axis=1)]

    return filtered.reset_index(drop=True)


def get_agent_activity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze agent activity and listing counts.

    Args:
        df: DataFrame with property data

    Returns:
        DataFrame with agent activity stats
    """
    if df.empty or 'agent_name' not in df.columns:
        return pd.DataFrame()

    # Group by agent
    agent_stats = df.groupby('agent_name').agg({
        'property_id': 'count',
        'list_price': ['mean', 'min', 'max'],
        'agent_email': 'first',
        'agent_phones': 'first',
        'agent_id': 'first',
        'broker_name': 'first',
        'office_name': 'first',
    }).reset_index()

    # Flatten column names
    agent_stats.columns = [
        'agent_name',
        'listing_count',
        'avg_price',
        'min_price',
        'max_price',
        'agent_email',
        'agent_phones',
        'agent_id',
        'broker_name',
        'office_name'
    ]

    # Sort by listing count
    agent_stats = agent_stats.sort_values('listing_count', ascending=False).reset_index(drop=True)

    # Add primary phone
    agent_stats['primary_phone'] = agent_stats['agent_phones'].apply(extract_primary_phone)

    return agent_stats


def get_broker_activity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze broker activity and listing counts.

    Args:
        df: DataFrame with property data

    Returns:
        DataFrame with broker activity stats
    """
    if df.empty or 'broker_name' not in df.columns:
        return pd.DataFrame()

    # Group by broker
    broker_stats = df.groupby('broker_name').agg({
        'property_id': 'count',
        'list_price': ['mean', 'min', 'max'],
        'broker_id': 'first',
        'agent_name': 'nunique',  # Number of unique agents
    }).reset_index()

    # Flatten column names
    broker_stats.columns = [
        'broker_name',
        'listing_count',
        'avg_price',
        'min_price',
        'max_price',
        'broker_id',
        'unique_agents'
    ]

    # Sort by listing count
    broker_stats = broker_stats.sort_values('listing_count', ascending=False).reset_index(drop=True)

    return broker_stats


def get_office_activity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze office activity and listing counts.

    Args:
        df: DataFrame with property data

    Returns:
        DataFrame with office activity stats
    """
    if df.empty or 'office_name' not in df.columns:
        return pd.DataFrame()

    # Group by office
    office_stats = df.groupby('office_name').agg({
        'property_id': 'count',
        'list_price': ['mean', 'min', 'max'],
        'office_id': 'first',
        'office_email': 'first',
        'office_phones': 'first',
        'agent_name': 'nunique',  # Number of unique agents
    }).reset_index()

    # Flatten column names
    office_stats.columns = [
        'office_name',
        'listing_count',
        'avg_price',
        'min_price',
        'max_price',
        'office_id',
        'office_email',
        'office_phones',
        'unique_agents'
    ]

    # Sort by listing count
    office_stats = office_stats.sort_values('listing_count', ascending=False).reset_index(drop=True)

    # Add primary phone
    office_stats['primary_phone'] = office_stats['office_phones'].apply(extract_primary_phone)

    return office_stats


def find_most_active_agents(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """
    Find the most active agents by listing count.

    Args:
        df: DataFrame with property data
        limit: Number of agents to return

    Returns:
        DataFrame with top agents
    """
    agent_stats = get_agent_activity(df)
    return agent_stats.head(limit)


def find_properties_by_agent(df: pd.DataFrame, agent_name: str) -> pd.DataFrame:
    """
    Find all properties listed by a specific agent.

    Args:
        df: DataFrame with property data
        agent_name: Name of the agent

    Returns:
        DataFrame with agent's properties
    """
    if df.empty or 'agent_name' not in df.columns:
        return pd.DataFrame()

    # Case-insensitive partial match
    mask = df['agent_name'].str.contains(agent_name, case=False, na=False)
    return df[mask].reset_index(drop=True)


def find_properties_by_broker(df: pd.DataFrame, broker_name: str) -> pd.DataFrame:
    """
    Find all properties listed by a specific broker.

    Args:
        df: DataFrame with property data
        broker_name: Name of the broker

    Returns:
        DataFrame with broker's properties
    """
    if df.empty or 'broker_name' not in df.columns:
        return pd.DataFrame()

    # Case-insensitive partial match
    mask = df['broker_name'].str.contains(broker_name, case=False, na=False)
    return df[mask].reset_index(drop=True)


def get_contact_export(df: pd.DataFrame) -> pd.DataFrame:
    """
    Export agent contact information in a clean format for CRM import.

    Args:
        df: DataFrame with property data

    Returns:
        DataFrame with contact information
    """
    if df.empty:
        return pd.DataFrame()

    # Get unique agents with contact info
    contacts = df[['agent_name', 'agent_email', 'agent_phones', 'agent_id',
                   'broker_name', 'office_name', 'office_phones', 'office_email']].drop_duplicates(subset=['agent_id'])

    # Add formatted phones
    contacts['agent_primary_phone'] = contacts['agent_phones'].apply(extract_primary_phone)
    contacts['office_primary_phone'] = contacts['office_phones'].apply(extract_primary_phone)

    # Remove rows without any contact info
    contacts = contacts[
        contacts['agent_email'].notna() |
        contacts['agent_primary_phone'].notna()
    ]

    # Select and order columns
    export_cols = [
        'agent_name',
        'agent_email',
        'agent_primary_phone',
        'broker_name',
        'office_name',
        'office_email',
        'office_primary_phone',
        'agent_id'
    ]

    return contacts[export_cols].reset_index(drop=True)


def analyze_agent_specialization(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze what types of properties each agent specializes in.

    Args:
        df: DataFrame with property data

    Returns:
        DataFrame with agent specialization info
    """
    if df.empty or 'agent_name' not in df.columns:
        return pd.DataFrame()

    # Build aggregation dict dynamically based on available columns
    agg_dict = {
        'property_id': 'count',
        'list_price': ['mean', 'median'],
        'agent_email': 'first',
    }

    # Add optional columns if they exist
    if 'sqft' in df.columns:
        agg_dict['sqft'] = 'mean'
    if 'beds' in df.columns:
        agg_dict['beds'] = 'mean'
    if 'full_baths' in df.columns:
        agg_dict['full_baths'] = 'mean'
    if 'style' in df.columns:  # Use style instead of property_type
        agg_dict['style'] = lambda x: x.mode()[0] if not x.mode().empty else None

    # Group by agent and calculate stats
    specialization = df.groupby('agent_name').agg(agg_dict).reset_index()

    # Flatten column names dynamically
    new_cols = ['agent_name', 'listing_count', 'avg_price', 'median_price']

    # Add optional columns in order
    if 'sqft' in agg_dict:
        new_cols.append('avg_sqft')
    if 'beds' in agg_dict:
        new_cols.append('avg_beds')
    if 'full_baths' in agg_dict:
        new_cols.append('avg_baths')
    if 'style' in agg_dict:
        new_cols.append('common_style')

    new_cols.append('agent_email')

    specialization.columns = new_cols

    # Categorize price range
    def categorize_price(price):
        if pd.isna(price):
            return 'Unknown'
        elif price < 200000:
            return 'Budget'
        elif price < 500000:
            return 'Mid-Range'
        elif price < 1000000:
            return 'Upper-Mid'
        else:
            return 'Luxury'

    specialization['price_category'] = specialization['avg_price'].apply(categorize_price)

    return specialization.sort_values('listing_count', ascending=False).reset_index(drop=True)


def get_wholesale_friendly_agents(df: pd.DataFrame, min_listings: int = 3) -> pd.DataFrame:
    """
    Find agents who may be wholesale-friendly based on their listing patterns.

    Criteria:
    - Multiple listings (inventory)
    - Lower price points (more likely motivated)
    - Has contact information

    Args:
        df: DataFrame with property data
        min_listings: Minimum number of listings

    Returns:
        DataFrame with wholesale-friendly agents
    """
    # Get agent activity
    agent_stats = get_agent_activity(df)

    # Filter by minimum listings
    agent_stats = agent_stats[agent_stats['listing_count'] >= min_listings]

    # Filter by having contact info
    agent_stats = agent_stats[
        (agent_stats['agent_email'].notna()) |
        (agent_stats['primary_phone'].notna())
    ]

    # Calculate a "wholesale score" (lower avg price + more listings = higher score)
    if not agent_stats.empty and 'avg_price' in agent_stats.columns:
        # Normalize prices (invert so lower is better)
        max_price = agent_stats['avg_price'].max()
        if max_price > 0:
            agent_stats['price_score'] = 1 - (agent_stats['avg_price'] / max_price)
        else:
            agent_stats['price_score'] = 0

        # Normalize listing count
        max_listings = agent_stats['listing_count'].max()
        if max_listings > 0:
            agent_stats['inventory_score'] = agent_stats['listing_count'] / max_listings
        else:
            agent_stats['inventory_score'] = 0

        # Combined wholesale score (60% price, 40% inventory)
        agent_stats['wholesale_score'] = (
            agent_stats['price_score'] * 0.6 +
            agent_stats['inventory_score'] * 0.4
        ) * 100

        # Sort by wholesale score
        agent_stats = agent_stats.sort_values('wholesale_score', ascending=False)

    return agent_stats.reset_index(drop=True)
