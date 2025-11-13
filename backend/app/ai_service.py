"""
AI Agent Service using OpenAI API

This service generates:
1. Natural language summaries of spending and savings
2. Reward recommendations (auto-apply and Priceless experiences)
3. Notification decisioning logic

Configure OpenAI API key via OPENAI_API_KEY environment variable.
"""
import os
from typing import List, Dict, Optional
from decimal import Decimal
from datetime import datetime
from openai import OpenAI
from app.schemas import TransactionResponse, RewardResponse, AIInsightSummary
from app.models import User, Transaction, Reward


class AiInsightsService:
    """
    AI service for generating insights, summaries, and recommendations.
    Uses OpenAI API - ensure OPENAI_API_KEY is set in environment.
    """
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"  # Updated model name for OpenAI v2.x
    
    def generate_dashboard_summary(
        self,
        user,  # Can be User model or dict
        transactions: List,  # Can be Transaction models or dicts
        rewards_applied: List,  # Can be Transaction models or dicts
        rewards_missed: List,  # Can be Transaction models or dicts
        saved_auto_apply: Decimal,
        saved_notifications: Decimal,
        rewards_by_category: List[Dict]
    ) -> AIInsightSummary:
        """
        Generate natural language summary and insights for the dashboard.
        """
        
        # Prepare transaction summary
        # Handle both model objects and dicts
        def get_value(t, key, default=0):
            if isinstance(t, dict):
                return t.get(key, default)
            return getattr(t, key, default)
        
        total_spent = sum(abs(get_value(t, "value_amount_usd", 0)) for t in transactions if get_value(t, "value_amount_usd", 0) < 0)
        category_breakdown = {}
        for t in transactions:
            category = get_value(t, "category")
            value = get_value(t, "value_amount_usd", 0)
            if category and value < 0:
                category_breakdown[category] = category_breakdown.get(category, 0) + abs(value)
        
        top_categories = sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Get user info (handle both model and dict)
        if isinstance(user, dict):
            user_name = user.get("name", "")
            user_location = user.get("primary_geo_location")
        else:
            user_name = user.name
            user_location = user.primary_geo_location
        
        # Prepare prompt
        prompt = f"""You are a financial insights assistant for Effortless, a smart rewards platform.

User: {user_name}
Location: {user_location or 'Not specified'}
Time Period: Last 30 days

Spending Summary:
- Total Spent: ${total_spent:,.2f}
- Top Categories: {', '.join([f"{cat} (${amt:,.2f})" for cat, amt in top_categories])}

Savings Summary:
- Saved via Auto-Apply: ${saved_auto_apply:,.2f}
- Saved via Priceless Notifications: ${saved_notifications:,.2f}
- Total Savings: ${saved_auto_apply + saved_notifications:,.2f}

Rewards Applied: {len(rewards_applied)} transactions
Rewards Missed: {len(rewards_missed)} transactions

Rewards by Category:
{chr(10).join([f"- {r['category']}: ${r['total_savings']:,.2f} ({r['count']} transactions)" for r in rewards_by_category])}

Generate a friendly, concise summary (2-3 sentences) and 2-3 key insights about the user's spending patterns and savings opportunities.
Be specific and actionable.

Return your response as JSON with this exact structure:
{{
    "summary_text": "A 2-3 sentence summary of this month's spending and savings",
    "top_insights": ["Insight 1", "Insight 2", "Insight 3"]
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful financial assistant. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            import json
            ai_data = json.loads(result) if result else {}
            
            return AIInsightSummary(
                summary_text=ai_data.get("summary_text", ""),
                top_insights=ai_data.get("top_insights", []),
                recommended_auto_apply_rewards=[],
                recommended_priceless_experiences=[]
            )
        except Exception as e:
            # Fallback if API fails
            return AIInsightSummary(
                summary_text=f"This month, you've saved ${saved_auto_apply + saved_notifications:,.2f} through Effortless rewards. Most of your savings came from {top_categories[0][0] if top_categories else 'various categories'}.",
                top_insights=[
                    f"Your top spending category is {top_categories[0][0] if top_categories else 'dining'}",
                    f"You've saved ${saved_auto_apply:,.2f} through automatic rewards",
                    "Consider enabling more auto-apply rewards to maximize savings"
                ],
                recommended_auto_apply_rewards=[],
                recommended_priceless_experiences=[]
            )
    
    def generate_reward_recommendations(
        self,
        user,  # Can be User model or dict
        recent_transactions: List,  # Can be Transaction models or dicts
        available_rewards: List,  # Can be Reward models or dicts
        user_preferences: Optional[Dict] = None
    ) -> Dict[str, List]:
        """
        Generate recommendations for auto-apply rewards and Priceless experiences.
        """
        
        # Helper to get value from model or dict
        def get_attr(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)
        
        # Analyze transaction patterns
        merchant_counts = {}
        category_counts = {}
        for t in recent_transactions:
            merchant = get_attr(t, "merchant_normalized")
            category = get_attr(t, "category")
            if merchant:
                merchant_counts[merchant] = merchant_counts.get(merchant, 0) + 1
            if category:
                category_counts[category] = category_counts.get(category, 0) + 1
        
        top_merchants = sorted(merchant_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Filter available rewards
        auto_apply_candidates = [
            r for r in available_rewards
            if get_attr(r, "is_auto_applicable", False) and not get_attr(r, "requires_user_opt_in", False)
        ]
        priceless_experiences = [
            r for r in available_rewards
            if get_attr(r, "reward_type") == "experience"
        ]
        
        # Match rewards to user patterns
        recommended_auto_apply = []
        recommended_priceless = []
        
        # Simple matching logic (can be enhanced with AI)
        for reward in auto_apply_candidates:
            reward_category = get_attr(reward, "category")
            reward_merchant = get_attr(reward, "merchant_name")
            if reward_category in category_counts:
                recommended_auto_apply.append(reward)
            elif reward_merchant in merchant_counts:
                recommended_auto_apply.append(reward)
        
        # Filter Priceless experiences by geo-location
        user_geo = None
        if user_preferences:
            user_geo = user_preferences.get("priceless_geo_location")
        if not user_geo:
            user_geo = get_attr(user, "primary_geo_location")
        
        for reward in priceless_experiences:
            reward_geo_scope = get_attr(reward, "geo_scope", "global")
            reward_geo_city = get_attr(reward, "geo_city")
            if reward_geo_scope == "global" or (user_geo and reward_geo_city and user_geo.lower() in reward_geo_city.lower()):
                recommended_priceless.append(reward)
        
        # Use AI to refine recommendations
        user_name = get_attr(user, "name", "")
        user_location = get_attr(user, "primary_geo_location") or "Not specified"
        
        prompt = f"""You are a rewards recommendation engine for Effortless.

