import ComplaintForm from "./components/ComplaintForm";
import CopilotChat from "./components/CopilotChat";
import "./App.css";

export default function App() {
  return (
    <div className="app-layout">
      <ComplaintForm />
      <CopilotChat />
    </div>
  );
}
