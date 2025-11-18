from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add HomeHarvest Elite to path (relative to AgentRadar root)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from homeharvest import (
    scrape_property,
    get_wholesale_friendly_agents,
    analyze_agent_specialization,
    rank_by_investment_potential,
    get_contact_export
)
from datetime import datetime
import traceback
import pandas as pd

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            # Extract search parameters
            zip_code = data.get('zipCode')
            preset = data.get('preset', 'investor_friendly')

            # Advanced filters
            price_min = data.get('priceMin')
            price_max = data.get('priceMax')
            beds_min = data.get('bedsMin')
            baths_min = data.get('bathsMin')
            sqft_min = data.get('sqftMin')
            hoa_fee_max = data.get('hoaFeeMax')

            # Features
            has_pool = data.get('hasPool')
            has_garage = data.get('hasGarage')
            waterfront = data.get('waterfront')
            garage_min = data.get('garageMin')

            # Tag filters
            tag_filters = data.get('tagFilters', [])
            tag_match_type = data.get('tagMatchType', 'any')
            tag_exclude = data.get('tagExclude', [])

            # Agent filters
            min_listings = data.get('minListings', 2)

            if not zip_code:
                self.send_error(400, "ZIP code is required")
                return

            print(f"[AgentRadar Elite] Scraping ZIP: {zip_code}")
            print(f"[AgentRadar Elite] Preset: {preset}")
            if price_min or price_max:
                print(f"[AgentRadar Elite] Price range: ${price_min or 0:,} - ${price_max or 'unlimited'}")

            # Build scraping parameters
            scrape_params = {
                'location': zip_code,
                'listing_type': 'for_sale',
                'preset': preset,
                'require_agent_email': True,  # MUST have agent contact
                'mls_only': True,
                'past_days': 365,
                'enable_advanced_sort': True,
                'add_derived_fields': True,
                'clean_data': True,
                'limit': 200
            }

            # Add optional filters
            if price_min:
                scrape_params['price_min'] = int(price_min)
            if price_max:
                scrape_params['price_max'] = int(price_max)
            if beds_min:
                scrape_params['beds_min'] = int(beds_min)
            if baths_min:
                scrape_params['baths_min'] = float(baths_min)
            if sqft_min:
                scrape_params['sqft_min'] = int(sqft_min)
            if hoa_fee_max:
                scrape_params['hoa_fee_max'] = int(hoa_fee_max)
            if has_pool is not None:
                scrape_params['has_pool'] = has_pool
            if has_garage is not None:
                scrape_params['has_garage'] = has_garage
            if waterfront is not None:
                scrape_params['waterfront'] = waterfront
            if garage_min:
                scrape_params['garage_spaces_min'] = int(garage_min)
            if tag_filters:
                scrape_params['tag_filters'] = tag_filters
                scrape_params['tag_match_type'] = tag_match_type
            if tag_exclude:
                scrape_params['tag_exclude'] = tag_exclude

            # Scrape properties
            print(f"[AgentRadar Elite] Fetching properties...")
            properties = scrape_property(**scrape_params)

            if properties.empty:
                print(f"[AgentRadar Elite] No properties found")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'zip_code': zip_code,
                    'total_properties': 0,
                    'agents': [],
                    'market_stats': {},
                    'scraped_at': datetime.now().isoformat()
                }).encode())
                return

            print(f"[AgentRadar Elite] Found {len(properties)} properties")

            # Get wholesale-friendly agents
            print(f"[AgentRadar Elite] Analyzing agents...")
            wholesale_agents = get_wholesale_friendly_agents(
                properties,
                min_listings=min_listings
            )

            # Get agent specialization
            specialization = analyze_agent_specialization(properties)

            # Rank properties by investment potential
            ranked_props = rank_by_investment_potential(properties)

            # Build agent data with ALL the details
            agents_list = []

            for idx, agent in wholesale_agents.iterrows():
                agent_name = agent['agent_name']

                # Get agent's properties
                agent_props = ranked_props[ranked_props['agent_name'] == agent_name]

                # Get specialization data
                spec = specialization[specialization['agent_name'] == agent_name]

                # Build listings array
                listings = []
                for _, prop in agent_props.iterrows():
                    listings.append({
                        'address': f"{prop.get('full_street_line', '')}, {prop.get('city', '')}, {prop.get('state', '')} {prop.get('zip_code', '')}".strip(),
                        'list_price': float(prop['list_price']) if pd.notna(prop.get('list_price')) else None,
                        'investment_score': float(prop['investment_score']) if pd.notna(prop.get('investment_score')) else None,
                        'price_per_sqft': float(prop['price_per_sqft']) if pd.notna(prop.get('price_per_sqft')) else None,
                        'days_on_mls': int(prop['days_on_mls']) if pd.notna(prop.get('days_on_mls')) else None,
                        'beds': int(prop['beds']) if pd.notna(prop.get('beds')) else None,
                        'baths': float(prop['full_baths']) if pd.notna(prop.get('full_baths')) else None,
                        'sqft': int(prop['sqft']) if pd.notna(prop.get('sqft')) else None,
                        'lot_sqft': int(prop['lot_sqft']) if pd.notna(prop.get('lot_sqft')) else None,
                        'year_built': int(prop['year_built']) if pd.notna(prop.get('year_built')) else None,
                        'property_url': prop.get('property_url'),
                        'tags': prop.get('tags', []) if pd.notna(prop.get('tags')) else []
                    })

                # Find best deal
                best_deal = None
                if not agent_props.empty:
                    best_prop = agent_props.nlargest(1, 'investment_score').iloc[0]
                    best_deal = {
                        'address': f"{best_prop.get('full_street_line', '')}, {best_prop.get('city', '')}",
                        'list_price': float(best_prop['list_price']) if pd.notna(best_prop.get('list_price')) else None,
                        'investment_score': float(best_prop['investment_score']) if pd.notna(best_prop.get('investment_score')) else None,
                        'property_url': best_prop.get('property_url')
                    }

                # Build complete agent object
                agent_data = {
                    'agent_name': agent_name,
                    'agent_email': agent.get('agent_email'),
                    'agent_phone': agent.get('primary_phone'),
                    'broker_name': agent.get('broker_name'),
                    'office_name': agent.get('office_name'),

                    # Wholesale scoring
                    'wholesale_score': float(agent.get('wholesale_score', 0)),
                    'listing_count': int(agent.get('listing_count', 0)),
                    'avg_price': float(agent.get('avg_price', 0)) if pd.notna(agent.get('avg_price')) else None,
                    'min_price': float(agent.get('min_price', 0)) if pd.notna(agent.get('min_price')) else None,
                    'max_price': float(agent.get('max_price', 0)) if pd.notna(agent.get('max_price')) else None,

                    # Specialization
                    'price_category': spec.iloc[0]['price_category'] if not spec.empty and 'price_category' in spec.columns else None,
                    'avg_sqft': float(spec.iloc[0]['avg_sqft']) if not spec.empty and 'avg_sqft' in spec.columns and pd.notna(spec.iloc[0].get('avg_sqft')) else None,
                    'avg_beds': float(spec.iloc[0]['avg_beds']) if not spec.empty and 'avg_beds' in spec.columns and pd.notna(spec.iloc[0].get('avg_beds')) else None,
                    'avg_baths': float(spec.iloc[0]['avg_baths']) if not spec.empty and 'avg_baths' in spec.columns and pd.notna(spec.iloc[0].get('avg_baths')) else None,

                    # Investment insights
                    'avg_investment_score': float(agent_props['investment_score'].mean()) if 'investment_score' in agent_props.columns else None,
                    'best_deal': best_deal,

                    # Days on market
                    'avg_days_on_market': float(agent_props['days_on_mls'].mean()) if 'days_on_mls' in agent_props.columns and not agent_props['days_on_mls'].isna().all() else None,

                    # Listings
                    'listings': listings
                }

                agents_list.append(agent_data)

            print(f"[AgentRadar Elite] Found {len(agents_list)} wholesale-friendly agents")

            # Calculate market statistics
            market_stats = {
                'total_properties': len(properties),
                'avg_price': float(properties['list_price'].mean()) if 'list_price' in properties.columns else None,
                'median_price': float(properties['list_price'].median()) if 'list_price' in properties.columns else None,
                'avg_price_per_sqft': float(properties['price_per_sqft'].mean()) if 'price_per_sqft' in properties.columns else None,
                'avg_days_on_market': float(properties['days_on_mls'].mean()) if 'days_on_mls' in properties.columns and not properties['days_on_mls'].isna().all() else None,
                'total_agents': len(agents_list),
                'avg_wholesale_score': float(sum(a['wholesale_score'] for a in agents_list) / len(agents_list)) if agents_list else 0,
                'high_potential_agents': len([a for a in agents_list if a['wholesale_score'] >= 70])
            }

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                'success': True,
                'zip_code': zip_code,
                'preset': preset,
                'agents': agents_list,
                'market_stats': market_stats,
                'scraped_at': datetime.now().isoformat()
            }

            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            print(f"[AgentRadar Elite] Error: {str(e)}")
            print(traceback.format_exc())

            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            error_response = {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }

            self.wfile.write(json.dumps(error_response).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
