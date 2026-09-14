import { useEffect, useRef, useState } from "react";
import { askCEO } from "../../../api";

export default function CEOChat() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const recognitionRef = useRef(null);
  const speechUtteranceRef = useRef(null);

  const SpeechRecognition =
    typeof window !== "undefined"
      ? window.SpeechRecognition || window.webkitSpeechRecognition
      : null;

  const voiceSupported = Boolean(SpeechRecognition);

  const speechOutputSupported =
    typeof window !== "undefined" &&
    "speechSynthesis" in window &&
    typeof window.SpeechSynthesisUtterance === "function";

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
        recognitionRef.current = null;
      }

      if (
        typeof window !== "undefined" &&
        "speechSynthesis" in window
      ) {
        window.speechSynthesis.cancel();
      }

      speechUtteranceRef.current = null;
    };
  }, []);

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

  function handleVoiceInput() {
    if (!SpeechRecognition || isListening) {
      return;
    }

    setErrorMessage("");

    const recognition = new SpeechRecognition();

    recognition.lang =
      typeof navigator !== "undefined" && navigator.language
        ? navigator.language
        : "en-US";

    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      const transcript = event.results?.[0]?.[0]?.transcript?.trim();

      if (transcript) {
        setQuestion((currentQuestion) => {
          const existing = currentQuestion.trim();

          return existing
            ? `${existing} ${transcript}`
            : transcript;
        });
      }
    };

    recognition.onerror = (event) => {
      if (event.error !== "aborted") {
        setErrorMessage(
          "Voice input was not available. You can continue typing your question.",
        );
      }
    };

    recognition.onend = () => {
      setIsListening(false);
      recognitionRef.current = null;
    };

    recognitionRef.current = recognition;

    try {
      recognition.start();
    } catch (error) {
      console.error("Voice recognition failed to start", error);
      recognitionRef.current = null;
      setIsListening(false);
      setErrorMessage(
        "Voice input was not available. You can continue typing your question.",
      );
    }
  }

  function handleSpeakResponse() {
    if (!speechOutputSupported || !answer) {
      return;
    }

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      speechUtteranceRef.current = null;
      setIsSpeaking(false);
      return;
    }

    const utterance =
      new window.SpeechSynthesisUtterance(answer);

    utterance.lang =
      typeof navigator !== "undefined" && navigator.language
        ? navigator.language
        : "en-US";

    utterance.onstart = () => {
      setIsSpeaking(true);
    };

    utterance.onend = () => {
      speechUtteranceRef.current = null;
      setIsSpeaking(false);
    };

    utterance.onerror = (event) => {
      speechUtteranceRef.current = null;
      setIsSpeaking(false);

      const benignSpeechErrors = new Set([
        "canceled",
        "interrupted",
      ]);

      if (!benignSpeechErrors.has(event.error)) {
        setErrorMessage(
          "Spoken response was not available. The CEO response is still shown below.",
        );
      }
    };

    speechUtteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  }
  return (
    <section className="ceo-chat-panel">
      <div className="ceo-chat-header">
        <div>
          <p className="eyebrow">AI CEO</p>
          <h2>Executive Console</h2>
          <p>Ask questions about your CRM, priorities, and opportunities.</p>
        </div>

        <span className="ceo-chat-icon" aria-hidden="true">AI</span>
      </div>

      <form className="ceo-chat-form" onSubmit={handleSubmit}>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Try: Show me my highest scoring leads"
          rows={4}
        />

        <div className="ceo-chat-actions">
          <button type="submit" disabled={isLoading}>
            {isLoading ? "Thinking..." : "Ask CEO"}
          </button>

          {voiceSupported && (
            <button
              type="button"
              className="ceo-chat-voice-button"
              onClick={handleVoiceInput}
              disabled={isListening || isLoading}
              aria-label={
                isListening
                  ? "Listening for voice input"
                  : "Start voice input"
              }
            >
              {isListening ? "Listening..." : "🎤 Voice"}
            </button>
          )}
        </div>

        {isListening && (
          <p className="ceo-chat-voice-status" role="status">
            Listening... Speak your question, then review the transcript before sending.
          </p>
        )}
      </form>

      {errorMessage && (
        <div className="ceo-chat-error">
          {errorMessage}
        </div>
      )}

      {answer && (
        <div className="ceo-chat-answer">
          <div className="ceo-chat-answer-header">
            <p className="eyebrow">CEO Response</p>

            {speechOutputSupported && (
              <button
                type="button"
                className="ceo-chat-speak-button"
                onClick={handleSpeakResponse}
                aria-label={
                  isSpeaking
                    ? "Stop speaking CEO response"
                    : "Speak CEO response"
                }
              >
                {isSpeaking ? "■ Stop" : "🔊 Speak"}
              </button>
            )}
          </div>

          <p>{answer}</p>
        </div>
      )}
    </section>
  );
}
