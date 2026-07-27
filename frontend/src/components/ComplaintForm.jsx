import { useState } from "react";
import { useSelector } from "react-redux";
import { selectIsReadyToCommit } from "../store/complaintSlice";
import { commitComplaint } from "../api/chatApi";

// Fields are read-only inputs — per the assignment, this form must ONLY be
// populated/edited via the Copilot chat, never typed into directly.
function Field({ label, value }) {
  return (
    <div className="field">
      <label>{label}</label>
      <input type="text" value={value || ""} readOnly placeholder="Awaiting AI extraction..." />
    </div>
  );
}

export default function ComplaintForm() {
  const complaint = useSelector((state) => state.complaint.complaint);
  const isReady = useSelector(selectIsReadyToCommit);

  const c = complaint || {};
  const risk = c.risk_assessment || {};

  const [isCommitting, setIsCommitting] = useState(false);
  const [commitSuccess, setCommitSuccess] = useState(false);

  const handleCommit = async () => {
    setIsCommitting(true);
    try {
      await commitComplaint(c);
      setCommitSuccess(true);
      setTimeout(() => setCommitSuccess(false), 5000);
    } catch (error) {
      console.error("Failed to commit:", error);
      alert("Failed to commit to QMS Ledger.");
    } finally {
      setIsCommitting(false);
    }
  };

  return (
    <div className="complaint-form">
      <div className="form-header">
        <div>
          <h2>Log Customer Complaint</h2>
          <p className="subtitle">API &amp; FDF Quality Assurance Module</p>
        </div>
        <span className={`badge ${isReady ? "ready" : "pending"}`}>
          {isReady ? "Ready to Commit" : "Pending Triage"}
        </span>
      </div>

      <section>
        <h3>1. Origin &amp; Customer Details</h3>
        <div className="row">
          <Field label="Complaint Source" value={c.complaint_source} />
          <Field label="Customer Name" value={c.customer_name} />
        </div>
      </section>

      <section>
        <h3>2. Product &amp; Batch Identification</h3>
        <div className="row">
          <Field label="Product Name" value={c.product_name} />
          <Field label="Product Strength" value={c.product_strength} />
        </div>
        <div className="row">
          <Field label="Batch / Lot Number" value={c.batch_lot_number} />
          <Field label="Affected Quantity" value={c.affected_quantity} />
        </div>
        <div className="row">
          <Field label="Manufacturing Date" value={c.manufacturing_date} />
          <Field label="Expiry Date" value={c.expiry_date} />
        </div>
      </section>

      <section>
        <h3>3. Facility &amp; Material Impact</h3>
        <div className="row">
          <Field label="Originating Site Block" value={c.originating_site_block} />
          <Field label="Impacted Non-Product Materials (NPM)" value={c.impacted_npm} />
        </div>
      </section>

      <section>
        <h3>4. Defect Analysis</h3>
        <Field label="Complaint Category" value={c.complaint_category} />
        <div className="field">
          <label>Complaint Description</label>
          <textarea readOnly value={c.complaint_description || ""} placeholder="AI will synthesize the complaint into a formal QMS description..." />
        </div>

        <div className="risk-box">
          <h4>AI Copilot Risk Assessment</h4>
          <div className="row risk-row">
            <div className="field severity-field">
              <label>Severity (Suggested)</label>
              <input type="text" readOnly value={risk.severity || ""} />
            </div>
            <div className="field action-field">
              <label>Suggested Next Action</label>
              <textarea readOnly value={risk.suggested_next_action || ""} rows="2" />
            </div>
          </div>
          <div className="field">
            <label>Initial Risk Assessment</label>
            <textarea readOnly value={risk.initial_risk_assessment || ""} rows="4" />
          </div>
        </div>
      </section>

      <button 
        className={`commit-btn ${commitSuccess ? 'success' : ''}`}
        disabled={!isReady || isCommitting || commitSuccess}
        onClick={handleCommit}
      >
        {isCommitting ? "Committing..." : commitSuccess ? "✓ Saved to Database" : "Commit to QMS Ledger"}
      </button>
    </div>
  );
}
