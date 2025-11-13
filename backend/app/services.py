"""
Business Logic Services

Handles:
1. Transaction enrichment (merchant normalization, category inference)
2. Reward matching logic
3. Savings calculations
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional
from app.models import Transaction, Reward, User, UserPreference


class TransactionEnrichmentService:
    """
    Enriches transaction data by normalizing merchant names and inferring categories.
    This is where Open Finance transaction data would be processed and enriched.
    """
    
    # Merchant name normalization patterns
    MERCHANT_PATTERNS = {
        "starbucks": "Starbucks",
        "sbux": "Starbucks",
        "coffee": "Coffee Shop",
        "mcdonald": "McDonald's",
        "mcd": "McDonald's",
        "uber": "Uber",
        "lyft": "Lyft",
        "amazon": "Amazon",
        "whole foods": "Whole Foods",
        "target": "Target",
        "walmart": "Walmart",
        "restaurant": "Restaurant",
        "dining": "Restaurant",
        "hotel": "Hotel",
        "airline": "Airline",
        "gas": "Gas Station",
        "shell": "Shell",
        "exxon": "Exxon",
        "grocery": "Grocery Store",
    }
    
    # Category inference patterns
    CATEGORY_PATTERNS = {
        "dining": ["restaurant", "cafe", "coffee", "starbucks", "mcdonald", "dining", "food", "pizza", "burger"],
        "travel": ["hotel", "airline", "uber", "lyft", "taxi", "airport", "travel", "booking"],
        "groceries": ["grocery", "whole foods", "safeway", "kroger", "walmart", "target", "supermarket"],
        "entertainment": ["movie", "theater", "cinema", "netflix", "spotify", "entertainment", "concert"],
        "shopping": ["amazon", "retail", "store", "shopping", "mall"],
        "gas": ["gas", "shell", "exxon", "chevron", "bp", "fuel"],
        "utilities": ["electric", "water", "gas bill", "utility", "internet", "phone"],
    }
    
    @staticmethod
    def normalize_merchant(description: str, memo: str = None) -> Optional[str]:
        """
        Normalize merchant name from description and memo fields.
        This is where data science would concatenate and process Description + Memo.
        """
        combined = f"{description} {memo or ''}".lower()
        
        for pattern, normalized in TransactionEnrichmentService.MERCHANT_PATTERNS.items():
            if pattern in combined:
                return normalized
        
        # Fallback: extract first meaningful word
        words = combined.split()
        if words:
            return words[0].capitalize()
        
        return None
    
    @staticmethod
    def infer_category(description: str, memo: str = None, merchant: str = None) -> Optional[str]:
        """
        Infer high-level category from transaction description, memo, and merchant.
        """
        combined = f"{description} {memo or ''} {merchant or ''}".lower()
        
        for category, patterns in TransactionEnrichmentService.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if pattern in combined:
                    return category
        
        return None
    
    @staticmethod
    def infer_location(description: str, memo: str = None) -> Optional[str]:
        """
        Optionally infer approximate geo-location from description/memo.
        This is a simplified version - real implementation would use geocoding APIs.
        """
        combined = f"{description} {memo or ''}".lower()
        
        # Simple city detection (would be enhanced with proper geocoding)
        cities = ["new york", "nyc", "san francisco", "sf", "los angeles", "la", "chicago", "boston", "miami"]
        for city in cities:
            if city in combined:
                return city.title()
        
        return None
    
    @staticmethod
    def enrich_transaction(transaction: Transaction) -> Transaction:
        """
        Enrich a transaction with normalized merchant, category, and location.
        """
        if not transaction.merchant_normalized:
            transaction.merchant_normalized = TransactionEnrichmentService.normalize_merchant(
                transaction.description, transaction.memo
            )
        
        if not transaction.category:
            transaction.category = TransactionEnrichmentService.infer_category(
                transaction.description, transaction.memo, transaction.merchant_normalized
            )
        
        if not transaction.location_inferred:
            transaction.location_inferred = TransactionEnrichmentService.infer_location(
                transaction.description, transaction.memo
            )
        
        return transaction


class RewardMatchingService:
    """
    Matches transactions to available rewards based on merchant, category, time, and geo-scope.
    """
    
    @staticmethod
    def find_matching_rewards(
        transaction: Transaction,
        user: User,
        user_preferences: Optional[UserPreference],
        db: Session
    ) -> List[Reward]:
        """
        Find rewards that match a transaction based on:
        - Merchant match and/or category
        - Time validity (start_date <= transaction_date <= end_date)
        - Geo-scope vs user's geo-location or Priceless geo-preference
        """
        # Ensure transaction is enriched
        transaction = TransactionEnrichmentService.enrich_transaction(transaction)
        
        # Build query for matching rewards
        query = db.query(Reward).filter(
            Reward.start_date <= transaction.transaction_at
        )
        
        # End date filter
        if transaction.transaction_at:
            query = query.filter(
                or_(
                    Reward.end_date.is_(None),
                    Reward.end_date >= transaction.transaction_at
                )
            )
        
        # Merchant or category match
        merchant_match = False
        if transaction.merchant_normalized:
            merchant_match = Reward.merchant_name.ilike(f"%{transaction.merchant_normalized}%")
        
        category_match = False
        if transaction.category:
            category_match = Reward.category == transaction.category
        
        if merchant_match or category_match:
            query = query.filter(or_(merchant_match, category_match))
        else:
            return []  # No matches if neither merchant nor category match
        
        # Geo-scope filtering
        user_geo = None
        if user_preferences and user_preferences.priceless_geo_location:
            user_geo = user_preferences.priceless_geo_location
        elif user.primary_geo_location:
            user_geo = user.primary_geo_location
        
        if user_geo:
            query = query.filter(
                or_(
                    Reward.geo_scope == "global",
                    Reward.geo_city.ilike(f"%{user_geo}%"),
                    Reward.geo_country.ilike(f"%{user_geo}%")
                )
            )
        
        matching_rewards = query.all()
        
        # Filter by auto-applicability if user has it enabled
        if user_preferences and user_preferences.auto_apply_rewards_enabled:
            auto_applicable = [r for r in matching_rewards if r.is_auto_applicable and not r.requires_user_opt_in]
            if auto_applicable:
                return auto_applicable[:1]  # Return best match (could be enhanced with ranking)
        
        return matching_rewards
    
    @staticmethod
    def calculate_reward_savings(transaction: Transaction, reward: Reward) -> Decimal:
        """
        Calculate savings amount for a transaction based on reward type.
        """
        transaction_amount = abs(transaction.value_amount_usd)
        
        if reward.reward_type == "percentage_cashback" and reward.percentage_value:
            savings = transaction_amount * (reward.percentage_value / 100)
            if reward.max_savings_amount:
                savings = min(savings, reward.max_savings_amount)
            return Decimal(str(savings))
        
        elif reward.reward_type == "fixed_amount" and reward.fixed_amount_value:
            return reward.fixed_amount_value
        
        return Decimal("0.00")


class SavingsCalculationService:
    """
    Calculates total savings from auto-apply and notifications.
    """
    
    @staticmethod
    def calculate_savings(
        user_id: int,
        db: Session,
        days: int = 30
    ) -> Dict[str, Decimal]:
        """
        Calculate saved_via_auto_apply and saved_via_notifications for a user.
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Transactions with auto-applied rewards
        auto_apply_transactions = db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.reward_applied == True,
                Transaction.notification_triggered == False,
                Transaction.reward_savings_amount.isnot(None),
                Transaction.transaction_at >= cutoff_date
            )
        ).all()
        
        saved_via_auto_apply = sum(
            t.reward_savings_amount for t in auto_apply_transactions
            if t.reward_savings_amount
        ) or Decimal("0.00")
        
        # Transactions where notification triggered user action
        notification_transactions = db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.notification_triggered == True,
                Transaction.reward_savings_amount.isnot(None),
                Transaction.transaction_at >= cutoff_date
            )
        ).all()
        
        saved_via_notifications = sum(
            t.reward_savings_amount for t in notification_transactions
            if t.reward_savings_amount
        ) or Decimal("0.00")
        
        return {
            "saved_via_auto_apply": saved_via_auto_apply,
            "saved_via_notifications": saved_via_notifications
        }
    
    @staticmethod
    def get_rewards_by_category(
        user_id: int,
        db: Session,
        days: int = 30
    ) -> List[Dict]:
        """
        Get aggregated rewards savings by category for pie chart.
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        transactions = db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.reward_applied == True,
                Transaction.reward_savings_amount.isnot(None),
                Transaction.transaction_at >= cutoff_date
            )
        ).all()
        
        category_totals = {}
        for t in transactions:
            category = t.category or "Other"
            if category not in category_totals:
                category_totals[category] = {"total_savings": Decimal("0.00"), "count": 0}
            
            category_totals[category]["total_savings"] += t.reward_savings_amount or Decimal("0.00")
            category_totals[category]["count"] += 1
        
        return [
            {
                "category": cat,
                "total_savings": data["total_savings"],
                "count": data["count"]
            }
            for cat, data in category_totals.items()
        ]

