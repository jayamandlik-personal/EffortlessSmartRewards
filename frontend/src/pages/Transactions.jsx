import { useState, useEffect } from 'react'
import './Transactions.css'

const Transactions = ({ userId }) => {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTransactions()
  }, [userId])

  const fetchTransactions = async () => {
    try {
      const response = await fetch(`/api/users/${userId}/transactions?limit=100`)
      const data = await response.json()
      setTransactions(data)
    } catch (error) {
      console.error('Error fetching transactions:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading transactions...</div>
  }

  return (
    <div className="transactions-page">
      <h1 className="page-title">Transactions</h1>
      <div className="transactions-table-container">
        <table className="transactions-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Description</th>
              <th>Merchant</th>
              <th>Category</th>
              <th>Amount</th>
              <th>Reward Applied</th>
              <th>Savings</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((transaction) => (
              <tr key={transaction.id}>
                <td>{new Date(transaction.transaction_at).toLocaleDateString()}</td>
                <td>
                  <div className="transaction-description">
                    {transaction.description}
                    {transaction.memo && (
                      <span className="transaction-memo">{transaction.memo}</span>
                    )}
                  </div>
                </td>
                <td>{transaction.merchant_normalized || '-'}</td>
                <td>
                  <span className="category-badge">{transaction.category || 'Other'}</span>
                </td>
                <td className={transaction.value_amount_usd < 0 ? 'amount-negative' : 'amount-positive'}>
                  ${Math.abs(parseFloat(transaction.value_amount_usd)).toFixed(2)}
                </td>
                <td>
                  {transaction.reward_applied ? (
                    <span className="badge badge-success">Yes</span>
                  ) : transaction.matched_reward_id ? (
                    <span className="badge badge-missed">Missed</span>
                  ) : (
                    <span className="badge">-</span>
                  )}
                </td>
                <td>
                  {transaction.reward_savings_amount ? (
                    <span className="savings-amount">
                      +${parseFloat(transaction.reward_savings_amount).toFixed(2)}
                    </span>
                  ) : (
                    '-'
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Transactions

