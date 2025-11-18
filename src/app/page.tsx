'use client';

import { useState } from 'react';

interface Agent {
  agent_name: string;
  agent_email: string;
  agent_phone: string;
  broker_name: string;
  office_name: string;

  // Wholesale scoring
  wholesale_score: number;
  listing_count: number;
  avg_price: number;
  min_price: number;
  max_price: number;

  // Specialization
  price_category: string;
  avg_sqft: number;
  avg_beds: number;
  avg_baths: number;

  // Investment insights
  avg_investment_score: number;
  avg_days_on_market: number;
  best_deal?: {
    address: string;
    list_price: number;
    investment_score: number;
    property_url?: string;
  };

  listings: Array<{
    address: string;
    list_price: number;
    investment_score: number;
    price_per_sqft: number;
    days_on_mls: number;
    beds: number;
    baths: number;
    sqft: number;
    lot_sqft: number;
    year_built: number;
    property_url?: string;
    tags?: string[];
  }>;
}

interface MarketStats {
  total_properties: number;
  avg_price: number;
  median_price: number;
  avg_price_per_sqft: number;
  avg_days_on_market: number;
  total_agents: number;
  avg_wholesale_score: number;
  high_potential_agents: number;
}

interface ScrapeResult {
  success: boolean;
  zip_code: string;
  preset: string;
  agents: Agent[];
  market_stats: MarketStats;
  scraped_at: string;
  error?: string;
}