User: {user_name}
Location: {user_location}

Recent Transaction Patterns:
- Top Merchants: {', '.join([f"{m} ({c}x)" for m, c in top_merchants])}
- Top Categories: {', '.join([f"{c} ({n}x)" for c, n in top_categories])}

Available Auto-Apply Rewards: {len(auto_apply_candidates)}
Available Priceless Experiences: {len(priceless_experiences)}

Based on the user's spending patterns, recommend the top 3-5 rewards they should enable for auto-apply,
and the top 3-5 Priceless experiences they should be notified about.

Return JSON with:
{{
    "auto_apply_recommendations": ["reward_id_1", "reward_id_2", ...],
    "priceless_recommendations": ["reward_id_1", "reward_id_2", ...],
    "reasoning": "Brief explanation of recommendations"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a rewards recommendation assistant. Return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            import json
            ai_data = json.loads(result)
            
            # Map AI recommendations to actual rewards
            recommended_auto_ids = ai_data.get("auto_apply_recommendations", [])
            recommended_priceless_ids = ai_data.get("priceless_recommendations", [])
            
            # For now, return top matches (AI integration can be enhanced)
            return {
                "recommended_auto_apply": recommended_auto_apply[:5],
                "recommended_priceless": recommended_priceless[:5]
            }
        except Exception as e:
            # Fallback to simple matching
            return {
                "recommended_auto_apply": recommended_auto_apply[:5],
                "recommended_priceless": recommended_priceless[:5]
            }
    
    def should_send_notification(
        self,
        user: User,
        user_preferences: Dict,
        experience: Reward
    ) -> bool:
        """
        Decision logic for whether to send a Priceless experience notification.
        Respects user notification preferences.
        """
        if not user_preferences.get("priceless_notifications_enabled", True):
            return False
        
        if not user_preferences.get("notifications_enabled", True):
            return False
        
        # Check geo-match
        user_geo = user_preferences.get("priceless_geo_location") or user.primary_geo_location
        if experience.geo_scope != "global":
            if not user_geo or (experience.geo_city and user_geo.lower() not in experience.geo_city.lower()):
                return False
        
        # Check if experience is still valid
        now = datetime.now(experience.start_date.tzinfo if experience.start_date.tzinfo else None)
        if experience.start_date > now or (experience.end_date and experience.end_date < now):
            return False
        
        return True

