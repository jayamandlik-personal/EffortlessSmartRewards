"""
Seed Data Script

Creates sample data for:
- Users and preferences
- Transactions (using the Transaction History schema)
- Rewards/merchant offers

Run with: python seed_data.py
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal
import random

from app.database import SessionLocal, engine
from app import models
from app.services import TransactionEnrichmentService, RewardMatchingService

# Create tables
models.Base.metadata.create_all(bind=engine)


def create_sample_users(db: Session):
    """Create sample users with preferences"""
    users_data = [
        {
            "customer_id": 1001,
            "name": "Sarah Johnson",
            "email": "sarah.johnson@example.com",
            "primary_geo_location": "San Francisco, CA"
        },
        {
            "customer_id": 1002,
            "name": "Michael Chen",
            "email": "michael.chen@example.com",
            "primary_geo_location": "New York, NY"
        }
    ]
    
    users = []
    for user_data in users_data:
        user = db.query(models.User).filter(
            models.User.customer_id == user_data["customer_id"]
        ).first()
        
        if not user:
            user = models.User(**user_data)
            db.add(user)
            db.flush()
            
            # Create default preferences
            preferences = models.UserPreference(
                user_id=user.id,
                notifications_enabled=True,
                priceless_geo_location=user_data["primary_geo_location"],
                priceless_notifications_enabled=True,
                auto_apply_rewards_enabled=True
            )
            db.add(preferences)
            users.append(user)
        else:
            users.append(user)
    
    db.commit()
    return users


def create_sample_rewards(db: Session):
    """Create sample rewards/merchant offers"""
    now = datetime.now()
    
    rewards_data = [
        {
            "merchant_name": "Starbucks",
            "reward_type": "percentage_cashback",
            "reward_label": "5% Cashback at Starbucks",
            "reward_description": "Get 5% cashback on all Starbucks purchases",
            "category": "dining",
            "terms": "Valid at all Starbucks locations. Max $50 savings per month.",
            "start_date": now - timedelta(days=30),
            "end_date": now + timedelta(days=60),
            "max_savings_amount": Decimal("50.00"),
            "geo_scope": "global",
            "is_auto_applicable": True,
            "requires_user_opt_in": False,
            "percentage_value": Decimal("5.00")
        },
        {
            "merchant_name": "Uber",
            "reward_type": "percentage_cashback",
            "reward_label": "10% Cashback on Rides",
            "reward_description": "10% cashback on all Uber rides",
            "category": "travel",
            "terms": "Valid for all Uber rides. No maximum.",
            "start_date": now - timedelta(days=15),
            "end_date": now + timedelta(days=45),
            "geo_scope": "global",
            "is_auto_applicable": True,
            "requires_user_opt_in": False,
            "percentage_value": Decimal("10.00")
        },
        {
            "merchant_name": "Whole Foods",
            "reward_type": "percentage_cashback",
            "reward_label": "3% Cashback at Whole Foods",
            "reward_description": "3% cashback on grocery purchases",
            "category": "groceries",
            "terms": "Valid at Whole Foods Market locations.",
            "start_date": now - timedelta(days=20),
            "end_date": now + timedelta(days=40),
            "geo_scope": "global",
            "is_auto_applicable": True,
            "requires_user_opt_in": False,
            "percentage_value": Decimal("3.00")
        },
        {
            "merchant_name": "Amazon",
            "reward_type": "percentage_cashback",
            "reward_label": "2% Cashback on Amazon",
            "reward_description": "2% cashback on all Amazon purchases",
            "category": "shopping",
            "terms": "Valid on all Amazon.com purchases.",
            "start_date": now - timedelta(days=10),
            "end_date": now + timedelta(days=50),
            "geo_scope": "global",
            "is_auto_applicable": True,
            "requires_user_opt_in": False,
            "percentage_value": Decimal("2.00")
        },
        {
            "merchant_name": "Exclusive Wine Tasting",
            "reward_type": "experience",
            "reward_label": "Priceless: Wine Tasting Experience",
            "reward_description": "Exclusive wine tasting at Napa Valley winery",
            "category": "entertainment",
            "terms": "Reservation required. Valid for cardholders in San Francisco area.",
            "start_date": now - timedelta(days=5),
            "end_date": now + timedelta(days=30),
            "geo_scope": "city",
            "geo_city": "San Francisco",
            "is_auto_applicable": False,
            "requires_user_opt_in": True,
            "fixed_amount_value": Decimal("150.00")  # Value of experience
        },
        {
            "merchant_name": "Broadway Show Tickets",
            "reward_type": "experience",
            "reward_label": "Priceless: Broadway Show Access",
            "reward_description": "VIP access to select Broadway shows",
            "category": "entertainment",
            "terms": "Subject to availability. New York area only.",
            "start_date": now - timedelta(days=3),
            "end_date": now + timedelta(days=20),
            "geo_scope": "city",
            "geo_city": "New York",
            "is_auto_applicable": False,
            "requires_user_opt_in": True,
            "fixed_amount_value": Decimal("200.00")
        },
        {
            "merchant_name": "Coffee Shop",
            "reward_type": "percentage_cashback",
            "reward_label": "4% Cashback at Coffee Shops",
            "reward_description": "4% cashback at participating coffee shops",
            "category": "dining",
            "terms": "Valid at independent coffee shops.",
            "start_date": now - timedelta(days=25),
            "end_date": now + timedelta(days=35),
            "geo_scope": "global",
            "is_auto_applicable": True,
            "requires_user_opt_in": False,
            "percentage_value": Decimal("4.00")
        }
    ]
    
    rewards = []
    for reward_data in rewards_data:
        reward = db.query(models.Reward).filter(
            models.Reward.reward_label == reward_data["reward_label"]
        ).first()
        
        if not reward:
            reward = models.Reward(**reward_data)
            db.add(reward)
            rewards.append(reward)
        else:
            rewards.append(reward)
    
    db.commit()
    return rewards


def create_sample_transactions(db: Session, users: list):
    """
    Create sample transactions using the Transaction History schema.
    
    Date Time Fields: Posted (by FI) and Transaction date/time fields available.
    Customer ID: A number generated by MA Open Banking that uniquely identifies a customer.
    Account ID: A number generated by MA Open Banking that uniquely identifies a customer's account: checking, savings, etc.
    Description + Memo: Two free text fields, often concatenated by data science, that offer information on merchant, payment processor, geographic location, and transaction type (P2P, P2M, Income, etc).
    Value Amount: In USD.
    """
    now = datetime.now()
    transactions_data = []
    
    # Sample transaction descriptions
    transaction_templates = [
        # Dining
        ("STARBUCKS STORE #12345", "Purchase at Starbucks Coffee", "dining", -5.50),
        ("SBUX #67890", "Coffee purchase", "dining", -4.75),
        ("MCDONALDS #111", "Fast food purchase", "dining", -12.30),
        ("RESTAURANT XYZ", "Dinner payment", "dining", -45.00),
        ("COFFEE SHOP SF", "Morning coffee", "dining", -6.25),
        
        # Travel
        ("UBER TRIP", "Ride share payment", "travel", -18.50),
        ("UBER *RIDE", "Uber ride to airport", "travel", -32.00),
        ("LYFT RIDE", "Lyft transportation", "travel", -15.75),
        ("HOTEL BOOKING", "Hotel reservation", "travel", -150.00),
        ("AIRLINE TICKET", "Flight booking", "travel", -350.00),
        
        # Groceries
        ("WHOLE FOODS MARKET", "Grocery purchase", "groceries", -85.50),
        ("WHOLE FOODS #SF", "Weekly groceries", "groceries", -120.00),
        ("TARGET STORE", "Shopping at Target", "groceries", -65.25),
        ("WALMART SUPER", "Grocery shopping", "groceries", -95.00),
        
        # Shopping
        ("AMAZON.COM", "Online purchase", "shopping", -29.99),
        ("AMAZON MARKETPLACE", "Amazon order", "shopping", -45.50),
        ("AMAZON PRIME", "Prime subscription", "shopping", -14.99),
        
        # Entertainment
        ("NETFLIX", "Streaming subscription", "entertainment", -15.99),
        ("SPOTIFY PREMIUM", "Music subscription", "entertainment", -9.99),
        ("MOVIE THEATER", "Cinema tickets", "entertainment", -24.00),
        
        # Income
        ("PAYROLL DEPOSIT", "Salary payment", "income", 3500.00),
        ("DIRECT DEPOSIT", "Monthly salary", "income", 3500.00),
    ]
    
    for user in users:
        account_id = 2000 + user.id  # Generate account ID
        
        # Create transactions over last 30 days
        for day_offset in range(30):
            transaction_date = now - timedelta(days=day_offset)
            
            # 1-3 transactions per day
            num_transactions = random.randint(1, 3)
            
            for _ in range(num_transactions):
                description, memo, category, base_amount = random.choice(transaction_templates)
                
                # Vary amounts slightly
                amount = Decimal(str(base_amount * random.uniform(0.8, 1.2)))
                
                # Posted date is usually same day or next day
                posted_date = transaction_date + timedelta(hours=random.randint(0, 24))
                
                transaction = models.Transaction(
                    customer_id=user.customer_id,
                    account_id=account_id,
                    posted_at=posted_date,
                    transaction_at=transaction_date,
                    description=description,
                    memo=memo,
                    value_amount_usd=amount,
                    user_id=user.id
                )
                
                # Enrich transaction
                transaction = TransactionEnrichmentService.enrich_transaction(transaction)
                
                # Try to match rewards
                preferences = db.query(models.UserPreference).filter(
                    models.UserPreference.user_id == user.id
                ).first()
                
                matching_rewards = RewardMatchingService.find_matching_rewards(
                    transaction, user, preferences, db
                )
                
                if matching_rewards:
                    reward = matching_rewards[0]
                    transaction.matched_reward_id = reward.id
                    
                    # Calculate savings
                    savings = RewardMatchingService.calculate_reward_savings(transaction, reward)
                    transaction.reward_savings_amount = savings
                    
                    # Auto-apply if enabled and applicable
                    if preferences and preferences.auto_apply_rewards_enabled:
                        if reward.is_auto_applicable and not reward.requires_user_opt_in:
                            transaction.reward_applied = True
                        elif random.random() < 0.3:  # 30% chance user acted on notification
                            transaction.notification_triggered = True
                            transaction.reward_applied = True
                
                db.add(transaction)
                transactions_data.append(transaction)
    
    db.commit()
    print(f"Created {len(transactions_data)} transactions")
    return transactions_data


def main():
    """Main seed function"""
    db = SessionLocal()
    
    try:
        print("Creating sample users...")
        users = create_sample_users(db)
        print(f"Created {len(users)} users")
        
        print("Creating sample rewards...")
        rewards = create_sample_rewards(db)
        print(f"Created {len(rewards)} rewards")
        
        print("Creating sample transactions...")
        transactions = create_sample_transactions(db, users)
        print(f"Created {len(transactions)} transactions")
        
        print("\nSeed data created successfully!")
        print(f"\nSample users:")
        for user in users:
            print(f"  - {user.name} (ID: {user.id}, Email: {user.email})")
        
    except Exception as e:
        print(f"Error creating seed data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

