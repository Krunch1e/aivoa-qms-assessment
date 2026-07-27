import { useState, useRef } from "react";
import { useSelector, useDispatch } from "react-redux";
import { chatMessageSent, chatResponseReceived, setLoading, setError } from "../store/complaintSlice";
import { sendChatMessage } from "../api/chatApi";

export default function CopilotChat() {
  const dispatch = useDispatch();
  const chatLog = useSelector((state) => state.complaint.chatLog);
  const currentComplaint = useSelector((state) => state.complaint.complaint);
  const status = useSelector((state) => state.complaint.status);

  const [input, setInput] = useState("");
  const [pendingFile, setPendingFile] = useState(null);
  const fileInputRef = useRef(null);

  async function handleSend() {
    if (!input.trim() && !pendingFile) return;

    dispatch(
      chatMessageSent({
        text: input || `Uploaded ${pendingFile?.name}`,
        fileName: pendingFile?.name,
      })
    );
    dispatch(setLoading());

    try {
      const result = await sendChatMessage(input, currentComplaint, pendingFile);
      dispatch(chatResponseReceived(result));
    } catch (err) {
      dispatch(setError());
      console.error(err);
    }

    setInput("");
    setPendingFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="copilot-chat">
      <div className="chat-header">
        <h3>AIVOA Copilot</h3>
        <p className="subtitle">Drop complaint files or paste text below.</p>
      </div>

      <div className="chat-log">
        {chatLog.length === 0 && (
          <div className="message assistant">
            Ready to process new complaints. You can paste the raw email from
            the customer, or upload a PDF of the complaint report. I will
            extract the data and run the initial risk assessment.
          </div>
        )}
        {chatLog.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            {msg.fileName ? `📄 ${msg.fileName}` : msg.text}
          </div>
        ))}
        {status === "loading" && <div className="message assistant loading">Thinking…</div>}
      </div>

      {pendingFile && (
        <div className="pending-file-badge">
          <span className="file-name">📄 {pendingFile.name}</span>
          <button className="remove-file-btn" onClick={() => {
            setPendingFile(null);
            if (fileInputRef.current) fileInputRef.current.value = "";
          }} title="Remove file">✕</button>
        </div>
      )}

      <div className="chat-input-row">
        <button className="icon-btn" onClick={() => fileInputRef.current.click()} title="Attach file">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt"
          style={{ display: "none" }}
          onChange={(e) => setPendingFile(e.target.files[0])}
        />
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message or paste a complaint..."
        />
        <button className="send-btn" onClick={handleSend} title="Send Message">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
        </button>
      </div>
      <p className="powered-by">POWERED BY LANGGRAPH</p>
    </div>
  );
}
