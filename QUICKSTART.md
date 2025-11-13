# Quick Start Guide

Get Effortless up and running in 5 minutes!

## Prerequisites

- Python 3.9+
- Node.js 18+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Step 1: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Initialize database with sample data
python seed_data.py

# Start backend server
uvicorn app.main:app --reload
```

Backend will run at `http://localhost:8000`

## Step 2: Frontend Setup

In a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run at `http://localhost:3000`

## Step 3: Access the Application

1. Open `http://localhost:3000` in your browser
2. The app uses mock authentication (user ID 1)
3. Explore:
   - **Dashboard**: View account summary, savings, and AI insights
   - **Transactions**: Browse transaction history
   - **Rewards**: See available rewards and Priceless experiences
   - **Settings**: Configure preferences and notifications

## Sample Data

The seed script creates:
- 2 users (Sarah Johnson, Michael Chen)
- 7 rewards (cashback and experiences)
- 60-90 transactions per user

## API Documentation

Once the backend is running:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Troubleshooting

### OpenAI API Key Error
- Make sure `OPENAI_API_KEY` is set in `backend/.env`
- The AI features will show fallback messages if the API key is missing

### Database Issues
- Delete `backend/effortless.db` and run `python seed_data.py` again

### Port Already in Use
- Backend: Change port in `uvicorn app.main:app --reload --port 8001`
- Frontend: Update `vite.config.js` port and proxy target

## Next Steps

- Replace mock authentication with real auth
- Connect to real Open Finance transaction feed
- Customize merchant normalization patterns
- Add more reward categories and experiences

