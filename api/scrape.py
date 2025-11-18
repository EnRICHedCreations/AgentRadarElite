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

class Handler(BaseHTTPRequestHandler):
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
                'require_agent_email': False,  # Don't filter by email - we filter later
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
            print(f"[AgentRadar Elite] Scrape params: {scrape_params}")
            try:
                properties = scrape_property(**scrape_params)
                print(f"[AgentRadar Elite] Scrape successful, got {len(properties)} properties")
            except Exception as scrape_error:
                print(f"[AgentRadar Elite] Scrape error: {str(scrape_error)}")
                raise

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
            print(f"[AgentRadar Elite] Analyzing agents with min_listings={min_listings}...")
            print(f"[AgentRadar Elite] Total unique agents in properties: {properties['agent_name'].nunique() if 'agent_name' in properties.columns else 0}")

            # Check how many properties have agent emails
            if 'agent_email' in properties.columns:
                props_with_email = properties['agent_email'].notna().sum()
                print(f"[AgentRadar Elite] Properties with agent email: {props_with_email}/{len(properties)}")

            try:
                # First get all agents to debug
                from homeharvest.agent_broker import get_agent_activity
                all_agents = get_agent_activity(properties)
                print(f"[AgentRadar Elite] All agents before filtering: {len(all_agents)}")
                if not all_agents.empty:
                    print(f"[AgentRadar Elite] Sample agents: {all_agents[['agent_name', 'listing_count', 'agent_email', 'primary_phone']].head(3).to_dict('records')}")

                wholesale_agents = get_wholesale_friendly_agents(
                    properties,
                    min_listings=min_listings
                )
                print(f"[AgentRadar Elite] Found {len(wholesale_agents)} wholesale agents after filtering")
                if wholesale_agents.empty:
                    print(f"[AgentRadar Elite] DEBUG - wholesale_agents is empty!")
                    print(f"[AgentRadar Elite] DEBUG - Columns in all_agents: {list(all_agents.columns)}")
            except Exception as agent_error:
                print(f"[AgentRadar Elite] Agent analysis error: {str(agent_error)}")
                import traceback
                traceback.print_exc()
                raise

            # Get agent specialization
            try:
                specialization = analyze_agent_specialization(properties)
                print(f"[AgentRadar Elite] Specialization analysis complete")
            except Exception as spec_error:
                print(f"[AgentRadar Elite] Specialization error: {str(spec_error)}")
                raise

            # Rank properties by investment potential
            try:
                ranked_props = rank_by_investment_potential(properties)
                print(f"[AgentRadar Elite] Property ranking complete")
            except Exception as rank_error:
                print(f"[AgentRadar Elite] Ranking error: {str(rank_error)}")
                raise

            # Build agent data with ALL the details
            agents_list = []

            for idx, agent in wholesale_agents.iterrows():
                try:
                    agent_name = agent['agent_name']

                    # Get agent's properties
                    agent_props = ranked_props[ranked_props['agent_name'] == agent_name]

                    # Get specialization data
                    spec = specialization[specialization['agent_name'] == agent_name]

                    # Build listings array
                    listings = []
                    for _, prop in agent_props.iterrows():
                        try:
                            # Helper function to safely get values
                            def safe_get(series, key, default=''):
                                try:
                                    return series[key] if key in series.index and pd.notna(series[key]) else default
                                except:
                                    return default

                            # Use safe_get for all fields
                            def safe_float(val):
                                try:
                                    return float(val) if pd.notna(val) else None
                                except:
                                    return None

                            def safe_int(val):
                                try:
                                    return int(val) if pd.notna(val) else None
                                except:
                                    return None

                            listings.append({
                                'address': f"{safe_get(prop, 'full_street_line')}, {safe_get(prop, 'city')}, {safe_get(prop, 'state')} {safe_get(prop, 'zip_code')}".strip(),
                                'list_price': safe_float(safe_get(prop, 'list_price', None)),
                                'investment_score': safe_float(safe_get(prop, 'investment_score', None)),
                                'price_per_sqft': safe_float(safe_get(prop, 'price_per_sqft', None)),
                                'days_on_mls': safe_int(safe_get(prop, 'days_on_mls', None)),
                                'beds': safe_int(safe_get(prop, 'beds', None)),
                                'baths': safe_float(safe_get(prop, 'full_baths', None)),
                                'sqft': safe_int(safe_get(prop, 'sqft', None)),
                                'lot_sqft': safe_int(safe_get(prop, 'lot_sqft', None)),
                                'year_built': safe_int(safe_get(prop, 'year_built', None)),
                                'property_url': safe_get(prop, 'property_url', None),
                                'tags': safe_get(prop, 'tags', [])
                            })
                        except Exception as listing_error:
                            print(f"[AgentRadar Elite] Error processing listing: {str(listing_error)}")
                            continue

                    # Find best deal
                    best_deal = None
                    if not agent_props.empty and 'investment_score' in agent_props.columns:
                        # Filter out NaN scores before finding best
                        scored_props = agent_props[agent_props['investment_score'].notna()]
                        if not scored_props.empty:
                            best_prop = scored_props.nlargest(1, 'investment_score').iloc[0]

                            def safe_get_prop(series, key, default=''):
                                try:
                                    return series[key] if key in series.index and pd.notna(series[key]) else default
                                except:
                                    return default

                            def safe_float_prop(val):
                                try:
                                    return float(val) if pd.notna(val) else None
                                except:
                                    return None

                            best_deal = {
                                'address': f"{safe_get_prop(best_prop, 'full_street_line')}, {safe_get_prop(best_prop, 'city')}",
                                'list_price': safe_float_prop(safe_get_prop(best_prop, 'list_price', None)),
                                'investment_score': safe_float_prop(safe_get_prop(best_prop, 'investment_score', None)),
                                'property_url': safe_get_prop(best_prop, 'property_url', None)
                            }

                    # Helper to safely get agent values
                    def safe_agent_get(series, key, default=None):
                        try:
                            return series[key] if key in series.index and pd.notna(series[key]) else default
                        except:
                            return default

                    # Helper to safely convert to float
                    def try_float(val):
                        try:
                            return float(val)
                        except (ValueError, TypeError):
                            return None

                    # Build complete agent object
                    agent_data = {
                        'agent_name': agent_name,
                        'agent_email': safe_agent_get(agent, 'agent_email'),
                        'agent_phone': safe_agent_get(agent, 'primary_phone'),
                        'broker_name': safe_agent_get(agent, 'broker_name'),
                        'office_name': safe_agent_get(agent, 'office_name'),

                        # Wholesale scoring
                        'wholesale_score': float(safe_agent_get(agent, 'wholesale_score', 0)),
                        'listing_count': int(safe_agent_get(agent, 'listing_count', 0)),
                        'avg_price': float(safe_agent_get(agent, 'avg_price', 0)) if pd.notna(safe_agent_get(agent, 'avg_price')) else None,
                        'min_price': float(safe_agent_get(agent, 'min_price', 0)) if pd.notna(safe_agent_get(agent, 'min_price')) else None,
                        'max_price': float(safe_agent_get(agent, 'max_price', 0)) if pd.notna(safe_agent_get(agent, 'max_price')) else None,

                        # Specialization - wrap in try-except to handle any access issues
                        'price_category': (
                            spec.iloc[0]['price_category']
                            if (not spec.empty and 'price_category' in spec.columns)
                            else None
                        ),
                        'avg_sqft': (lambda: (
                            try_float(spec.loc[spec.index[0], 'avg_sqft'])
                            if pd.notna(spec.loc[spec.index[0], 'avg_sqft'])
                            else None
                        ) if 'avg_sqft' in spec.columns else None)() if not spec.empty else None,
                        'avg_beds': (lambda: (
                            try_float(spec.loc[spec.index[0], 'avg_beds'])
                            if pd.notna(spec.loc[spec.index[0], 'avg_beds'])
                            else None
                        ) if 'avg_beds' in spec.columns else None)() if not spec.empty else None,
                        'avg_baths': (lambda: (
                            try_float(spec.loc[spec.index[0], 'avg_baths'])
                            if pd.notna(spec.loc[spec.index[0], 'avg_baths'])
                            else None
                        ) if 'avg_baths' in spec.columns else None)() if not spec.empty else None,

                        # Investment insights
                        'avg_investment_score': float(agent_props['investment_score'].mean()) if 'investment_score' in agent_props.columns else None,
                        'best_deal': best_deal,

                        # Days on market
                        'avg_days_on_market': float(agent_props['days_on_mls'].mean()) if 'days_on_mls' in agent_props.columns and not agent_props['days_on_mls'].isna().all() else None,

                        # Listings
                        'listings': listings
                    }

                    agents_list.append(agent_data)

                except Exception as agent_error:
                    print(f"[AgentRadar Elite] Error processing agent {agent.get('agent_name', 'Unknown')}: {str(agent_error)}")
                    import traceback
                    traceback.print_exc()
                    continue

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

# Vercel requires this export
handler = Handler
