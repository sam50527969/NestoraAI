import { useState } from "react";
import { askCEO } from "../../../api";

export default function CEOChat() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      return;
    }

    setIsLoading(true);
    setErrorMessage("");

    try {
      const response = await askCEO(trimmedQuestion);
      setAnswer(response.answer || "No answer was returned.");
    } catch (error) {
      console.error("CEO Agent request failed", error);
      setErrorMessage("Unable to contact the CEO Agent.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="ceo-chat-panel">
      <div className="ceo-chat-header">
        <div>
          <p className="eyebrow">AI CEO</p>
          <h2>Executive Console</h2>
          <p>Ask questions about your CRM, priorities, and opportunities.</p>
        </div>

        <span className="ceo-chat-icon">🧠</span>
      </div>

      <form className="ceo-chat-form" onSubmit={handleSubmit}>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Try: Show me my highest scoring leads"
          rows={4}
        />

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Thinking..." : "Ask CEO"}
        </button>
      </form>

      {errorMessage && (
        <div className="ceo-chat-error">
          {errorMessage}
        </div>
      )}

      {answer && (
        <div className="ceo-chat-answer">
          <p className="eyebrow">CEO Response</p>
          <p>{answer}</p>
        </div>
      )}
    </section>
  );
}