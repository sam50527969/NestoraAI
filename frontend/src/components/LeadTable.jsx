function LeadTable({ leads = [] }) {
  function openMap(lead) {
    const query = encodeURIComponent(`${lead.businessName} ${lead.location}`);
    window.open(`https://www.google.com/maps/search/?api=1&query=${query}`, "_blank");
  }

  return (
    <section className="panel">
      <div className="table-header">
        <div>
          <h2>Lead Finder</h2>
          <p className="eyebrow">Real Business Leads</p>
        </div>
        <button className="secondary">Find More Leads</button>
      </div>

      <table className="lead-table">
        <thead>
          <tr>
            <th>Business</th>
            <th>Category</th>
            <th>Location</th>
            <th>Phone</th>
            <th>Website</th>
            <th>Map</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {leads.map((lead) => (
            <tr key={lead.id}>
              <td>{lead.businessName}</td>
              <td>{lead.category}</td>
              <td>{lead.location}</td>
              <td>{lead.phone || "Not found"}</td>
              <td>
                {lead.website && lead.website !== "Not found" ? (
                  <a href={lead.website} target="_blank" rel="noreferrer">
                    Open Website
                  </a>
                ) : (
                  "Not found"
                )}
              </td>
              <td>
                <button className="small-btn" onClick={() => openMap(lead)}>
                  Open Map
                </button>
              </td>
              <td>{lead.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

export default LeadTable;