from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime, timedelta
from decimal import Decimal

from app import schemas
from app.csv_loader import CSVDataLoader
from app.services import (
    TransactionEnrichmentService,
    RewardMatchingService,
    SavingsCalculationService
)
from app.ai_service import AiInsightsService

# Initialize CSV loader (using CSV files instead of database for POC)
csv_loader = CSVDataLoader(data_dir="data")

app = FastAPI(
    title="Effortless API",
    description="Smart Rewards Platform API (CSV-based POC)",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Effortless API (CSV-based)", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "data_source": "CSV"}


# User endpoints
@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int):
    user = csv_loader.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users/{user_id}/preferences", response_model=schemas.UserPreferenceResponse)
def get_user_preferences(user_id: int):
    user = csv_loader.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    preferences = csv_loader.get_user_preferences(user_id)
    
    if not preferences:
        # Create default preferences
        preferences = {
            "id": 0,
            "user_id": user_id,
            "notifications_enabled": True,
            "priceless_geo_location": user.get("primary_geo_location"),
            "priceless_notifications_enabled": True,
            "auto_apply_rewards_enabled": True,
            "created_at": datetime.now(),
            "updated_at": None
        }
    
    return preferences


@app.put("/users/{user_id}/preferences", response_model=schemas.UserPreferenceResponse)
def update_user_preferences(
    user_id: int,
    preferences_update: schemas.UserPreferenceUpdate
):
    user = csv_loader.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    preferences = csv_loader.get_user_preferences(user_id)
    
    if not preferences:
        preferences = {
            "id": 0,
            "user_id": user_id,
            "notifications_enabled": True,
            "priceless_geo_location": None,
            "priceless_notifications_enabled": True,
            "auto_apply_rewards_enabled": True,
            "created_at": datetime.now(),
            "updated_at": None
        }
    
    # Update preferences (in a real app, this would write back to CSV)
    for key, value in preferences_update.dict(exclude_unset=True).items():
        preferences[key] = value
    
    preferences["updated_at"] = datetime.now()
    
    return preferences


# Transaction endpoints
@app.get("/users/{user_id}/transactions", response_model=List[schemas.TransactionResponse])
def get_user_transactions(
    user_id: int,
    limit: int = 50,
    offset: int = 0
):
    user = csv_loader.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    transactions = csv_loader.get_transactions_by_user(user_id)
    # Sort by transaction_at descending
    transactions.sort(key=lambda x: x.get("transaction_at") or datetime.min, reverse=True)
    
    return transactions[offset:offset + limit]


# Rewards endpoints
@app.get("/rewards", response_model=List[schemas.RewardResponse])
def get_rewards(
    category: str = None,
    active_only: bool = True
):
    rewards = csv_loader.get_rewards(active_only=active_only, category=category)
    return rewards


# Dashboard summary endpoint
@app.get("/users/{user_id}/dashboard-summary", response_model=schemas.DashboardSummary)
def get_dashboard_summary(user_id: int):
    """
    Main dashboard endpoint that returns:
    - Account totals
    - Savings calculations (auto-apply and notifications)
    - Rewards by category for pie chart
    - Recent rewards applied/missed
    """
    user = csv_loader.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all transactions for user
    transactions = csv_loader.get_transactions_by_user(user_id)
    
    # Calculate total balance (sum of all transactions)
    total_balance = sum(
        Decimal(str(t.get("value_amount_usd", 0))) for t in transactions
    ) or Decimal("0.00")
    
    # Calculate savings
    cutoff_date = datetime.now() - timedelta(days=30)
    
    # Filter transactions from last 30 days
    recent_transactions = [
        t for t in transactions
        if t.get("transaction_at") and t.get("transaction_at") >= cutoff_date
    ]
    
    # Calculate saved_via_auto_apply
    auto_apply_transactions = [
        t for t in recent_transactions
        if t.get("reward_applied") and not t.get("notification_triggered")
        and t.get("reward_savings_amount")
    ]
    saved_via_auto_apply = sum(
        Decimal(str(t.get("reward_savings_amount", 0))) for t in auto_apply_transactions
    ) or Decimal("0.00")
    
    # Calculate saved_via_notifications
    notification_transactions = [
        t for t in recent_transactions
        if t.get("notification_triggered") and t.get("reward_savings_amount")
    ]
    saved_via_notifications = sum(
        Decimal(str(t.get("reward_savings_amount", 0))) for t in notification_transactions
    ) or Decimal("0.00")
    
    # Get rewards by category
    rewards_by_category_dict = {}
    for t in recent_transactions:
        if t.get("reward_applied") and t.get("reward_savings_amount"):
            category = t.get("category") or "Other"
            if category not in rewards_by_category_dict:
                rewards_by_category_dict[category] = {"total_savings": Decimal("0.00"), "count": 0}
            rewards_by_category_dict[category]["total_savings"] += Decimal(str(t.get("reward_savings_amount", 0)))
            rewards_by_category_dict[category]["count"] += 1
    
    rewards_by_category = [
        schemas.RewardsByCategory(
            category=cat,
            total_savings=data["total_savings"],
            count=data["count"]
        )
        for cat, data in rewards_by_category_dict.items()
    ]
    
    # Get recent rewards applied
    recent_rewards_applied = [
        t for t in recent_transactions
        if t.get("reward_applied")
    ]
    recent_rewards_applied.sort(key=lambda x: x.get("transaction_at") or datetime.min, reverse=True)
    recent_rewards_applied = recent_rewards_applied[:10]
    
    # Get recent rewards missed
    recent_rewards_missed = [
        t for t in recent_transactions
        if t.get("matched_reward_id") and not t.get("reward_applied")
    ]
    recent_rewards_missed.sort(key=lambda x: x.get("transaction_at") or datetime.min, reverse=True)
    recent_rewards_missed = recent_rewards_missed[:10]
    
    return schemas.DashboardSummary(
        total_balance=total_balance,
        total_transactions=len(transactions),
        saved_via_auto_apply=saved_via_auto_apply,
        saved_via_notifications=saved_via_notifications,
        rewards_by_category=rewards_by_category,
        recent_rewards_applied=recent_rewards_applied,
        recent_rewards_missed=recent_rewards_missed
    )


