# AgentRadar - Simple Tool Development Plan

## Project Overview

A simple, single-page web tool that scrapes a zip code and identifies frustrated real estate agents with stale listings. No database, no authentication - just enter a zip code and get results.

### What It Does
1. User enters a zip code
2. Scrapes listings from that zip code using HomeHarvest
3. Identifies agents with stale listings (90+ days on market)
4. Calculates "frustration score" for each agent
5. Displays results in a sortable table
6. Allows export to CSV

---

## Technology Stack

### Frontend & Backend
- **Framework**: Next.js 14 (App Router) with TypeScript
- **Styling**: Tailwind CSS
- **UI**: Basic HTML components (no component library needed)
- **Deployment**: Vercel
- **Scraping**: Python serverless function with HomeHarvest

### No Database Required
- Results stored in browser session only
- Export to CSV for saving

---

## Project Structure

```
agentradar-simple/
├── src/
│   └── app/
│       ├── page.tsx              # Main page (only page)
│       ├── layout.tsx            # Root layout
│       └── api/
│           └── scrape/
│               └── route.ts      # API route that calls Python
├── api/
│   ├── scrape.py                 # Python scraping function
│   └── requirements.txt          # Python dependencies
├── public/
├── .env.local
├── .gitignore
├── next.config.js
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── vercel.json                   # Vercel config for Python function
```

---

## Setup Instructions

### 1. Create Next.js Project

```bash
# Create project
npx create-next-app@latest agentradar-simple --typescript --tailwind --app --src-dir --no-eslint

cd agentradar-simple

# Install minimal dependencies
npm install
```

### 2. Create Python Scraping Function

**File**: `api/scrape.py`

```python
from http.server import BaseHTTPRequestHandler
import json
from homeharvest import scrape_property
from datetime import datetime
import traceback

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            zip_code = data.get('zipCode')
            
            if not zip_code:
                self.send_error(400, "ZIP code is required")
                return
            
            print(f"Scraping ZIP code: {zip_code}")
            
            # Scrape properties
            properties = scrape_property(
                location=zip_code,
                listing_type="for_sale",
                past_days=365,  # Get last year of listings
                mls_only=True   # Only MLS listings have agent info
            )
            
            # Convert to dict
            props_list = properties.to_dict('records')
            
            print(f"Found {len(props_list)} total properties")
            
            # Filter for stale listings (90+ days)
            stale_props = [
                p for p in props_list 
                if p.get('days_on_mls') and p.get('days_on_mls') >= 90
            ]
            
            print(f"Found {len(stale_props)} stale properties")
            
            # Group by agent
            agents_map = {}
            
            for prop in stale_props:
                agent_email = prop.get('agent_email')
                
                if not agent_email:
                    continue
                
                if agent_email not in agents_map:
                    agents_map[agent_email] = {
                        'agent_name': prop.get('agent_name') or 'Unknown',
                        'agent_email': agent_email,
                        'agent_phone': prop.get('agent_phone'),
                        'broker_name': prop.get('broker_name'),
                        'office_name': prop.get('office_name'),
                        'office_phone': prop.get('office_phone'),
                        'stale_listings': []
                    }
                
                # Add property to agent's listings
                agents_map[agent_email]['stale_listings'].append({
                    'address': f"{prop.get('street', '')}, {prop.get('city', '')}, {prop.get('state', '')} {prop.get('zip_code', '')}".strip(),
                    'list_price': prop.get('list_price'),
                    'days_on_mls': prop.get('days_on_mls'),
                    'beds': prop.get('beds'),
                    'baths': prop.get('full_baths'),
                    'sqft': prop.get('sqft'),
                    'property_url': prop.get('property_url')
                })
            
            # Calculate frustration score for each agent
            agents_list = []
            
            for agent_data in agents_map.values():
                stale_count = len(agent_data['stale_listings'])
                
                if stale_count == 0:
                    continue
                
                # Calculate average days on market
                total_dom = sum(l['days_on_mls'] for l in agent_data['stale_listings'])
                avg_dom = total_dom / stale_count
                
                # Frustration Score Algorithm:
                # Base: 10 points per stale listing (max 50 points)
                # + 0.25 points per average day on market (max 50 points)
                # Result: 0-100 scale
                
                listing_score = min(50, stale_count * 10)
                dom_score = min(50, avg_dom * 0.25)
                frustration_score = int(listing_score + dom_score)
                
                agents_list.append({
                    'agent_name': agent_data['agent_name'],
                    'agent_email': agent_data['agent_email'],
                    'agent_phone': agent_data['agent_phone'] or 'N/A',
                    'broker_name': agent_data['broker_name'] or 'N/A',
                    'office_name': agent_data['office_name'] or 'N/A',
                    'office_phone': agent_data['office_phone'] or 'N/A',
                    'stale_listing_count': stale_count,
                    'avg_days_on_market': round(avg_dom, 1),
                    'frustration_score': frustration_score,
                    'listings': agent_data['stale_listings']
                })
            
            # Sort by frustration score (highest first)
            agents_list.sort(key=lambda x: x['frustration_score'], reverse=True)
            
            print(f"Found {len(agents_list)} agents with stale listings")
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'success': True,
                'zip_code': zip_code,
                'total_properties': len(props_list),
                'stale_properties': len(stale_props),
                'agents': agents_list,
                'scraped_at': datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_response = {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }
            
            self.wfile.write(json.dumps(error_response).encode())
```

