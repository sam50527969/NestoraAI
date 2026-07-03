import { useState } from 'react'
import './App.css'

const stats = [
  { label: 'New Leads', value: '0', note: 'Priority metric' },
  { label: "Today's Revenue", value: '0 QAR', note: 'Target: 200 QAR' },
  { label: 'Tasks Due Today', value: '0', note: 'No overdue tasks' },
]

function App() {
  const [activePage, setActivePage] = useState('Dashboard')

  const pages = ['Dashboard', 'CEO Agent', 'Sales', 'CRM', 'Marketing', 'Finance']

  return (
    <div className="app">
      <aside className="sidebar">
        <div>
          <h2>Nestora AI</h2>
          <p className="sidebar-subtitle">Business command center</p>
        </div>

        <nav>
          {pages.map((page) => (
            <button
              key={page}
              className={activePage === page ? 'active' : ''}
              onClick={() => setActivePage(page)}
            >
              {page}
            </button>
          ))}
        </nav>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">Version 0.2</p>
            <h1>{activePage}</h1>
            <p>Your AI business operating system</p>
          </div>
          <button className="primary">Start AI</button>
        </header>

        {activePage === 'Dashboard' && (
          <>
            <section className="cards">
              {stats.map((item) => (
                <div className="card" key={item.label}>
                  <p>{item.label}</p>
                  <h2>{item.value}</h2>
                  <span>{item.note}</span>
                </div>
              ))}
            </section>

            <section className="panel">
              <div>
                <p className="eyebrow">CEO Agent</p>
                <h2>Today’s Recommendation</h2>
              </div>
              <p>
                Focus on finding 20 small businesses in Qatar today. Start with
                cafés, salons, bakeries, and car wash businesses. Offer the 99
                QAR Starter Business Package.
              </p>
              <button className="secondary">Generate Today’s Plan</button>
            </section>
          </>
        )}

        {activePage !== 'Dashboard' && (
          <section className="panel">
            <p className="eyebrow">{activePage}</p>
            <h2>{activePage} module coming next</h2>
            <p>
              This section will be built as part of the next milestones. For
              now, the navigation is working and the dashboard foundation is
              ready.
            </p>
          </section>
        )}
      </main>
    </div>
  )
}

export default App