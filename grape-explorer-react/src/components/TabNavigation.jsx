import { useState } from 'react'

const TabNavigation = ({ activeTab, onTabChange }) => {
  const tabs = [
    { id: 'overview', label: 'Overview', icon: '🍇' },
    { id: 'tree', label: 'Family Tree', icon: '🌳' },
    { id: 'map', label: 'Producers', icon: '🗺️' },
    { id: 'research', label: 'Research', icon: '📚' }
  ]

  return (
    <div className="tab-buttons">
      {tabs.map(tab => (
        <button
          key={tab.id}
          className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
          onClick={() => onTabChange(tab.id)}
        >
          <span className="tab-icon">{tab.icon}</span>
          <span className="tab-label">{tab.label}</span>
        </button>
      ))}
    </div>
  )
}

export default TabNavigation