import { createSlice } from "@reduxjs/toolkit";

// This shape MUST mirror backend/app/models.py Complaint exactly.
// If you add a field on the backend, add it here too.
const initialState = {
  complaint: null, // null until the first log_complaint call succeeds
  chatLog: [], // { role: 'user' | 'assistant', text, fileName? }
  status: "idle", // idle | loading | error
};

const complaintSlice = createSlice({
  name: "complaint",
  initialState,
  reducers: {
    setLoading(state) {
      state.status = "loading";
    },
    setError(state) {
      state.status = "error";
    },
    chatMessageSent(state, action) {
      // action.payload: { text, fileName? }
      state.chatLog.push({ role: "user", ...action.payload });
    },
    chatResponseReceived(state, action) {
      // action.payload: { reply, complaint, tool_used }
      state.complaint = action.payload.complaint;
      state.chatLog.push({ role: "assistant", text: action.payload.reply });
      state.status = "idle";
    },
  },
});

export const { setLoading, setError, chatMessageSent, chatResponseReceived } =
  complaintSlice.actions;

// Derived "Pending Triage" / "Ready to Commit" badge — mirrors
// Complaint.is_ready_to_commit on the backend. Keep logic in sync.
export const selectIsReadyToCommit = (state) => {
  const c = state.complaint.complaint;
  if (!c) return false;
  return Boolean(
    c.product_name &&
      c.batch_lot_number &&
      c.complaint_description &&
      c.risk_assessment?.severity
  );
};

export default complaintSlice.reducer;
