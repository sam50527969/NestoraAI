export default function CRMToolbar({
  searchTerm,
  onSearchChange,
  categoryFilter,
  onCategoryChange,
  categories = ["All"],
  totalLeads = 0,
  visibleLeads = 0,
}) {
  return (
    <section className="crm-toolbar">
      <div className="crm-toolbar-field">
        <label htmlFor="crm-search">Search leads</label>
        <input
          id="crm-search"
          type="text"
          value={searchTerm}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder="Search by name, category, address, phone, or website"
        />
      </div>

      <div className="crm-toolbar-field">
        <label htmlFor="crm-category">Category</label>
        <select
          id="crm-category"
          value={categoryFilter}
          onChange={(event) => onCategoryChange(event.target.value)}
        >
          {categories.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
      </div>

      <div className="crm-lead-counter">
        <span>{visibleLeads}</span>
        <p>{visibleLeads === 1 ? "lead shown" : "leads shown"}</p>
        <small>{totalLeads} total saved</small>
      </div>
    </section>
  );
}