export default function Home() {
  const [zipCode, setZipCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<ScrapeResult | null>(null);
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  // Smart preset
  const [preset, setPreset] = useState('investor_friendly');

  // Advanced filters
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [priceMin, setPriceMin] = useState('');
  const [priceMax, setPriceMax] = useState('');
  const [bedsMin, setBedsMin] = useState('');
  const [bathsMin, setBathsMin] = useState('');
  const [sqftMin, setSqftMin] = useState('');
  const [hoaFeeMax, setHoaFeeMax] = useState('');
  const [hasPool, setHasPool] = useState<boolean | null>(null);
  const [hasGarage, setHasGarage] = useState<boolean | null>(null);
  const [waterfront, setWaterfront] = useState<boolean | null>(null);
  const [garageMin, setGarageMin] = useState('');
  const [minListings, setMinListings] = useState('2');

  // Tag filters
  const [tagInput, setTagInput] = useState('');
  const [tagFilters, setTagFilters] = useState<string[]>([]);
  const [tagExclude, setTagExclude] = useState<string[]>([]);
  const [tagMatchType, setTagMatchType] = useState<'any' | 'all' | 'exact'>('any');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!zipCode || zipCode.length !== 5) {
      alert('Please enter a valid 5-digit ZIP code');
      return;
    }

    setLoading(true);
    setResults(null);

    try {
      // Build request body with all filters
      const requestBody: any = {
        zipCode,
        preset,
        minListings: parseInt(minListings) || 2,
      };

      // Add advanced filters if set
      if (priceMin) requestBody.priceMin = parseInt(priceMin);
      if (priceMax) requestBody.priceMax = parseInt(priceMax);
      if (bedsMin) requestBody.bedsMin = parseInt(bedsMin);
      if (bathsMin) requestBody.bathsMin = parseFloat(bathsMin);
      if (sqftMin) requestBody.sqftMin = parseInt(sqftMin);
      if (hoaFeeMax) requestBody.hoaFeeMax = parseInt(hoaFeeMax);
      if (hasPool !== null) requestBody.hasPool = hasPool;
      if (hasGarage !== null) requestBody.hasGarage = hasGarage;
      if (waterfront !== null) requestBody.waterfront = waterfront;
      if (garageMin) requestBody.garageMin = parseInt(garageMin);

      // Add tag filters
      if (tagFilters.length > 0) {
        requestBody.tagFilters = tagFilters;
        requestBody.tagMatchType = tagMatchType;
      }
      if (tagExclude.length > 0) {
        requestBody.tagExclude = tagExclude;
      }

      const response = await fetch('/api/scrape.py', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
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

    // Export detailed listings with all Elite fields
    const headers = [
      'Agent Name',
      'Agent Email',
      'Agent Phone',
      'Broker',
      'Office',
      'Wholesale Score',
      'Price Category',
      'Avg Price',
      'Property Address',
      'List Price',
      'Investment Score',
      'Price per Sqft',
      'Days on MLS',
      'Beds',
      'Baths',
      'Sqft',
      'Lot Sqft',
      'Year Built',
      'Tags',
      'Property URL'
    ];

    const rows: string[][] = [];

    results.agents.forEach(agent => {
      agent.listings.forEach(listing => {
        rows.push([
          agent.agent_name,
          agent.agent_email || 'N/A',
          agent.agent_phone || 'N/A',
          agent.broker_name || 'N/A',
          agent.office_name || 'N/A',
          agent.wholesale_score?.toFixed(1) || 'N/A',
          agent.price_category || 'N/A',
          agent.avg_price ? `$${agent.avg_price.toFixed(0)}` : 'N/A',
          listing.address || 'N/A',
          listing.list_price ? `$${listing.list_price}` : 'N/A',
          listing.investment_score?.toFixed(1) || 'N/A',
          listing.price_per_sqft ? `$${listing.price_per_sqft.toFixed(0)}` : 'N/A',
          listing.days_on_mls?.toString() || 'N/A',
          listing.beds?.toString() || 'N/A',
          listing.baths?.toString() || 'N/A',
          listing.sqft?.toString() || 'N/A',
          listing.lot_sqft?.toString() || 'N/A',
          listing.year_built?.toString() || 'N/A',
          listing.tags?.join('; ') || 'None',
          listing.property_url || 'N/A'
        ]);
      });
    });

    const csv = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `wholesale-agents-elite-${results.zip_code}-${Date.now()}.csv`;
    a.click();
  };

  const addTag = (isExclude: boolean = false) => {
    if (!tagInput.trim()) return;

    // Split by comma and process multiple tags
    const tags = tagInput
      .split(',')
      .map(t => t.trim().toLowerCase())
      .filter(t => t.length > 0);

    if (isExclude) {
      const newTags = tags.filter(tag => !tagExclude.includes(tag));
      if (newTags.length > 0) {
        setTagExclude([...tagExclude, ...newTags]);
      }
    } else {
      const newTags = tags.filter(tag => !tagFilters.includes(tag));
      if (newTags.length > 0) {
        setTagFilters([...tagFilters, ...newTags]);
      }
    }
    setTagInput('');
  };

  const removeTag = (tag: string, isExclude: boolean = false) => {
    if (isExclude) {
      setTagExclude(tagExclude.filter(t => t !== tag));
    } else {
      setTagFilters(tagFilters.filter(t => t !== tag));
    }
  };

  const getWholesaleScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-700 bg-green-100 border-green-300';
    if (score >= 60) return 'text-blue-700 bg-blue-100 border-blue-300';
    if (score >= 40) return 'text-yellow-700 bg-yellow-100 border-yellow-300';
    return 'text-gray-700 bg-gray-100 border-gray-300';
  };

  const getPriceCategoryColor = (category: string) => {
    switch (category) {
      case 'Budget': return 'text-green-700 bg-green-50 border-green-300';
      case 'Mid-Range': return 'text-blue-700 bg-blue-50 border-blue-300';
      case 'Upper-Mid': return 'text-purple-700 bg-purple-50 border-purple-300';
      case 'Luxury': return 'text-amber-700 bg-amber-50 border-amber-300';
      default: return 'text-gray-700 bg-gray-50 border-gray-300';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-block mb-3 px-4 py-1 bg-gradient-to-r from-blue-600 to-green-600 text-white rounded-full text-sm font-semibold">
            ELITE EDITION
          </div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent mb-3">
            AgentRadar Elite
          </h1>
          <p className="text-gray-600 text-lg">
            Find wholesale-friendly real estate agents with investment-grade properties
          </p>
        </div>

        {/* Search Form */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border border-gray-200">
          <form onSubmit={handleSearch}>
            <div className="grid md:grid-cols-3 gap-4 mb-4">
              {/* ZIP Code */}
              <div>
                <label htmlFor="zipCode" className="block text-sm font-medium text-gray-700 mb-2">
                  ZIP Code
                </label>
                <input
                  type="text"
                  id="zipCode"
                  value={zipCode}
                  onChange={(e) => setZipCode(e.target.value.replace(/\D/g, '').slice(0, 5))}
                  placeholder="Enter ZIP code"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  maxLength={5}
                />
              </div>

              {/* Smart Preset */}
              <div>
                <label htmlFor="preset" className="block text-sm font-medium text-gray-700 mb-2">
                  Investment Strategy
                </label>
                <select
                  id="preset"
                  value={preset}
                  onChange={(e) => setPreset(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="investor_friendly">Investor Friendly</option>
                  <option value="cash_flow">Cash Flow</option>
                  <option value="value_add">Value Add</option>
                  <option value="luxury_wholesale">Luxury Wholesale</option>
                  <option value="distressed">Distressed</option>
                  <option value="land">Land/Lots</option>
                </select>
              </div>

              {/* Min Listings */}
              <div>
                <label htmlFor="minListings" className="block text-sm font-medium text-gray-700 mb-2">
                  Min Agent Listings
                </label>
                <input
                  type="number"
                  id="minListings"
                  value={minListings}
                  onChange={(e) => setMinListings(e.target.value)}
                  placeholder="2"
                  min="1"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Search Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-green-600 text-white rounded-lg hover:from-blue-700 hover:to-green-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed font-semibold text-lg shadow-md"
            >
              {loading ? 'Analyzing Market...' : '🎯 Find Wholesale Agents'}
            </button>

            {/* Advanced Filters Toggle */}
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="mt-4 text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              {showAdvanced ? '▼ Hide' : '▶ Show'} Advanced Filters
            </button>

            {/* Advanced Filters */}
            {showAdvanced && (
              <div className="mt-4 pt-4 border-t border-gray-200 space-y-6">
                {/* Price & Size Filters */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-900 mb-3">Price & Size Filters</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Min Price</label>
                      <input
                        type="number"
                        value={priceMin}
                        onChange={(e) => setPriceMin(e.target.value)}
                        placeholder="$0"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Max Price</label>
                      <input
                        type="number"
                        value={priceMax}
                        onChange={(e) => setPriceMax(e.target.value)}
                        placeholder="No limit"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Min Beds</label>
                      <input
                        type="number"
                        value={bedsMin}
                        onChange={(e) => setBedsMin(e.target.value)}
                        placeholder="Any"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Min Baths</label>
                      <input
                        type="number"
                        step="0.5"
                        value={bathsMin}
                        onChange={(e) => setBathsMin(e.target.value)}
                        placeholder="Any"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Min Sqft</label>
                      <input
                        type="number"
                        value={sqftMin}
                        onChange={(e) => setSqftMin(e.target.value)}
                        placeholder="Any"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Max HOA Fee</label>
                      <input
                        type="number"
                        value={hoaFeeMax}
                        onChange={(e) => setHoaFeeMax(e.target.value)}
                        placeholder="No limit"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Min Garage</label>
                      <input
                        type="number"
                        value={garageMin}
                        onChange={(e) => setGarageMin(e.target.value)}
                        placeholder="Any"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                  </div>
                </div>

                {/* Feature Filters */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-900 mb-3">Property Features</h3>
                  <div className="flex flex-wrap gap-3">
                    <button
                      type="button"
                      onClick={() => setHasPool(hasPool === null ? true : hasPool ? false : null)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium border-2 ${
                        hasPool === true
                          ? 'bg-blue-100 border-blue-500 text-blue-700'
                          : hasPool === false
                          ? 'bg-red-100 border-red-500 text-red-700'
                          : 'bg-white border-gray-300 text-gray-700'
                      }`}
                    >
                      {hasPool === null ? '○ Pool' : hasPool ? '✓ Has Pool' : '✗ No Pool'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setHasGarage(hasGarage === null ? true : hasGarage ? false : null)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium border-2 ${
                        hasGarage === true
                          ? 'bg-blue-100 border-blue-500 text-blue-700'
                          : hasGarage === false
                          ? 'bg-red-100 border-red-500 text-red-700'
                          : 'bg-white border-gray-300 text-gray-700'
                      }`}
                    >
                      {hasGarage === null ? '○ Garage' : hasGarage ? '✓ Has Garage' : '✗ No Garage'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setWaterfront(waterfront === null ? true : waterfront ? false : null)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium border-2 ${
                        waterfront === true
                          ? 'bg-blue-100 border-blue-500 text-blue-700'
                          : waterfront === false
                          ? 'bg-red-100 border-red-500 text-red-700'
                          : 'bg-white border-gray-300 text-gray-700'
                      }`}
                    >
                      {waterfront === null ? '○ Waterfront' : waterfront ? '✓ Waterfront' : '✗ Not Waterfront'}
                    </button>
                  </div>
                </div>

                {/* Tag Filters */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-900 mb-3">Tag Filters</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs text-gray-600 mb-2">Include Tags</label>
                      <div className="flex gap-2 mb-2">
                        <input
                          type="text"
                          value={tagInput}
                          onChange={(e) => setTagInput(e.target.value)}
                          onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag(false))}
                          placeholder="e.g., swimming_pool"
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        />
                        <button
                          type="button"
                          onClick={() => addTag(false)}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                        >
                          Add
                        </button>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {tagFilters.map(tag => (
                          <span key={tag} className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                            {tag}
                            <button type="button" onClick={() => removeTag(tag, false)} className="hover:text-blue-900 font-bold">×</button>
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-2">Exclude Tags</label>
                      <div className="flex gap-2 mb-2">
                        <input
                          type="text"
                          value={tagInput}
                          onChange={(e) => setTagInput(e.target.value)}
                          onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag(true))}
                          placeholder="e.g., fixer_upper"
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        />
                        <button
                          type="button"
                          onClick={() => addTag(true)}
                          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
                        >
                          Add
                        </button>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {tagExclude.map(tag => (
                          <span key={tag} className="inline-flex items-center gap-1 px-3 py-1 bg-red-100 text-red-800 rounded-full text-xs">
                            {tag}
                            <button type="button" onClick={() => removeTag(tag, true)} className="hover:text-red-900 font-bold">×</button>
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                  {tagFilters.length > 0 && (
                    <div className="mt-2">
                      <label className="text-xs text-gray-600">Match Type: </label>
                      <select
                        value={tagMatchType}
                        onChange={(e) => setTagMatchType(e.target.value as 'any' | 'all' | 'exact')}
                        className="ml-2 px-3 py-1 border border-gray-300 rounded-lg text-xs"
                      >
                        <option value="any">Any (OR)</option>
                        <option value="all">All (AND)</option>
                        <option value="exact">Exact</option>
                      </select>
                    </div>
                  )}
                </div>
              </div>
            )}
          </form>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600 rounded-full"></div>
            <p className="mt-4 text-lg font-medium text-gray-700">Analyzing Market Intelligence...</p>
            <p className="text-sm text-gray-500">Scanning properties • Scoring agents • Calculating insights</p>
          </div>
        )}

        {/* Results */}
        {results && !loading && (
          <div>
            {/* Market Statistics Dashboard */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-6 border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">Market Intelligence</h2>
                {results.agents.length > 0 && (
                  <button
                    onClick={exportToCSV}
                    className="px-4 py-2 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-lg hover:from-green-700 hover:to-blue-700 font-medium text-sm shadow-md"
                  >
                    📥 Export All Data
                  </button>
                )}
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
                  <div className="text-xs text-blue-600 font-semibold uppercase mb-1">ZIP Code</div>
                  <div className="text-3xl font-bold text-blue-900">{results.zip_code}</div>
                </div>
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
                  <div className="text-xs text-green-600 font-semibold uppercase mb-1">Total Properties</div>
                  <div className="text-3xl font-bold text-green-900">{results.market_stats.total_properties}</div>
                </div>
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
                  <div className="text-xs text-purple-600 font-semibold uppercase mb-1">Wholesale Agents</div>
                  <div className="text-3xl font-bold text-purple-900">{results.agents.length}</div>
                </div>
                <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-lg p-4 border border-amber-200">
                  <div className="text-xs text-amber-600 font-semibold uppercase mb-1">High Potential</div>
                  <div className="text-3xl font-bold text-amber-900">{results.market_stats.high_potential_agents}</div>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-600">Avg Price</div>
                  <div className="text-lg font-bold text-gray-900">
                    ${results.market_stats.avg_price ? Math.round(results.market_stats.avg_price).toLocaleString() : 'N/A'}
                  </div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-600">Median Price</div>
                  <div className="text-lg font-bold text-gray-900">
                    ${results.market_stats.median_price ? Math.round(results.market_stats.median_price).toLocaleString() : 'N/A'}
                  </div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-600">Avg $/Sqft</div>
                  <div className="text-lg font-bold text-gray-900">
                    ${results.market_stats.avg_price_per_sqft ? Math.round(results.market_stats.avg_price_per_sqft) : 'N/A'}
                  </div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-600">Avg Days on Market</div>
                  <div className="text-lg font-bold text-gray-900">
                    {results.market_stats.avg_days_on_market ? Math.round(results.market_stats.avg_days_on_market) : 'N/A'}
                  </div>
                </div>
              </div>
            </div>

            {/* Agents List */}
            {results.agents.length === 0 ? (
              <div className="bg-white rounded-xl shadow-lg p-12 text-center border border-gray-200">
                <div className="text-gray-400 text-6xl mb-4">🎯</div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  No Wholesale Agents Found
                </h3>
                <p className="text-gray-600">
                  Try adjusting your filters or search a different ZIP code.
                </p>
              </div>
            ) : (
              <div className="space-y-5">
                {results.agents.map((agent, index) => (
                  <div key={index} className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200 hover:shadow-xl transition-shadow">
                    {/* Agent Header */}
                    <div className="bg-gradient-to-r from-blue-50 to-green-50 px-6 py-4 border-b border-gray-200">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-2xl font-bold text-gray-900">
                              {agent.agent_name}
                            </h3>
                            <span className={`px-4 py-1.5 rounded-full text-sm font-bold border-2 ${getWholesaleScoreColor(agent.wholesale_score)}`}>
                              ⭐ {agent.wholesale_score.toFixed(0)}
                            </span>
                            <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getPriceCategoryColor(agent.price_category)}`}>
                              {agent.price_category}
                            </span>
                          </div>
                          <div className="flex items-center gap-4 text-sm text-gray-600">
                            <span>{agent.broker_name || 'N/A'}</span>
                            <span>•</span>
                            <span>{agent.listing_count} listings</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Agent Details */}
                    <div className="p-6">
                      {/* Contact Info */}
                      <div className="grid md:grid-cols-2 gap-3 mb-5">
                        <div className="flex items-center gap-2">
                          <span className="text-gray-500">📧</span>
                          <a href={`mailto:${agent.agent_email}`} className="text-blue-600 hover:underline font-medium">
                            {agent.agent_email || 'N/A'}
                          </a>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-gray-500">📞</span>
                          <a href={`tel:${agent.agent_phone}`} className="text-blue-600 hover:underline font-medium">
                            {agent.agent_phone || 'N/A'}
                          </a>
                        </div>
                      </div>

                      {/* Stats Grid */}
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-5">
                        <div className="bg-blue-50 rounded-lg p-3 text-center border border-blue-200">
                          <div className="text-xs text-blue-600 font-semibold mb-1">Avg Price</div>
                          <div className="text-lg font-bold text-blue-900">
                            ${agent.avg_price ? Math.round(agent.avg_price / 1000) + 'K' : 'N/A'}
                          </div>
                        </div>
                        <div className="bg-green-50 rounded-lg p-3 text-center border border-green-200">
                          <div className="text-xs text-green-600 font-semibold mb-1">Avg Sqft</div>
                          <div className="text-lg font-bold text-green-900">
                            {agent.avg_sqft ? Math.round(agent.avg_sqft).toLocaleString() : 'N/A'}
                          </div>
                        </div>
                        <div className="bg-purple-50 rounded-lg p-3 text-center border border-purple-200">
                          <div className="text-xs text-purple-600 font-semibold mb-1">Avg Beds</div>
                          <div className="text-lg font-bold text-purple-900">
                            {agent.avg_beds ? agent.avg_beds.toFixed(1) : 'N/A'}
                          </div>
                        </div>
                        <div className="bg-orange-50 rounded-lg p-3 text-center border border-orange-200">
                          <div className="text-xs text-orange-600 font-semibold mb-1">Days on Mkt</div>
                          <div className="text-lg font-bold text-orange-900">
                            {agent.avg_days_on_market ? Math.round(agent.avg_days_on_market) : 'N/A'}
                          </div>
                        </div>
                        <div className="bg-amber-50 rounded-lg p-3 text-center border border-amber-200">
                          <div className="text-xs text-amber-600 font-semibold mb-1">Invest Score</div>
                          <div className="text-lg font-bold text-amber-900">
                            {agent.avg_investment_score ? agent.avg_investment_score.toFixed(0) : 'N/A'}
                          </div>
                        </div>
                      </div>

                      {/* Best Deal Highlight */}
                      {agent.best_deal && (
                        <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4 mb-5 border-2 border-green-300">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-xl">🏆</span>
                            <h4 className="font-bold text-gray-900">Best Investment Deal</h4>
                            <span className="ml-auto px-3 py-1 bg-green-200 text-green-800 rounded-full text-xs font-bold">
                              Score: {agent.best_deal.investment_score.toFixed(0)}
                            </span>
                          </div>
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="font-medium text-gray-900">{agent.best_deal.address}</div>
                              <div className="text-sm text-gray-600">
                                ${agent.best_deal.list_price.toLocaleString()}
                              </div>
                            </div>
                            {agent.best_deal.property_url && (
                              <a
                                href={agent.best_deal.property_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
                              >
                                View →
                              </a>
                            )}
                          </div>
                        </div>
                      )}

                      {/* View Listings Button */}
                      <button
                        onClick={() => setExpandedAgent(expandedAgent === agent.agent_email ? null : agent.agent_email)}
                        className="w-full px-4 py-3 bg-gradient-to-r from-blue-600 to-green-600 text-white rounded-lg hover:from-blue-700 hover:to-green-700 font-semibold shadow-md"
                      >
                        {expandedAgent === agent.agent_email ? '▲ Hide All Listings' : `▼ View All ${agent.listing_count} Listings`}
                      </button>
                    </div>

                    {/* Expanded Listings */}
                    {expandedAgent === agent.agent_email && (
                      <div className="px-6 pb-6">
                        <div className="bg-gray-50 rounded-lg p-4">
                          <h4 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                            <span className="text-lg">📋</span>
                            All Properties ({agent.listings.length})
                          </h4>
                          <div className="space-y-3">
                            {agent.listings.map((listing, idx) => (
                              <div key={idx} className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3">
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                      <div className="font-bold text-gray-900">{listing.address}</div>
                                      {listing.investment_score && (
                                        <span className="px-2 py-0.5 bg-amber-100 text-amber-800 rounded-full text-xs font-bold border border-amber-300">
                                          Score: {listing.investment_score.toFixed(0)}
                                        </span>
                                      )}
                                    </div>
                                    <div className="text-sm text-gray-600 mb-2">
                                      {listing.beds} bed · {listing.baths} bath · {listing.sqft?.toLocaleString()} sqft
                                      {listing.lot_sqft && ` · ${(listing.lot_sqft / 43560).toFixed(2)} acre lot`}
                                      {listing.year_built && ` · Built ${listing.year_built}`}
                                    </div>
                                    {listing.tags && listing.tags.length > 0 && (
                                      <div className="flex flex-wrap gap-1 mt-2">
                                        {listing.tags.slice(0, 5).map((tag, tagIdx) => (
                                          <span
                                            key={tagIdx}
                                            className="inline-block px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs font-medium"
                                          >
                                            {tag.replace(/_/g, ' ')}
                                          </span>
                                        ))}
                                        {listing.tags.length > 5 && (
                                          <span className="inline-block px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
                                            +{listing.tags.length - 5} more
                                          </span>
                                        )}
                                      </div>
                                    )}
                                  </div>
                                  <div className="text-right">
                                    <div className="text-xl font-bold text-gray-900 mb-1">
                                      ${listing.list_price?.toLocaleString()}
                                    </div>
                                    {listing.price_per_sqft && (
                                      <div className="text-sm text-gray-600 mb-1">
                                        ${listing.price_per_sqft.toFixed(0)}/sqft
                                      </div>
                                    )}
                                    <div className="text-sm font-medium text-orange-600 mb-2">
                                      {listing.days_on_mls} days on market
                                    </div>
                                    {listing.property_url && (
                                      <a
                                        href={listing.property_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="inline-block px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-xs font-medium"
                                      >
                                        View Listing →
                                      </a>
                                    )}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
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
