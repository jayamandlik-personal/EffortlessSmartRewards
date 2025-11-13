import { useState, useEffect } from 'react'
import { Save } from 'lucide-react'
import './Settings.css'

const Settings = ({ userId }) => {
  const [preferences, setPreferences] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    fetchPreferences()
  }, [userId])

  const fetchPreferences = async () => {
    try {
      const response = await fetch(`/api/users/${userId}/preferences`)
      const data = await response.json()
      setPreferences(data)
    } catch (error) {
      console.error('Error fetching preferences:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setSaved(false)
    try {
      const response = await fetch(`/api/users/${userId}/preferences`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(preferences),
      })
      if (response.ok) {
        setSaved(true)
        setTimeout(() => setSaved(false), 3000)
      }
    } catch (error) {
      console.error('Error saving preferences:', error)
    } finally {
      setSaving(false)
    }
  }

  const handleChange = (field, value) => {
    setPreferences((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  if (loading) {
    return <div className="loading">Loading settings...</div>
  }

  if (!preferences) {
    return <div className="error">Error loading settings</div>
  }

  return (
    <div className="settings-page">
      <h1 className="page-title">Settings & Preferences</h1>

      <div className="settings-container">
        <div className="settings-section">
          <h2 className="settings-section-title">Priceless Experiences</h2>
          <div className="settings-card">
            <div className="setting-item">
              <div className="setting-info">
                <label className="setting-label">Geo-Location for Priceless Experiences</label>
                <p className="setting-description">
                  Set your city/region to receive notifications about nearby Priceless experiences
                </p>
              </div>
              <input
                type="text"
                className="setting-input"
                value={preferences.priceless_geo_location || ''}
                onChange={(e) => handleChange('priceless_geo_location', e.target.value)}
                placeholder="e.g., San Francisco, CA"
              />
            </div>
          </div>
        </div>

        <div className="settings-section">
          <h2 className="settings-section-title">Notifications</h2>
          <div className="settings-card">
            <div className="setting-item">
              <div className="setting-info">
                <label className="setting-label">Enable Notifications</label>
                <p className="setting-description">
                  Receive notifications about rewards and account activity
                </p>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={preferences.notifications_enabled}
                  onChange={(e) => handleChange('notifications_enabled', e.target.checked)}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <label className="setting-label">Priceless Experience Notifications</label>
                <p className="setting-description">
                  Get notified about nearby Priceless experiences based on your geo-location
                </p>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={preferences.priceless_notifications_enabled}
                  onChange={(e) => handleChange('priceless_notifications_enabled', e.target.checked)}
                  disabled={!preferences.notifications_enabled}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <label className="setting-label">Auto-Apply Rewards Activity Summary</label>
                <p className="setting-description">
                  Receive periodic summaries of rewards automatically applied to your transactions
                </p>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={preferences.notifications_enabled}
                  onChange={(e) => handleChange('notifications_enabled', e.target.checked)}
                  disabled={!preferences.notifications_enabled}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>

        <div className="settings-section">
          <h2 className="settings-section-title">Rewards</h2>
          <div className="settings-card">
            <div className="setting-item">
              <div className="setting-info">
                <label className="setting-label">Auto-Apply Rewards</label>
                <p className="setting-description">
                  Automatically apply eligible rewards to your transactions when available
                </p>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={preferences.auto_apply_rewards_enabled}
                  onChange={(e) => handleChange('auto_apply_rewards_enabled', e.target.checked)}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>

        <div className="settings-actions">
          <button
            className="save-button"
            onClick={handleSave}
            disabled={saving}
          >
            <Save size={18} />
            {saving ? 'Saving...' : 'Save Preferences'}
          </button>
          {saved && <span className="save-message">Preferences saved!</span>}
        </div>
      </div>
    </div>
  )
}

export default Settings