**File**: `api/requirements.txt`

```
homeharvest>=0.4.0
pandas
```

### 3. Configure Vercel for Python

**File**: `vercel.json`

```json
{
  "functions": {
    "api/scrape.py": {
      "runtime": "python3.9",
      "maxDuration": 300
    }
  }
}
```

### 4. Create Main Page

**File**: `src/app/page.tsx`

```typescript
'use client';

import { useState } from 'react';

interface Agent {
  agent_name: string;
  agent_email: string;
  agent_phone: string;
  broker_name: string;
  office_name: string;
  stale_listing_count: number;
  avg_days_on_market: number;
  frustration_score: number;
  listings: Array<{
    address: string;
    list_price: number;
    days_on_mls: number;
    beds: number;
    baths: number;
    sqft: number;
    property_url?: string;
  }>;
}

interface ScrapeResult {
  success: boolean;
  zip_code: string;
  total_properties: number;
  stale_properties: number;
  agents: Agent[];
  scraped_at: string;
  error?: string;
}

export default function Home() {
  const [zipCode, setZipCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<ScrapeResult | null>(null);
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!zipCode || zipCode.length !== 5) {
      alert('Please enter a valid 5-digit ZIP code');
      return;
    }

    setLoading(true);
    setResults(null);

    try {
      const response = await fetch('/api/scrape.py', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ zipCode }),
      });

      const data = await response.json();
      
      if (data.success) {
        setResults(data);
      } else {
        alert(`Error: ${data.error}`);
      }
    } catch (error: any) {
      alert(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const exportToCSV = () => {
    if (!results || results.agents.length === 0) return;

    const headers = [
      'Agent Name',
      'Email',
      'Phone',
      'Broker',
      'Office',
      'Stale Listings',
      'Avg Days on Market',
      'Frustration Score'
    ];

    const rows = results.agents.map(agent => [
      agent.agent_name,
      agent.agent_email,
      agent.agent_phone,
      agent.broker_name,
      agent.office_name,
      agent.stale_listing_count.toString(),
      agent.avg_days_on_market.toString(),
      agent.frustration_score.toString()
    ]);

    const csv = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `frustrated-agents-${results.zip_code}-${Date.now()}.csv`;
    a.click();
  };

  const getFrustrationColor = (score: number) => {
    if (score >= 80) return 'text-red-600 bg-red-100';
    if (score >= 60) return 'text-orange-600 bg-orange-100';
    if (score >= 40) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            AgentRadar
          </h1>
          <p className="text-gray-600">
            Find frustrated real estate agents with stale listings
          </p>
        </div>

        {/* Search Form */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <form onSubmit={handleSearch} className="flex gap-4 items-end">
            <div className="flex-1">
              <label htmlFor="zipCode" className="block text-sm font-medium text-gray-700 mb-2">
                ZIP Code
              </label>
              <input
                type="text"
                id="zipCode"
                value={zipCode}
                onChange={(e) => setZipCode(e.target.value.replace(/\D/g, '').slice(0, 5))}
                placeholder="Enter 5-digit ZIP code"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                maxLength={5}
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
            >
              {loading ? 'Searching...' : 'Find Agents'}
            </button>
          </form>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Scraping listings and analyzing agents...</p>
            <p className="text-sm text-gray-500">This may take 30-60 seconds</p>
          </div>
        )}

        {/* Results */}
        {results && !loading && (
          <div>
            {/* Stats Bar */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div className="text-sm text-gray-600">ZIP Code</div>
                  <div className="text-2xl font-bold text-gray-900">{results.zip_code}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Total Properties</div>
                  <div className="text-2xl font-bold text-gray-900">{results.total_properties}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Stale Listings</div>
                  <div className="text-2xl font-bold text-gray-900">{results.stale_properties}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Frustrated Agents</div>
                  <div className="text-2xl font-bold text-gray-900">{results.agents.length}</div>
                </div>
              </div>
              
              {results.agents.length > 0 && (
                <div className="mt-4 flex justify-end">
                  <button
                    onClick={exportToCSV}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium text-sm"
                  >
                    Export to CSV
                  </button>
                </div>
              )}
            </div>

            {/* Agents List */}
            {results.agents.length === 0 ? (
              <div className="bg-white rounded-lg shadow-md p-12 text-center">
                <div className="text-gray-400 text-5xl mb-4">🎉</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  No frustrated agents found
                </h3>
                <p className="text-gray-600">
                  There are no agents with stale listings (90+ days) in this ZIP code.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {results.agents.map((agent, index) => (
                  <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden">
                    <div className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-xl font-bold text-gray-900">
                              {agent.agent_name}
                            </h3>
                            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getFrustrationColor(agent.frustration_score)}`}>
                              Frustration Score: {agent.frustration_score}
                            </span>
                          </div>
                          
                          <div className="grid md:grid-cols-2 gap-2 text-sm text-gray-600 mb-4">
                            <div>
                              <span className="font-medium">Email:</span>{' '}
                              <a href={`mailto:${agent.agent_email}`} className="text-blue-600 hover:underline">
                                {agent.agent_email}
                              </a>
                            </div>
                            <div>
                              <span className="font-medium">Phone:</span>{' '}
                              <a href={`tel:${agent.agent_phone}`} className="text-blue-600 hover:underline">
                                {agent.agent_phone}
                              </a>
                            </div>
                            <div>
                              <span className="font-medium">Broker:</span> {agent.broker_name}
                            </div>
                            <div>
                              <span className="font-medium">Office:</span> {agent.office_name}
                            </div>
                          </div>
                          
                          <div className="flex gap-6">
                            <div>
                              <div className="text-2xl font-bold text-gray-900">
                                {agent.stale_listing_count}
                              </div>
                              <div className="text-sm text-gray-600">Stale Listings</div>
                            </div>
                            <div>
                              <div className="text-2xl font-bold text-gray-900">
                                {agent.avg_days_on_market}
                              </div>
                              <div className="text-sm text-gray-600">Avg Days on Market</div>
                            </div>
                          </div>
                        </div>
                        
                        <button
                          onClick={() => setExpandedAgent(expandedAgent === agent.agent_email ? null : agent.agent_email)}
                          className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 font-medium"
                        >
                          {expandedAgent === agent.agent_email ? 'Hide' : 'View'} Listings
                        </button>
                      </div>
                      
                      {/* Expanded Listings */}
                      {expandedAgent === agent.agent_email && (
                        <div className="mt-4 pt-4 border-t">
                          <h4 className="font-semibold text-gray-900 mb-3">
                            Stale Listings ({agent.listings.length})
                          </h4>
                          <div className="space-y-2">
                            {agent.listings.map((listing, idx) => (
                              <div key={idx} className="bg-gray-50 p-3 rounded-md text-sm">
                                <div className="flex justify-between items-start">
                                  <div className="flex-1">
                                    <div className="font-medium text-gray-900">{listing.address}</div>
                                    <div className="text-gray-600">
                                      {listing.beds} bed · {listing.baths} bath · {listing.sqft?.toLocaleString()} sqft
                                    </div>
                                  </div>
                                  <div className="text-right">
                                    <div className="font-bold text-gray-900">
                                      ${listing.list_price?.toLocaleString()}
                                    </div>
                                    <div className="text-red-600 font-medium">
                                      {listing.days_on_mls} days
                                    </div>
                                  </div>
                                </div>
                                {listing.property_url && (
                                  <a
                                    href={listing.property_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-600 hover:underline text-xs mt-1 inline-block"
                                  >
                                    View on Realtor.com →
                                  </a>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
```

### 5. Update Layout

**File**: `src/app/layout.tsx`

```typescript
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AgentRadar - Find Frustrated Real Estate Agents",
  description: "Identify motivated listing agents with stale properties",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

### 6. Configure Next.js

**File**: `next.config.js`

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};

module.exports = nextConfig;
```

### 7. Environment Variables

**File**: `.env.local`

```env
# No environment variables needed for basic version
```

---

## Deployment to Vercel

### 1. Initialize Git

```bash
git init
git add .
git commit -m "Initial commit"
```

### 2. Push to GitHub

```bash
# Create repo on GitHub first, then:
git remote add origin https://github.com/yourusername/agentradar-simple.git
git branch -M main
git push -u origin main
```

### 3. Deploy on Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your GitHub repository
4. Vercel will auto-detect Next.js
5. Click "Deploy"

That's it! Your app will be live at `https://your-project.vercel.app`

---

## How to Use

1. Open the app in your browser
2. Enter a 5-digit ZIP code
3. Click "Find Agents"
4. Wait 30-60 seconds while it scrapes
5. View results sorted by frustration score
6. Click "View Listings" to see each agent's properties
7. Click "Export to CSV" to download the data

---

## Understanding the Frustration Score

The algorithm calculates a 0-100 score based on:

**Formula:**
- **Listing Score** (0-50 points): 10 points per stale listing (capped at 50)
- **Days on Market Score** (0-50 points): 0.25 points per average day on market (capped at 50)
- **Total**: Listing Score + DOM Score = Frustration Score (0-100)

**Examples:**
- Agent with 3 stale listings averaging 100 days: Score = 30 + 25 = **55** (moderate)
- Agent with 5 stale listings averaging 180 days: Score = 50 + 45 = **95** (very high)
- Agent with 2 stale listings averaging 95 days: Score = 20 + 24 = **44** (low-moderate)

**Color Coding:**
- 🔴 80-100: Very frustrated (red)
- 🟠 60-79: Frustrated (orange)
- 🟡 40-59: Somewhat frustrated (yellow)
- 🟢 0-39: Mildly frustrated (green)

---

## Customization Options

### Adjust Stale Listing Threshold

In `api/scrape.py`, change line 43:
```python
# Current: 90+ days
if p.get('days_on_mls') and p.get('days_on_mls') >= 90:

# Make it 60+ days for more results:
if p.get('days_on_mls') and p.get('days_on_mls') >= 60:

# Make it 120+ days for only very stale:
if p.get('days_on_mls') and p.get('days_on_mls') >= 120:
```

### Adjust Frustration Score Algorithm

In `api/scrape.py`, change lines 89-95:
```python
# Make listing count more important (15 points each instead of 10):
listing_score = min(50, stale_count * 15)

# Make days on market less important (0.15 instead of 0.25):
dom_score = min(50, avg_dom * 0.15)
```

### Change Scraping Time Range

In `api/scrape.py`, change line 33:
```python
# Current: Last 365 days
past_days=365,

# Change to 180 days for more recent only:
past_days=180,
```

---

## Troubleshooting

### "No agents found"
- Try a more populated ZIP code
- Lower the stale listing threshold (see customization above)
- Check that the ZIP code has active listings

### Scraping takes too long / times out
- Vercel functions have a 300-second timeout (already configured)
- If still timing out, reduce `past_days` parameter
- Try a smaller/less populated ZIP code

### Python function not working
- Ensure `api/requirements.txt` exists with `homeharvest` listed
- Check Vercel deployment logs for Python errors
- Verify `vercel.json` is configured correctly

### Rate limiting (403 errors)
- HomeHarvest may be rate-limited by Realtor.com
- Wait a few minutes between searches
- Don't scrape the same ZIP code repeatedly

---

## Limitations

This simple version has intentional limitations:
- ❌ No data persistence (results disappear on refresh)
- ❌ No authentication/user accounts
- ❌ No history of past searches
- ❌ One ZIP code at a time
- ❌ No scheduling/automated scraping
- ✅ But it works perfectly for quick manual searches!

---

## Potential Enhancements (Optional)

If you want to add features later:

1. **Local Storage**: Save results in browser
2. **Multiple ZIP Codes**: Search multiple at once
3. **Email Results**: Send CSV via email
4. **Property Photos**: Show listing images
5. **Price Drop Tracking**: Add recent price reductions to score
6. **Agent Notes**: Let yourself add notes about agents
7. **Print View**: Formatted for printing reports

---

## File Checklist

Before deploying, ensure you have:

- [ ] `src/app/page.tsx` - Main page
- [ ] `src/app/layout.tsx` - Layout
- [ ] `api/scrape.py` - Python scraping function
- [ ] `api/requirements.txt` - Python dependencies
- [ ] `vercel.json` - Vercel configuration
- [ ] `next.config.js` - Next.js config
- [ ] `tailwind.config.ts` - Tailwind config
- [ ] `tsconfig.json` - TypeScript config
- [ ] `.gitignore` - Git ignore file

---

## Total Development Time

Expected time to build: **2-4 hours**

Breakdown:
- Project setup: 30 mins
- Python scraping function: 1 hour
- Frontend page: 1-2 hours
- Testing & deployment: 30 mins

---

## Cost

**Free!** Everything runs on Vercel's free tier:
- Unlimited deployments
- Serverless functions included
- No database = no database costs

The only cost is your time. 🎉

---

That's it! You now have a simple but powerful tool to find frustrated agents in any ZIP code. Good luck with your wholesaling! 🏠