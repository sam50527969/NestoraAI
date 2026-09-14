import {
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import { askCEO } from "../../../../api";
import CEOChat from "../CEOChat";

vi.mock("../../../../api", () => ({
  askCEO: vi.fn(),
}));

let recognitionInstance;

class MockSpeechRecognition {
  constructor() {
    this.lang = "";
    this.continuous = false;
    this.interimResults = false;
    this.onstart = null;
    this.onresult = null;
    this.onerror = null;
    this.onend = null;

    recognitionInstance = this;
  }

  start() {
    this.onstart?.();
  }

  abort() {
    this.onend?.();
  }
}

function installSpeechRecognition() {
  window.SpeechRecognition =
    MockSpeechRecognition;
}

function removeSpeechRecognition() {
  delete window.SpeechRecognition;
  delete window.webkitSpeechRecognition;
}

function emitTranscript(transcript) {
  recognitionInstance.onresult?.({
    results: [
      [
        {
          transcript,
        },
      ],
    ],
  });

  recognitionInstance.onend?.();
}

let spokenUtterance;

class MockSpeechSynthesisUtterance {
  constructor(text) {
    this.text = text;
    this.lang = "";
    this.onstart = null;
    this.onend = null;
    this.onerror = null;
  }
}

const mockSpeechSynthesis = {
  speak: vi.fn((utterance) => {
    spokenUtterance = utterance;
    utterance.onstart?.();
  }),
  cancel: vi.fn(),
};

function installSpeechSynthesis() {
  window.SpeechSynthesisUtterance =
    MockSpeechSynthesisUtterance;

  Object.defineProperty(
    window,
    "speechSynthesis",
    {
      configurable: true,
      value: mockSpeechSynthesis,
    },
  );
}

function removeSpeechSynthesis() {
  delete window.SpeechSynthesisUtterance;
  delete window.speechSynthesis;
}
beforeEach(() => {
  recognitionInstance = null;
  spokenUtterance = null;
  askCEO.mockReset();
  mockSpeechSynthesis.speak.mockClear();
  mockSpeechSynthesis.cancel.mockClear();
  removeSpeechRecognition();
  removeSpeechSynthesis();
});

afterEach(() => {
  removeSpeechRecognition();
  removeSpeechSynthesis();
  vi.clearAllMocks();
});

describe("CEOChat voice input", () => {
  it("keeps typed CEO chat available when speech recognition is unsupported", () => {
    render(<CEOChat />);

    expect(
      screen.queryByRole("button", {
        name: "Start voice input",
      }),
    ).not.toBeInTheDocument();

    expect(
      screen.getByRole("button", {
        name: "Ask CEO",
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("textbox"),
    ).toBeInTheDocument();
  });

  it("places recognized speech in the question without automatically sending it", async () => {
    installSpeechRecognition();

    render(<CEOChat />);

    fireEvent.click(
      screen.getByRole("button", {
        name: "Start voice input",
      }),
    );

    expect(
      screen.getByRole("status"),
    ).toHaveTextContent("Listening");

    emitTranscript(
      "What is my highest priority lead?",
    );

    await waitFor(() => {
      expect(
        screen.getByRole("textbox"),
      ).toHaveValue(
        "What is my highest priority lead?",
      );
    });

    expect(
      askCEO,
    ).not.toHaveBeenCalled();
  });

  it("submits recognized speech only after explicit Ask CEO action", async () => {
    installSpeechRecognition();

    askCEO.mockResolvedValue({
      answer: "Savant Coffee Shop is the current priority.",
    });

    render(<CEOChat />);

    fireEvent.click(
      screen.getByRole("button", {
        name: "Start voice input",
      }),
    );

    emitTranscript(
      "What is my highest priority lead?",
    );

    await waitFor(() => {
      expect(
        screen.getByRole("textbox"),
      ).toHaveValue(
        "What is my highest priority lead?",
      );
    });

    expect(
      askCEO,
    ).not.toHaveBeenCalled();

    fireEvent.click(
      screen.getByRole("button", {
        name: "Ask CEO",
      }),
    );

    await waitFor(() => {
      expect(
        askCEO,
      ).toHaveBeenCalledTimes(1);
    });

    expect(
      askCEO,
    ).toHaveBeenCalledWith(
      "What is my highest priority lead?",
    );

    expect(
      await screen.findByText(
        "Savant Coffee Shop is the current priority.",
      ),
    ).toBeInTheDocument();
  });

  it("preserves existing typed text when voice transcription is added", async () => {
    installSpeechRecognition();

    render(<CEOChat />);

    fireEvent.change(
      screen.getByRole("textbox"),
      {
        target: {
          value: "Review",
        },
      },
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Start voice input",
      }),
    );

    emitTranscript("my CRM pipeline");

    await waitFor(() => {
      expect(
        screen.getByRole("textbox"),
      ).toHaveValue(
        "Review my CRM pipeline",
      );
    });

    expect(
      askCEO,
    ).not.toHaveBeenCalled();
  });

  it("shows a safe fallback message when speech recognition fails", async () => {
    installSpeechRecognition();

    render(<CEOChat />);

    fireEvent.click(
      screen.getByRole("button", {
        name: "Start voice input",
      }),
    );

    recognitionInstance.onerror?.({
      error: "not-allowed",
    });

    recognitionInstance.onend?.();

    expect(
      await screen.findByText(
        "Voice input was not available. You can continue typing your question.",
      ),
    ).toBeInTheDocument();

    expect(
      askCEO,
    ).not.toHaveBeenCalled();
  });

  it("does not speak a CEO response automatically", async () => {
    installSpeechSynthesis();

    askCEO.mockResolvedValue({
      answer: "Review the Savant opportunity today.",
    });

    render(<CEOChat />);

    fireEvent.change(
      screen.getByRole("textbox"),
      {
        target: {
          value: "What should I do next?",
        },
      },
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Ask CEO",
      }),
    );

    expect(
      await screen.findByText(
        "Review the Savant opportunity today.",
      ),
    ).toBeInTheDocument();

    expect(
      mockSpeechSynthesis.speak,
    ).not.toHaveBeenCalled();

    expect(
      screen.getByRole("button", {
        name: "Speak CEO response",
      }),
    ).toBeInTheDocument();
  });

  it("speaks the displayed CEO response only after explicit user action", async () => {
    installSpeechSynthesis();

    askCEO.mockResolvedValue({
      answer: "Contact the highest priority lead.",
    });

    render(<CEOChat />);

    fireEvent.change(
      screen.getByRole("textbox"),
      {
        target: {
          value: "What is my priority?",
        },
      },
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Ask CEO",
      }),
    );

    await screen.findByText(
      "Contact the highest priority lead.",
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Speak CEO response",
      }),
    );

    expect(
      mockSpeechSynthesis.speak,
    ).toHaveBeenCalledTimes(1);

    expect(
      spokenUtterance.text,
    ).toBe(
      "Contact the highest priority lead.",
    );

    expect(
      screen.getByRole("button", {
        name: "Stop speaking CEO response",
      }),
    ).toBeInTheDocument();
  });

  it("cancels spoken output when the user presses Stop", async () => {
    installSpeechSynthesis();

    askCEO.mockResolvedValue({
      answer: "Follow up with the lead.",
    });

    render(<CEOChat />);

    fireEvent.change(
      screen.getByRole("textbox"),
      {
        target: {
          value: "Give me the next action.",
        },
      },
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Ask CEO",
      }),
    );

    await screen.findByText(
      "Follow up with the lead.",
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Speak CEO response",
      }),
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Stop speaking CEO response",
      }),
    );

    expect(
      mockSpeechSynthesis.cancel,
    ).toHaveBeenCalledTimes(1);

    expect(
      screen.getByRole("button", {
        name: "Speak CEO response",
      }),
    ).toBeInTheDocument();
  });

  it("keeps the CEO text response usable when speech output is unsupported", async () => {
    askCEO.mockResolvedValue({
      answer: "The text response remains available.",
    });

    render(<CEOChat />);

    fireEvent.change(
      screen.getByRole("textbox"),
      {
        target: {
          value: "Show my recommendation.",
        },
      },
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Ask CEO",
      }),
    );

    expect(
      await screen.findByText(
        "The text response remains available.",
      ),
    ).toBeInTheDocument();

    expect(
      screen.queryByRole("button", {
        name: "Speak CEO response",
      }),
    ).not.toBeInTheDocument();
  });

  it("does not show a failure message when speech is interrupted", async () => {
    installSpeechSynthesis();

    askCEO.mockResolvedValue({
      answer: "Review your CRM pipeline.",
    });

    render(<CEOChat />);

    fireEvent.change(
      screen.getByRole("textbox"),
      {
        target: {
          value: "What should I review?",
        },
      },
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Ask CEO",
      }),
    );

    await screen.findByText(
      "Review your CRM pipeline.",
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Speak CEO response",
      }),
    );

    spokenUtterance.onerror?.({
      error: "interrupted",
    });

    await waitFor(() => {
      expect(
        screen.queryByText(
          "Spoken response was not available. The CEO response is still shown below.",
        ),
      ).not.toBeInTheDocument();
    });

    expect(
      screen.getByRole("button", {
        name: "Speak CEO response",
      }),
    ).toBeInTheDocument();
  });

  it("still reports a genuine speech synthesis failure", async () => {
    installSpeechSynthesis();

    askCEO.mockResolvedValue({
      answer: "Review the highest priority opportunity.",
    });

    render(<CEOChat />);

    fireEvent.change(
      screen.getByRole("textbox"),
      {
        target: {
          value: "What is my priority?",
        },
      },
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Ask CEO",
      }),
    );

    await screen.findByText(
      "Review the highest priority opportunity.",
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Speak CEO response",
      }),
    );

    spokenUtterance.onerror?.({
      error: "synthesis-failed",
    });

    expect(
      await screen.findByText(
        "Spoken response was not available. The CEO response is still shown below.",
      ),
    ).toBeInTheDocument();
  });
});
