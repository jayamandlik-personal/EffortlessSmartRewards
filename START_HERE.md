# 🚀 START HERE - Effortless Smart Rewards

## Quick Start (2 Terminals Required)

### Terminal 1: Backend Server

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

✅ Backend running at: **http://localhost:8000**

### Terminal 2: Frontend Server

```bash
cd frontend
npm install
npm run dev
```

✅ Frontend running at: **http://localhost:3000**

## 🌐 Open in Browser

**Go to: http://localhost:3000**

## 📱 What You'll See

### Dashboard
- Account balance & transaction count
- 3 Savings KPI cards (Auto-Apply, Notifications, Total)
- Pie chart of rewards by category
- **AI Insights** (powered by OpenAI) - may take 10-20 seconds
- Recent rewards applied list

### Transactions
- Full transaction history table
- Shows merchant, category, amount, reward status
- Color-coded reward badges

### Rewards
- 7 available rewards in card grid
- Auto-Apply vs Opt-In badges
- Priceless experiences with locations

### Settings
- Configure geo-location for Priceless experiences
- Toggle notifications on/off
- Enable/disable auto-apply rewards

## 🧪 Test API Directly

```bash
# Health check
curl http://localhost:8000/health

# Get user
curl http://localhost:8000/users/1

# Get dashboard data
curl http://localhost:8000/users/1/dashboard-summary

# Get AI insights (requires OpenAI API key)
curl http://localhost:8000/users/1/ai-insights
```

## 📊 Sample Data

- **2 Users**: Sarah Johnson (SF), Michael Chen (NY)
- **63 Transactions**: Mix of dining, travel, groceries, shopping
- **7 Rewards**: 5 cashback + 2 Priceless experiences
- **Rewards Applied**: Many transactions already have rewards matched

## ⚙️ Configuration

- OpenAI API key: `backend/.env` (already configured)
- CSV data files: `backend/data/` (edit directly to add data)

## 🐛 Troubleshooting

**Backend not starting?**
- Check Python version: `python3 --version` (need 3.9+)
- Verify `.env` file exists: `ls backend/.env`
- Check virtual environment: `source backend/venv/bin/activate`

**Frontend not loading?**
- Check Node version: `node --version` (need 18+)
- Install dependencies: `cd frontend && npm install`
- Check backend is running on port 8000

**AI Insights not working?**
- Verify OpenAI API key in `backend/.env`
- Check backend logs for API errors
- May take 10-20 seconds to generate

## 📖 Full Documentation

See `TESTING_GUIDE.md` for complete testing instructions.

