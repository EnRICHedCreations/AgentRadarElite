# AgentRadar - Simple

Find frustrated real estate agents with stale listings in any ZIP code.

## What It Does

1. Enter a ZIP code
2. Scrapes listings using HomeHarvest
3. Identifies agents with stale listings (90+ days on market)
4. Calculates "frustration score" for each agent
5. Displays results in a sortable interface
6. Export to CSV

## Tech Stack

- **Frontend**: Next.js 14 with TypeScript & Tailwind CSS
- **Scraping**: Python serverless function with HomeHarvest
- **Deployment**: Vercel (free tier)
- **Database**: None (results stored in browser session only)

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### 3. Deploy to Vercel

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit"

# Push to GitHub
git remote add origin https://github.com/yourusername/agentradar-simple.git
git branch -M main
git push -u origin main

# Deploy on Vercel
# 1. Go to vercel.com
# 2. Import your GitHub repository
# 3. Vercel auto-detects Next.js
# 4. Click Deploy
```

## How to Use

1. Open the app
2. Enter a 5-digit ZIP code
3. Click "Find Agents"
4. Wait 30-60 seconds while it scrapes
5. View results sorted by frustration score
6. Click "View Listings" to see details
7. Click "Export to CSV" to download data

## Frustration Score

0-100 scale based on:
- **Listing Score** (0-50 points): 10 points per stale listing
- **Days on Market Score** (0-50 points): 0.25 points per average day

### Color Coding
- 🔴 80-100: Very frustrated (red)
- 🟠 60-79: Frustrated (orange)
- 🟡 40-59: Somewhat frustrated (yellow)
- 🟢 0-39: Mildly frustrated (green)

## Project Structure

```
agentradar-simple/
├── src/
│   └── app/
│       ├── page.tsx              # Main page (only page)
│       ├── layout.tsx            # Root layout
│       └── globals.css           # Tailwind styles
├── api/
│   ├── scrape.py                 # Python scraping function
│   └── requirements.txt          # Python dependencies
├── vercel.json                   # Vercel config for Python
├── package.json
└── README.md
```

## Cost

**Free!** Everything runs on Vercel's free tier.

## Limitations

- No data persistence (results disappear on refresh)
- No authentication
- No search history
- One ZIP code at a time
- No scheduling

Perfect for quick manual searches!
