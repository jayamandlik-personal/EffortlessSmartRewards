import { useState, useEffect } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { DollarSign, TrendingUp, Gift, Bell } from 'lucide-react'
import './Dashboard.css'

const Dashboard = ({ userId }) => {
  const [dashboardData, setDashboardData] = useState(null)
  const [aiInsights, setAiInsights] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
    fetchAIInsights()
  }, [userId])

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`/api/users/${userId}/dashboard-summary`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      setDashboardData(data)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      setDashboardData(null) // Set to null on error
    } finally {
      setLoading(false)
    }
  }

  const fetchAIInsights = async () => {
    try {
      const response = await fetch(`/api/users/${userId}/ai-insights`)
      const data = await response.json()
      setAiInsights(data)
    } catch (error) {
      console.error('Error fetching AI insights:', error)
    }
  }

  if (loading) {
    return <div className="loading">Loading dashboard...</div>
  }

  if (!dashboardData) {
    return <div className="error">Error loading dashboard data</div>
  }

  // Prepare pie chart data
  const pieData = dashboardData.rewards_by_category.map((item) => ({
    name: item.category || 'Other',
    value: parseFloat(item.total_savings),
  }))

  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b']

  return (
    <div className="dashboard">
      <h1 className="page-title">Dashboard</h1>

      {/* Account Summary */}
      <div className="account-summary">
        <div className="summary-card balance-card">
          <div className="card-label">Total Balance</div>
          <div className="card-value">
            ${Math.abs(parseFloat(dashboardData.total_balance)).toLocaleString('en-US', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </div>
          <div className="card-subtitle">{dashboardData.total_transactions} transactions</div>
        </div>
      </div>

      {/* Savings KPIs */}
      <div className="savings-section">
        <h2 className="section-title">Rewards & Savings</h2>
        <div className="kpi-grid">
          <div className="kpi-card">
            <div className="kpi-icon" style={{ backgroundColor: '#667eea20' }}>
              <DollarSign size={24} color="#667eea" />
            </div>
            <div className="kpi-content">
              <div className="kpi-label">Saved via Auto-Apply</div>
              <div className="kpi-value">
                ${parseFloat(dashboardData.saved_via_auto_apply).toLocaleString('en-US', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </div>
            </div>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon" style={{ backgroundColor: '#764ba220' }}>
              <Bell size={24} color="#764ba2" />
            </div>
            <div className="kpi-content">
              <div className="kpi-label">Saved via Priceless Notifications</div>
              <div className="kpi-value">
                ${parseFloat(dashboardData.saved_via_notifications).toLocaleString('en-US', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </div>
            </div>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon" style={{ backgroundColor: '#43e97b20' }}>
              <TrendingUp size={24} color="#43e97b" />
            </div>
            <div className="kpi-content">
              <div className="kpi-label">Total Savings</div>
              <div className="kpi-value">
                ${(
                  parseFloat(dashboardData.saved_via_auto_apply) +
                  parseFloat(dashboardData.saved_via_notifications)
                ).toLocaleString('en-US', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Rewards by Category Pie Chart */}
      {pieData.length > 0 && (
        <div className="chart-section">
          <h2 className="section-title">Rewards by Category</h2>
          <div className="chart-card">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `$${parseFloat(value).toFixed(2)}`} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* AI Insights */}
      {aiInsights && (
        <div className="insights-section">
          <h2 className="section-title">AI Insights</h2>
          <div className="insights-card">
            <p className="insights-summary">{aiInsights.summary_text}</p>
            {aiInsights.top_insights && aiInsights.top_insights.length > 0 && (
              <div className="insights-list">
                <h3>Key Insights:</h3>
                <ul>
                  {aiInsights.top_insights.map((insight, idx) => (
                    <li key={idx}>{insight}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Recommended Rewards */}
          {aiInsights.recommended_auto_apply_rewards &&
            aiInsights.recommended_auto_apply_rewards.length > 0 && (
              <div className="recommendations-card">
                <h3>
                  <Gift size={20} /> Recommended Auto-Apply Rewards
                </h3>
                <div className="rewards-list">
                  {aiInsights.recommended_auto_apply_rewards.map((reward) => (
                    <div key={reward.id} className="reward-item">
                      <div className="reward-label">{reward.reward_label}</div>
                      <div className="reward-description">{reward.reward_description}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

          {/* Recommended Priceless Experiences */}
          {aiInsights.recommended_priceless_experiences &&
            aiInsights.recommended_priceless_experiences.length > 0 && (
              <div className="recommendations-card">
                <h3>
                  <Bell size={20} /> Recommended Priceless Experiences
                </h3>
                <div className="rewards-list">
                  {aiInsights.recommended_priceless_experiences.map((reward) => (
                    <div key={reward.id} className="reward-item">
                      <div className="reward-label">{reward.reward_label}</div>
                      <div className="reward-description">{reward.reward_description}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
        </div>
      )}

      {/* Recent Transactions */}
      <div className="recent-section">
        <h2 className="section-title">Recent Rewards Applied</h2>
        <div className="transactions-list">
          {dashboardData.recent_rewards_applied.slice(0, 5).map((transaction) => (
            <div key={transaction.id} className="transaction-item">
              <div className="transaction-info">
                <div className="transaction-merchant">
                  {transaction.merchant_normalized || transaction.description}
                </div>
                <div className="transaction-date">
                  {new Date(transaction.transaction_at).toLocaleDateString()}
                </div>
              </div>
              <div className="transaction-amount savings">
                +${parseFloat(transaction.reward_savings_amount || 0).toFixed(2)} saved
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Dashboard

