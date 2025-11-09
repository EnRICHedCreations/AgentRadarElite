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
