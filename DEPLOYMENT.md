# AgentRadar - Deployment Guide

## ✅ Project Complete!

Your simple AgentRadar tool is ready to deploy. This is a single-page app with no database or authentication - just enter a ZIP code and get results.

---

## 🚀 Deploy to Vercel (5 Minutes)

### Step 1: Push to GitHub

```bash
# Create a new repository on GitHub first, then:
git remote add origin https://github.com/EnRICHedCreations/AgentRadar.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Vercel

1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Import your GitHub repository: `EnRICHedCreations/AgentRadar`
4. Vercel will auto-detect Next.js configuration
5. Click "Deploy"

**That's it!** Your app will be live at `https://your-project.vercel.app`

---

## 📋 What's Included

### Frontend (Next.js 14)
- ✅ Single-page interface
- ✅ ZIP code search form
- ✅ Loading states
- ✅ Results display with frustration scores
- ✅ Expandable listing details
- ✅ Export to CSV functionality
- ✅ Responsive design with Tailwind CSS

### Backend (Python Serverless)
- ✅ HomeHarvest integration
- ✅ Property scraping (365-day range)
- ✅ Stale listing filter (90+ days)
- ✅ Agent grouping and scoring
- ✅ Frustration score algorithm (0-100)
- ✅ Error handling
- ✅ 300-second timeout configured

### Configuration
- ✅ Vercel Python runtime configured
- ✅ Next.js optimized for production
- ✅ Tailwind CSS configured
- ✅ TypeScript setup
- ✅ Git initialized

---

## 🎯 How It Works

### User Flow
1. User enters a 5-digit ZIP code
2. Frontend sends POST request to `/api/scrape.py`
3. Python function scrapes listings using HomeHarvest
4. Filters for stale listings (90+ days on market)
5. Groups by agent and calculates frustration scores
6. Returns JSON results to frontend
7. Frontend displays results with interactive UI
8. User can view listing details and export to CSV

### Frustration Score Algorithm

**Formula:**
```
Listing Score (0-50) = min(50, stale_count * 10)
DOM Score (0-50) = min(50, avg_days_on_market * 0.25)
Frustration Score = Listing Score + DOM Score
```

**Examples:**
- 3 stale listings, 100 avg days = 30 + 25 = **55** (moderate)
- 5 stale listings, 180 avg days = 50 + 45 = **95** (very high)
- 2 stale listings, 95 avg days = 20 + 24 = **44** (low-moderate)

---

## 🔧 Customization

### Adjust Stale Listing Threshold

Edit `api/scrape.py` line 38:
```python
# Current: 90+ days
if p.get('days_on_mls') and p.get('days_on_mls') >= 90:

# Change to 60+ days for more results:
if p.get('days_on_mls') and p.get('days_on_mls') >= 60:
```

### Adjust Frustration Score Weight

Edit `api/scrape.py` lines 93-94:
```python
# Make listing count more important:
listing_score = min(50, stale_count * 15)  # Was: * 10

# Make days on market less important:
dom_score = min(50, avg_dom * 0.15)  # Was: * 0.25
```

### Change Scraping Time Range

Edit `api/scrape.py` line 26:
```python
# Current: Last 365 days
past_days=365,

# Change to 180 days:
past_days=180,
```

---

## 🐛 Troubleshooting

### No Agents Found
- Try a more populated ZIP code
- Lower the stale listing threshold
- Check that ZIP code has active listings

### Scraping Times Out
- Already configured for 300-second max
- Try a smaller/less populated ZIP code
- Reduce `past_days` parameter

### Python Function Not Working
- Check Vercel deployment logs
- Ensure `api/requirements.txt` exists
- Verify `vercel.json` configuration

### Rate Limiting (403 Errors)
- HomeHarvest may be rate-limited
- Wait a few minutes between searches
- Don't scrape same ZIP repeatedly

---

## 💰 Cost

**$0/month** - Everything runs on Vercel's free tier:
- Unlimited deployments
- Serverless functions included
- No database = no database costs
- No authentication = no auth service costs

---

## 📊 Features & Limitations

### ✅ What It Does
- Search any ZIP code instantly
- Find agents with stale listings
- Calculate frustration scores
- View detailed listing information
- Export results to CSV
- Fast, simple, no signup required

### ❌ What It Doesn't Do
- Store search history (results disappear on refresh)
- Require authentication
- Save data to database
- Support multiple ZIP codes at once
- Automated/scheduled scraping
- Email notifications

**This is intentional!** It's a simple, focused tool that does one thing well.

---

## 🎯 Next Steps (Optional)

If you want to enhance later:

1. **Local Storage**: Save results in browser
2. **Multiple ZIP Codes**: Search multiple at once
3. **Email Results**: Send CSV via email
4. **Property Photos**: Show listing images
5. **Price Drop Tracking**: Add price reduction tracking
6. **Agent Notes**: Add notes about agents
7. **Print View**: Formatted for printing

---

## 📁 File Structure

```
AgentRadar/
├── src/
│   └── app/
│       ├── page.tsx              # Main page (only page)
│       ├── layout.tsx            # Root layout
│       └── globals.css           # Tailwind styles
├── api/
│   ├── scrape.py                 # Python scraping function
│   └── requirements.txt          # homeharvest, pandas
├── vercel.json                   # Python runtime config
├── package.json                  # NPM dependencies
├── tsconfig.json                 # TypeScript config
├── tailwind.config.ts            # Tailwind config
├── next.config.js                # Next.js config
├── .gitignore
├── README.md
├── DEPLOYMENT.md (this file)
└── DevelopmentPlan.md (original plan)
```

---

## ✨ You're Ready!

### Deployment Checklist
- [x] Next.js project created
- [x] Python scraping function built
- [x] UI components completed
- [x] Vercel configuration set
- [x] Git initialized
- [ ] Push to GitHub (you do this)
- [ ] Deploy on Vercel (you do this)

### Time to Deploy
**Estimated:** 5 minutes
1. Push to GitHub: 2 minutes
2. Deploy on Vercel: 3 minutes
3. **Done!**

---

## 🎉 What You Built

A production-ready, serverless web app that:
- Scrapes real estate data in real-time
- Analyzes agent frustration levels
- Provides actionable insights
- Exports data for outreach
- Costs $0 to run
- Took less than an hour to build

**Perfect for finding motivated agents to work with!**

---

*Built with Next.js 14, Python, HomeHarvest, and Vercel*
*No database. No authentication. Just results.*
