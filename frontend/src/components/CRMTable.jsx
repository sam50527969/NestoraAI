function getMapsUrl(lead) {
  if (lead.google_maps_url) return lead.google_maps_url;
  if (lead.maps_url) return lead.maps_url;

  const latitude = lead.latitude ?? lead.lat;
  const longitude = lead.longitude ?? lead.lon ?? lead.lng;

  if (latitude && longitude) {
    return `https://www.google.com/maps/search/?api=1&query=${latitude},${longitude}`;
  }

  const query = [lead.name, lead.address].filter(Boolean).join(" ");

  if (!query) return null;

  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`;
}

function getWebsiteUrl(website) {
  if (!website) return null;
  if (website.startsWith("http://") || website.startsWith("https://")) return website;
  return `https://${website}`;
}

function getLeadKey(lead, index) {
  return lead.id || lead.source_id || lead.place_id || lead.osm_id || `${lead.name || "lead"}-${index}`;
}

function getStatusClassName(status) {
  return `status-badge ${(status || "New").toLowerCase().replace(/\s+/g, "-")}`;
}

export default function CRMTable({
  leads = [],
  isLoading = false,
  selectedLeadId = null,
  onSelectLead,
}) {
  if (isLoading) {
    return (
      <section className="crm-table-state">
        <p>Loading saved leads...</p>
      </section>
    );
  }

  if (!leads.length) {
    return (
      <section className="crm-table-state">
        <h3>No saved leads found</h3>
        <p>Save leads from the discovery table and they will appear here.</p>
      </section>
    );
  }

  return (
    <section className="crm-table-wrapper">
      <table className="crm-table">
        <thead>
          <tr>
            <th>Business</th>
            <th>Category</th>
            <th>Phone</th>
            <th>Website</th>
            <th>Maps</th>
            <th>Status</th>
            <th>Priority</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {leads.map((lead, index) => {
            const mapsUrl = getMapsUrl(lead);
            const websiteUrl = getWebsiteUrl(lead.website || lead.url);
            const isSelected = selectedLeadId === lead.id;

            return (
              <tr
                key={getLeadKey(lead, index)}
                className={isSelected ? "selected-row" : ""}
                onClick={() => onSelectLead?.(lead)}
              >
                <td>
                  <strong>{lead.name || "Unknown Business"}</strong>
                  <small>{lead.address || lead.source || "Saved lead"}</small>
                </td>
                <td>{lead.category || lead.type || lead.business_type || "Unknown"}</td>
                <td>
                  {lead.phone ? <a href={`tel:${lead.phone}`}>{lead.phone}</a> : "-"}
                </td>
                <td>
                  {websiteUrl ? (
                    <a href={websiteUrl} target="_blank" rel="noreferrer" onClick={(event) => event.stopPropagation()}>
                      Visit
                    </a>
                  ) : (
                    "-"
                  )}
                </td>
                <td>
                  {mapsUrl ? (
                    <a href={mapsUrl} target="_blank" rel="noreferrer" onClick={(event) => event.stopPropagation()}>
                      Open
                    </a>
                  ) : (
                    "-"
                  )}
                </td>
                <td>
                  <span className={getStatusClassName(lead.status)}>{lead.status || "New"}</span>
                </td>
                <td>{lead.priority || "Medium"}</td>
                <td>
                  <button
                    type="button"
                    className="secondary-button compact"
                    onClick={(event) => {
                      event.stopPropagation();
                      onSelectLead?.(lead);
                    }}
                  >
                    Details
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}
