import './App.css'

function App() {
  return (
    <div className="app">
      <aside className="sidebar">
        <h2>Nestora AI</h2>
        <nav>
          <button>Dashboard</button>
          <button>CEO Agent</button>
          <button>Sales</button>
          <button>CRM</button>
          <button>Marketing</button>
          <button>Finance</button>
        </nav>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <h1>Dashboard</h1>
            <p>Your AI business command center</p>
          </div>
          <button className="primary">Start AI</button>
        </header>

        <section className="cards">
          <div className="card">
            <p>Revenue Today</p>
            <h2>0 QAR</h2>
          </div>
          <div className="card">
            <p>Leads Found</p>
            <h2>0</h2>
          </div>
          <div className="card">
            <p>Interested Clients</p>
            <h2>0</h2>
          </div>
          <div className="card">
            <p>Pending Tasks</p>
            <h2>0</h2>
          </div>
        </section>

        <section className="panel">
          <h2>CEO Agent Recommendation</h2>
          <p>
            Focus on finding 20 small businesses in Qatar today. Start with
            cafés, salons, bakeries, and car wash businesses. Offer the 99 QAR
            Starter Business Package.
          </p>
          <button className="secondary">Generate Today’s Plan</button>
        </section>
      </main>
    </div>
  )
}

export default App