# AI Insights endpoint
@app.get("/users/{user_id}/ai-insights", response_model=schemas.AIInsightSummary)
def get_ai_insights(user_id: int):
    """
    Get AI-generated insights, summaries, and recommendations.
    Requires OPENAI_API_KEY to be set in environment.
    """
    user = csv_loader.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get recent transactions
    cutoff_date = datetime.now() - timedelta(days=30)
    transactions = csv_loader.get_transactions_by_user(user_id)
    recent_transactions = [
        t for t in transactions
        if t.get("transaction_at") and t.get("transaction_at") >= cutoff_date
    ]
    
    # Get rewards applied and missed
    rewards_applied = [
        t for t in recent_transactions if t.get("reward_applied")
    ]
    rewards_missed = [
        t for t in recent_transactions
        if t.get("matched_reward_id") and not t.get("reward_applied")
    ]
    
    # Calculate savings
    auto_apply_transactions = [
        t for t in recent_transactions
        if t.get("reward_applied") and not t.get("notification_triggered")
        and t.get("reward_savings_amount")
    ]
    saved_auto_apply = sum(
        Decimal(str(t.get("reward_savings_amount", 0))) for t in auto_apply_transactions
    ) or Decimal("0.00")
    
    notification_transactions = [
        t for t in recent_transactions
        if t.get("notification_triggered") and t.get("reward_savings_amount")
    ]
    saved_notifications = sum(
        Decimal(str(t.get("reward_savings_amount", 0))) for t in notification_transactions
    ) or Decimal("0.00")
    
    # Get rewards by category
    rewards_by_category_dict = {}
    for t in recent_transactions:
        if t.get("reward_applied") and t.get("reward_savings_amount"):
            category = t.get("category") or "Other"
            if category not in rewards_by_category_dict:
                rewards_by_category_dict[category] = {"total_savings": Decimal("0.00"), "count": 0}
            rewards_by_category_dict[category]["total_savings"] += Decimal(str(t.get("reward_savings_amount", 0)))
            rewards_by_category_dict[category]["count"] += 1
    
    rewards_by_category = [
        {
            "category": cat,
            "total_savings": data["total_savings"],
            "count": data["count"]
        }
        for cat, data in rewards_by_category_dict.items()
    ]
    
    # Get available rewards for recommendations
    available_rewards = csv_loader.get_rewards(active_only=True)
    
    # Get user preferences
    preferences = csv_loader.get_user_preferences(user_id)
    preferences_dict = {}
    if preferences:
        preferences_dict = {
            "priceless_geo_location": preferences.get("priceless_geo_location"),
            "priceless_notifications_enabled": preferences.get("priceless_notifications_enabled", True),
            "auto_apply_rewards_enabled": preferences.get("auto_apply_rewards_enabled", True)
        }
    
    # Convert transactions to Transaction objects for AI service
    # For simplicity, we'll pass dicts and let the AI service handle them
    try:
        ai_service = AiInsightsService()
        
        # Create a simple user-like object
        class SimpleUser:
            def __init__(self, user_dict):
                self.name = user_dict.get("name", "")
                self.primary_geo_location = user_dict.get("primary_geo_location")
        
        simple_user = SimpleUser(user)
        
        # Generate summary
        summary = ai_service.generate_dashboard_summary(
            user=simple_user,
            transactions=recent_transactions,
            rewards_applied=rewards_applied,
            rewards_missed=rewards_missed,
            saved_auto_apply=saved_auto_apply,
            saved_notifications=saved_notifications,
            rewards_by_category=rewards_by_category
        )
        
        # Generate recommendations
        recommendations = ai_service.generate_reward_recommendations(
            user=simple_user,
            recent_transactions=recent_transactions[:50],
            available_rewards=available_rewards,
            user_preferences=preferences_dict
        )
        
        # Convert Reward dicts to RewardResponse schemas
        summary.recommended_auto_apply_rewards = [
            schemas.RewardResponse.model_validate(r) for r in recommendations.get("recommended_auto_apply", [])
        ]
        summary.recommended_priceless_experiences = [
            schemas.RewardResponse.model_validate(r) for r in recommendations.get("recommended_priceless", [])
        ]
        
        return summary
    except Exception as e:
        # Fallback if AI service fails
        return schemas.AIInsightSummary(
            summary_text=f"Unable to generate AI insights: {str(e)}",
            top_insights=[],
            recommended_auto_apply_rewards=[],
            recommended_priceless_experiences=[]
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
