import {
  useEffect,
  useState,
} from "react";

import {
  formToWorkspace,
  INDUSTRY_OPTIONS,
  SIZE_OPTIONS,
  workspaceToForm,
} from "./workspacePayload";

function errorMessage(error) {
  if (!error?.message) {
    return "The workspace could not be saved.";
  }

  try {
    const parsed = JSON.parse(
      error.message,
    );

    if (
      typeof parsed.detail
      === "string"
    ) {
      return parsed.detail;
    }
  } catch {
    return error.message;
  }

  return error.message;
}

function WorkspaceForm({
  workspace = null,
  submitLabel = "Save workspace",
  onSubmit,
  onCancel = null,
}) {
  const [
    form,
    setForm,
  ] = useState(
    () => workspaceToForm(
      workspace,
    ),
  );

  const [
    submitting,
    setSubmitting,
  ] = useState(false);

  const [error, setError] =
    useState("");

  useEffect(() => {
    setForm(
      workspaceToForm(
        workspace,
      ),
    );
    setError("");
  }, [workspace]);

  function updateField(event) {
    const {
      name,
      value,
    } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function submit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      await onSubmit(
        formToWorkspace(
          form,
          workspace,
        ),
      );
    } catch (submitError) {
      setError(
        errorMessage(
          submitError,
        ),
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form
      className="workspace-form"
      onSubmit={submit}
    >
      <section className="workspace-form-section">
        <h3>Business identity</h3>

        <p>
          Define the organization Nestora
          will operate for.
        </p>

        <div className="workspace-form-grid">
          <label>
            Business name

            <input
              name="name"
              value={form.name}
              onChange={updateField}
              minLength={2}
              maxLength={200}
              required
            />
          </label>

          <label>
            Industry

            <select
              name="industry"
              value={form.industry}
              onChange={updateField}
            >
              {INDUSTRY_OPTIONS.map(
                ([value, label]) => (
                  <option
                    key={value}
                    value={value}
                  >
                    {label}
                  </option>
                ),
              )}
            </select>
          </label>

          <label>
            Business type

            <input
              name="business_type"
              value={
                form.business_type
              }
              onChange={updateField}
              placeholder="Agency, shop, consultancy..."
              maxLength={120}
            />
          </label>

          <label>
            Business size

            <select
              name="size"
              value={form.size}
              onChange={updateField}
            >
              {SIZE_OPTIONS.map(
                ([value, label]) => (
                  <option
                    key={value}
                    value={value}
                  >
                    {label}
                  </option>
                ),
              )}
            </select>
          </label>

          <label className="workspace-form-wide">
            Description

            <textarea
              name="description"
              value={form.description}
              onChange={updateField}
              maxLength={2000}
              placeholder="What does this business do?"
            />
          </label>

          <label className="workspace-form-wide">
            Products and services

            <input
              name="products_services"
              value={
                form.products_services
              }
              onChange={updateField}
              placeholder="Separate items with commas"
            />
          </label>
        </div>
      </section>

      <section className="workspace-form-section">
        <h3>Location and language</h3>

        <p>
          These values control regional,
          timezone, and language context.
        </p>

        <div className="workspace-form-grid">
          <label>
            Country

            <input
              name="country"
              value={form.country}
              onChange={updateField}
              minLength={2}
              maxLength={100}
              required
            />
          </label>

          <label>
            City

            <input
              name="city"
              value={form.city}
              onChange={updateField}
              maxLength={100}
            />
          </label>

          <label>
            Region or state

            <input
              name="region"
              value={form.region}
              onChange={updateField}
              maxLength={100}
            />
          </label>

          <label>
            Timezone

            <input
              name="timezone"
              value={form.timezone}
              onChange={updateField}
              placeholder="Asia/Qatar"
              maxLength={100}
            />
          </label>

          <label>
            Locale

            <input
              name="locale"
              value={form.locale}
              onChange={updateField}
              placeholder="en-QA"
              maxLength={50}
            />
          </label>

          <label>
            Preferred languages

            <input
              name="preferred_languages"
              value={
                form.preferred_languages
              }
              onChange={updateField}
              placeholder="English, Arabic"
            />
          </label>
        </div>
      </section>

      <section className="workspace-form-section">
        <h3>Operating profile</h3>

        <p>
          Supply the minimum financial and
          capacity context used across
          Nestora.
        </p>

        <div className="workspace-form-grid">
          <label>
            Currency

            <input
              name="currency"
              value={form.currency}
              onChange={updateField}
              minLength={3}
              maxLength={10}
              placeholder="USD"
              required
            />
          </label>

          <label>
            Employee count

            <input
              type="number"
              name="employee_count"
              value={
                form.employee_count
              }
              onChange={updateField}
              min="0"
              required
            />
          </label>

          <label>
            Number of locations

            <input
              type="number"
              name="locations_count"
              value={
                form.locations_count
              }
              onChange={updateField}
              min="1"
              required
            />
          </label>
        </div>
      </section>

      {error && (
        <div
          className="workspace-form-error"
          role="alert"
        >
          {error}
        </div>
      )}

      <div className="workspace-form-actions">
        <button
          type="submit"
          className="primary"
          disabled={submitting}
        >
          {submitting
            ? "Saving..."
            : submitLabel}
        </button>

        {onCancel && (
          <button
            type="button"
            className="secondary"
            onClick={onCancel}
            disabled={submitting}
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

export default WorkspaceForm;
