"use client";

import { useEffect, useState, type FormEvent } from "react";
import { authFetch } from "@/lib/auth";

interface Doc {
  id: number;
  filename: string;
}

interface Message {
  id: number;
  role: string;
  content: string;
}

interface ChatResponse {
  conversation_id: number;
  user_message: Message;
  ai_response: Message;
}

export default function ChatPage() {
  const [docs, setDocs] = useState<Doc[]>([]);
  const [docId, setDocId] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [input, setInput] = useState("");
  const [error, setError] = useState("");
  const [sending, setSending] = useState(false);

  // Load the user's documents so they can pick which one to chat about.
  useEffect(() => {
    authFetch("/documents").then(async (res) => {
      if (res.ok) {
        const data = await res.json();
        setDocs(data);
        if (data.length > 0) setDocId(String(data[0].id));
      }
    });
  }, []);

  const sendMessage = async (e: FormEvent) => {
    e.preventDefault();
    if (!docId || !input.trim()) return;
    setError("");
    setSending(true);
    try {
      const res = await authFetch("/chat", {
        method: "POST",
        body: JSON.stringify({
          message: input,
          document_id: Number(docId),
          // Continue the same conversation once one exists
          ...(conversationId ? { conversation_id: conversationId } : {}),
        }),
      });
      if (!res.ok) {
        setError((await res.json()).detail ?? "Chat failed");
        return;
      }
      const data: ChatResponse = await res.json();
      setConversationId(data.conversation_id);
      setMessages((prev) => [...prev, data.user_message, data.ai_response]);
      setInput("");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="flex flex-col items-center w-full pt-10">
      <h1 className="text-2xl font-bold w-full max-w-2xl">Chat</h1>

      <div className="w-full max-w-2xl mt-4">
        <label className="text-sm text-gray-600">Document:</label>
        <select
          value={docId}
          onChange={(e) => {
            setDocId(e.target.value);
            setMessages([]);
            setConversationId(null);
          }}
          className="ml-2 border border-gray-300 rounded-md p-1"
        >
          {docs.length === 0 && <option value="">No documents - upload one first</option>}
          {docs.map((doc) => (
            <option key={doc.id} value={doc.id}>
              {doc.filename}
            </option>
          ))}
        </select>
      </div>

      <div className="w-full max-w-2xl mt-4 flex flex-col gap-2 border border-gray-200 rounded-lg p-4 min-h-64">
        {messages.length === 0 && (
          <p className="text-gray-500">
            Ask a question about your selected document.
          </p>
        )}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`max-w-[80%] rounded-lg p-3 whitespace-pre-wrap ${
              msg.role === "user"
                ? "self-end bg-blue-600 text-white"
                : "self-start bg-gray-100 text-gray-800"
            }`}
          >
            {msg.content}
          </div>
        ))}
      </div>

      <form
        onSubmit={sendMessage}
        className="w-full max-w-2xl mt-4 flex gap-2"
      >
        <input
          type="text"
          placeholder="Message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={!docId}
          className="flex-1 border border-gray-300 rounded-lg p-2"
        />
        <button
          type="submit"
          disabled={!docId || sending}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg transition-colors"
        >
          {sending ? "..." : "Send"}
        </button>
      </form>
      {error && <p className="mt-2 text-red-600 text-sm">{error}</p>}
    </div>
  );
}
