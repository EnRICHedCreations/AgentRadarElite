"""
Test the scraping API locally to debug the pandas boolean error
"""
import sys
import os

# Add homeharvest to path
sys.path.insert(0, os.path.dirname(__file__))

from homeharvest import (
    scrape_property,
    get_wholesale_friendly_agents,
    analyze_agent_specialization,
    rank_by_investment_potential,
)

# Test scraping
print("[TEST] Starting scrape test...")
try:
    properties = scrape_property(
        location='31201',
        listing_type='for_sale',
        preset='investor_friendly',
        require_agent_email=True,
        mls_only=True,
        past_days=365,
        limit=50
    )

    print(f"[TEST] Found {len(properties)} properties")

    if not properties.empty:
        print("[TEST] Getting wholesale agents...")
        wholesale_agents = get_wholesale_friendly_agents(properties, min_listings=2)
        print(f"[TEST] Found {len(wholesale_agents)} wholesale agents")

        print("[TEST] Analyzing specialization...")
        specialization = analyze_agent_specialization(properties)
        print(f"[TEST] Analyzed {len(specialization)} agents")

        print("[TEST] Ranking properties...")
        ranked = rank_by_investment_potential(properties)
        print(f"[TEST] Ranked {len(ranked)} properties")

        print("\n[TEST] SUCCESS - All functions work!")
    else:
        print("[TEST] No properties found")

except Exception as e:
    print(f"\n[TEST] ERROR: {e}")
    import traceback
    traceback.print_exc()
