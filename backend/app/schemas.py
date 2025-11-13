from pydantic import BaseModel, EmailStr
from datetime import datetime
from decimal import Decimal
from typing import Optional, List


class UserBase(BaseModel):
    customer_id: int
    name: str
    email: EmailStr
    primary_geo_location: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserPreferenceBase(BaseModel):
    notifications_enabled: bool = True
    priceless_geo_location: Optional[str] = None
    priceless_notifications_enabled: bool = True
    auto_apply_rewards_enabled: bool = True


class UserPreferenceUpdate(UserPreferenceBase):
    pass


class UserPreferenceResponse(UserPreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    customer_id: int
    account_id: int
    posted_at: datetime
    transaction_at: datetime
    description: str
    memo: Optional[str] = None
    value_amount_usd: Decimal


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int
    merchant_normalized: Optional[str] = None
    category: Optional[str] = None
    location_inferred: Optional[str] = None
    matched_reward_id: Optional[int] = None
    reward_applied: bool = False
    reward_savings_amount: Optional[Decimal] = None
    notification_triggered: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class RewardBase(BaseModel):
    merchant_name: str
    reward_type: str
    reward_label: str
    reward_description: Optional[str] = None
    category: Optional[str] = None
    terms: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    max_savings_amount: Optional[Decimal] = None
    geo_scope: str = "global"
    is_auto_applicable: bool = False
    requires_user_opt_in: bool = False


class RewardCreate(RewardBase):
    percentage_value: Optional[Decimal] = None
    fixed_amount_value: Optional[Decimal] = None


class RewardResponse(RewardBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class RewardsByCategory(BaseModel):
    category: str
    total_savings: Decimal
    count: int


class DashboardSummary(BaseModel):
    total_balance: Decimal
    total_transactions: int
    saved_via_auto_apply: Decimal
    saved_via_notifications: Decimal
    rewards_by_category: List[RewardsByCategory]
    recent_rewards_applied: List[TransactionResponse]
    recent_rewards_missed: List[TransactionResponse]


class AIInsightSummary(BaseModel):
    summary_text: str
    top_insights: List[str]
    recommended_auto_apply_rewards: List[RewardResponse]
    recommended_priceless_experiences: List[RewardResponse]

