# Testing Guide - Effortless Smart Rewards

Complete guide to run and test the application.

## Prerequisites Check

✅ Python 3.9+ installed
✅ Node.js 18+ installed  
✅ OpenAI API key configured in `backend/.env`

## Step-by-Step Setup & Testing

### 1. Backend Setup (Terminal 1)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Verify .env file exists with OpenAI API key
cat .env | grep OPENAI_API_KEY

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Backend will be available at:** `http://localhost:8000`

### 2. Frontend Setup (Terminal 2)

```bash
# Navigate to frontend directory (in a NEW terminal)
cd frontend

# Install dependencies (first time only)
npm install

# Start the frontend development server
npm run dev
```

**Expected Output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

**Frontend will be available at:** `http://localhost:3000`

### 3. Access the Application

Open your browser and navigate to: **http://localhost:3000**

## What You'll See in the UI

### 🏠 Dashboard Page (`/dashboard`)

**Features:**
- **Account Summary Card**: Total balance and transaction count
- **Savings KPIs** (3 cards):
  - Saved via Auto-Apply (green gradient)
  - Saved via Priceless Notifications (purple gradient)
  - Total Savings (blue gradient)
- **Rewards by Category Pie Chart**: Visual breakdown of savings by category
- **AI Insights Section**:
  - Natural language summary of spending and savings
  - Top 2-3 insights
  - Recommended auto-apply rewards
  - Recommended Priceless experiences
- **Recent Rewards Applied**: List of transactions with rewards applied

**Sample Data:**
- User ID 1: Sarah Johnson (San Francisco)
- User ID 2: Michael Chen (New York)
- 63 transactions across both users
- 7 rewards (Starbucks, Uber, Whole Foods, Amazon, Coffee Shops, + 2 Priceless experiences)

### 💳 Transactions Page (`/transactions`)

**Features:**
- Table view of all transactions
- Columns:
  - Date
  - Description & Memo
  - Merchant (normalized)
  - Category badge
  - Amount (negative for expenses, positive for income)
  - Reward Applied status (Yes/Missed/-)
  - Savings amount (if reward applied)
- Color coding:
  - Green badges for applied rewards
  - Red badges for missed opportunities

### 🎁 Rewards Page (`/rewards`)

**Features:**
- Grid of reward cards showing:
  - Reward type icon and color
  - Auto-Apply or Opt-In Required badge
  - Reward label and description
  - Category, merchant, cashback percentage
  - Terms and conditions
  - Valid date range
  - Geo-location (for Priceless experiences)

**Available Rewards:**
1. 5% Cashback at Starbucks (Auto-Apply)
2. 10% Cashback on Uber Rides (Auto-Apply)
3. 3% Cashback at Whole Foods (Auto-Apply)
4. 2% Cashback on Amazon (Auto-Apply)
5. 4% Cashback at Coffee Shops (Auto-Apply)
6. Priceless: Wine Tasting Experience (San Francisco - Opt-In)
7. Priceless: Broadway Show Access (New York - Opt-In)

### ⚙️ Settings Page (`/settings`)

**Features:**
- **Priceless Experiences Section**:
  - Geo-Location input (e.g., "San Francisco, CA")
- **Notifications Section**:
  - Enable Notifications toggle
  - Priceless Experience Notifications toggle
  - Auto-Apply Rewards Activity Summary toggle
- **Rewards Section**:
  - Auto-Apply Rewards toggle
- **Save Preferences** button

## Testing the AI Agent

### Test AI Insights Endpoint

```bash
# Test the AI insights endpoint directly
curl http://localhost:8000/users/1/ai-insights | python -m json.tool
```

**Expected Response:**
```json
{
  "summary_text": "This month, you've saved $X.XX through Effortless rewards...",
  "top_insights": [
    "Your top spending category is dining",
    "You've saved $X.XX through automatic rewards",
    "Consider enabling more auto-apply rewards..."
  ],
  "recommended_auto_apply_rewards": [...],
  "recommended_priceless_experiences": [...]
}
```

### Test Dashboard Summary

```bash
# Test dashboard data
curl http://localhost:8000/users/1/dashboard-summary | python -m json.tool
```

**Expected Response:**
```json
{
  "total_balance": 3500.00,
  "total_transactions": 31,
  "saved_via_auto_apply": 15.23,
  "saved_via_notifications": 0.00,
  "rewards_by_category": [
    {"category": "dining", "total_savings": 8.50, "count": 12},
    {"category": "travel", "total_savings": 4.20, "count": 5},
    ...
  ],
  "recent_rewards_applied": [...],
  "recent_rewards_missed": [...]
}
```

## API Endpoints to Test

### Health Check
```bash
curl http://localhost:8000/health
# Response: {"status":"healthy","data_source":"CSV"}
```

### Get User
```bash
curl http://localhost:8000/users/1
```

