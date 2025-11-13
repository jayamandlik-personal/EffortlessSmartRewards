import { useState, useEffect } from 'react'
import { Gift, CheckCircle, XCircle } from 'lucide-react'
import './Rewards.css'

const Rewards = ({ userId }) => {
  const [rewards, setRewards] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchRewards()
  }, [])

  const fetchRewards = async () => {
    try {
      const response = await fetch('/api/rewards?active_only=true')
      const data = await response.json()
      setRewards(data)
    } catch (error) {
      console.error('Error fetching rewards:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading rewards...</div>
  }

  const getRewardTypeColor = (type) => {
    switch (type) {
      case 'experience':
        return '#764ba2'
      case 'percentage_cashback':
        return '#667eea'
      case 'fixed_amount':
        return '#43e97b'
      default:
        return '#6e6e73'
    }
  }

  return (
    <div className="rewards-page">
      <h1 className="page-title">Available Rewards</h1>
      <div className="rewards-grid">
        {rewards.map((reward) => (
          <div key={reward.id} className="reward-card">
            <div className="reward-header">
              <div className="reward-icon" style={{ backgroundColor: `${getRewardTypeColor(reward.reward_type)}20` }}>
                <Gift size={24} color={getRewardTypeColor(reward.reward_type)} />
              </div>
              <div className="reward-status">
                {reward.is_auto_applicable && !reward.requires_user_opt_in ? (
                  <span className="status-badge auto-apply">
                    <CheckCircle size={14} /> Auto-Apply
                  </span>
                ) : (
                  <span className="status-badge opt-in">
                    <XCircle size={14} /> Opt-In Required
                  </span>
                )}
              </div>
            </div>
            <div className="reward-content">
              <h3 className="reward-label">{reward.reward_label}</h3>
              <p className="reward-description">{reward.reward_description}</p>
              <div className="reward-details">
                <div className="detail-item">
                  <span className="detail-label">Category:</span>
                  <span className="detail-value">{reward.category || 'N/A'}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Merchant:</span>
                  <span className="detail-value">{reward.merchant_name}</span>
                </div>
                {reward.percentage_value && (
                  <div className="detail-item">
                    <span className="detail-label">Cashback:</span>
                    <span className="detail-value highlight">{reward.percentage_value}%</span>
                  </div>
                )}
                {reward.fixed_amount_value && (
                  <div className="detail-item">
                    <span className="detail-label">Value:</span>
                    <span className="detail-value highlight">
                      ${parseFloat(reward.fixed_amount_value).toFixed(2)}
                    </span>
                  </div>
                )}
                {reward.geo_scope !== 'global' && (
                  <div className="detail-item">
                    <span className="detail-label">Location:</span>
                    <span className="detail-value">{reward.geo_city || reward.geo_country || reward.geo_scope}</span>
                  </div>
                )}
              </div>
              {reward.terms && (
                <div className="reward-terms">
                  <strong>Terms:</strong> {reward.terms}
                </div>
              )}
              <div className="reward-dates">
                <div className="date-item">
                  <span>Valid from:</span> {new Date(reward.start_date).toLocaleDateString()}
                </div>
                {reward.end_date && (
                  <div className="date-item">
                    <span>Valid until:</span> {new Date(reward.end_date).toLocaleDateString()}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Rewards

