"""
Test scraping ZIP 31201 to debug agent filtering
"""
import sys
import os

# Add homeharvest to path
sys.path.insert(0, os.path.dirname(__file__))

from homeharvest import (
    scrape_property,
    get_wholesale_friendly_agents,
    analyze_agent_specialization,
)

print("=" * 60)
print("Testing ZIP 31201 - Investor Friendly Preset")
print("=" * 60)

# Scrape parameters matching what Vercel uses
scrape_params = {
    'location': '31201',
    'listing_type': 'for_sale',
    'preset': 'investor_friendly',
    'require_agent_email': False,  # Changed from True
    'mls_only': True,
    'past_days': 365,
    'enable_advanced_sort': True,
    'add_derived_fields': True,
    'clean_data': True,
    'limit': 200
}

print(f"\nScraping with params:")
for key, val in scrape_params.items():
    print(f"  {key}: {val}")

# Scrape properties
print(f"\n[*] Fetching properties...")
properties = scrape_property(**scrape_params)

print(f"\n[+] Found {len(properties)} total properties")

if not properties.empty:
    # Check agent data
    print(f"\n[*] Agent Analysis:")
    print(f"  Total unique agents: {properties['agent_name'].nunique() if 'agent_name' in properties.columns else 0}")

    if 'agent_email' in properties.columns:
        props_with_email = properties['agent_email'].notna().sum()
        print(f"  Properties with agent email: {props_with_email}/{len(properties)}")

    if 'agent_phones' in properties.columns:
        props_with_phone = properties['agent_phones'].notna().sum()
        print(f"  Properties with agent phone: {props_with_phone}/{len(properties)}")

    # Get wholesale-friendly agents with min_listings=2
    print(f"\n[*] Finding wholesale-friendly agents (min_listings=2)...")
    wholesale_agents = get_wholesale_friendly_agents(properties, min_listings=2)

    print(f"\n[+] Found {len(wholesale_agents)} wholesale-friendly agents")

    if not wholesale_agents.empty:
        print(f"\n[*] Wholesale Agents:")
        print(wholesale_agents[['agent_name', 'listing_count', 'wholesale_score', 'agent_email', 'primary_phone']].to_string())

        # Show specialization
        print(f"\n[*] Agent Specialization:")
        spec = analyze_agent_specialization(properties)
        print(spec[['agent_name', 'listing_count', 'price_category', 'avg_price']].to_string())
    else:
        print("\n[!] No wholesale agents found after filtering")
        print("\nDebugging - All agents before wholesale filtering:")
        from homeharvest.agent_broker import get_agent_activity
        all_agents = get_agent_activity(properties)
        print(all_agents[['agent_name', 'listing_count', 'agent_email', 'primary_phone']].to_string())

else:
    print("[!] No properties found!")

print("\n" + "=" * 60)