### Get User Transactions
```bash
curl http://localhost:8000/users/1/transactions?limit=10
```

### Get Rewards
```bash
curl http://localhost:8000/rewards?active_only=true
```

### Get User Preferences
```bash
curl http://localhost:8000/users/1/preferences
```

### Update Preferences
```bash
curl -X PUT http://localhost:8000/users/1/preferences \
  -H "Content-Type: application/json" \
  -d '{"priceless_geo_location": "Los Angeles, CA", "notifications_enabled": true}'
```

## UI Testing Checklist

### ✅ Dashboard Tests
- [ ] Account balance displays correctly
- [ ] Savings KPIs show calculated values
- [ ] Pie chart renders with category data
- [ ] AI insights section loads (may take a few seconds)
- [ ] Recent rewards applied list shows transactions

### ✅ Transactions Tests
- [ ] Transaction table loads all transactions
- [ ] Merchant names are normalized
- [ ] Categories are displayed with badges
- [ ] Reward applied status shows correctly
- [ ] Savings amounts display for rewarded transactions

### ✅ Rewards Tests
- [ ] All 7 rewards display in grid
- [ ] Auto-Apply badges show correctly
- [ ] Priceless experiences show location
- [ ] Reward details (terms, dates) display

### ✅ Settings Tests
- [ ] Current preferences load
- [ ] Toggle switches work
- [ ] Geo-location input accepts text
- [ ] Save button updates preferences (in-memory)

## Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'app'`
**Solution:** Make sure you're in the `backend` directory and virtual environment is activated

**Problem:** `OPENAI_API_KEY not found`
**Solution:** Check that `backend/.env` exists and contains `OPENAI_API_KEY=your_key_here`

**Problem:** `FileNotFoundError: data/users.csv`
**Solution:** Verify `backend/data/` directory exists with all CSV files

### Frontend Issues

**Problem:** `Cannot GET /`
**Solution:** Make sure frontend dev server is running on port 3000

**Problem:** API calls failing with CORS errors
**Solution:** Backend CORS is configured for `localhost:3000` - ensure frontend runs on that port

**Problem:** Blank page or errors
**Solution:** Check browser console (F12) for errors, verify backend is running on port 8000

### AI Agent Issues

**Problem:** AI insights show error message
**Solution:** 
- Verify OpenAI API key is valid in `.env`
- Check backend logs for OpenAI API errors
- API may have rate limits - wait a moment and retry

**Problem:** AI insights are generic/fallback
**Solution:** OpenAI API may be unavailable - check API key and network connection

## Quick Test Script

Save this as `test_app.sh`:

```bash
#!/bin/bash

echo "🧪 Testing Effortless App..."

# Test backend health
echo "1. Testing backend health..."
curl -s http://localhost:8000/health | grep -q "healthy" && echo "   ✅ Backend is healthy" || echo "   ❌ Backend not responding"

# Test user endpoint
echo "2. Testing user endpoint..."
curl -s http://localhost:8000/users/1 | grep -q "name" && echo "   ✅ User data loaded" || echo "   ❌ User endpoint failed"

# Test transactions
echo "3. Testing transactions..."
TRANS_COUNT=$(curl -s http://localhost:8000/users/1/transactions | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)
echo "   ✅ Found $TRANS_COUNT transactions"

# Test rewards
echo "4. Testing rewards..."
REWARDS_COUNT=$(curl -s http://localhost:8000/rewards | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)
echo "   ✅ Found $REWARDS_COUNT rewards"

# Test dashboard
echo "5. Testing dashboard..."
curl -s http://localhost:8000/users/1/dashboard-summary | grep -q "total_balance" && echo "   ✅ Dashboard data loaded" || echo "   ❌ Dashboard failed"

# Test AI insights (may take longer)
echo "6. Testing AI insights (this may take 10-20 seconds)..."
curl -s http://localhost:8000/users/1/ai-insights | grep -q "summary_text" && echo "   ✅ AI insights generated" || echo "   ⚠️  AI insights may have failed (check API key)"

echo ""
echo "🎉 Testing complete! Open http://localhost:3000 in your browser"
```

Run with: `chmod +x test_app.sh && ./test_app.sh`

## Next Steps

1. **Start Backend**: Follow Step 1 above
2. **Start Frontend**: Follow Step 2 above  
3. **Open Browser**: Navigate to http://localhost:3000
4. **Explore**: Click through Dashboard, Transactions, Rewards, and Settings
5. **Test AI**: Check the AI Insights section on the Dashboard (may take 10-20 seconds to load)

## Data Files Location

All CSV data is in: `backend/data/`
- `users.csv` - User profiles
- `user_preferences.csv` - User settings
- `transactions.csv` - Transaction history (63 transactions)
- `rewards.csv` - Available rewards (7 rewards)

You can edit these CSV files directly to add/modify data!

