function LeadTable({ leads }) {
  return (
    <div className="panel">
      <div className="table-header">
        <div>
          <p className="eyebrow">Lead Finder</p>
          <h2>Sample Leads</h2>
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
            <th>Email</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {leads.map((lead) => (
            <tr key={lead.id}>
              <td>{lead.businessName}</td>
              <td>{lead.category}</td>
              <td>{lead.location}</td>
              <td>{lead.phone}</td>
              <td>{lead.email}</td>
              <td>{lead.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default LeadTable;