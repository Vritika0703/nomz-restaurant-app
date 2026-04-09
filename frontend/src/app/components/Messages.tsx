import { useCallback, useEffect, useState } from "react";
import { Footer } from "./Footer";
import { apiFetch } from "../api";

type ConvRow = {
  id: number;
  restaurant_id: number;
  restaurant_name: string;
  diner_username: string;
  updated_at: string;
  last_message: { body: string; created_at: string } | null;
};

type ChatMessage = {
  id: number;
  sender_id: number;
  sender_username: string;
  body: string;
  created_at: string;
};

export function Messages({
  onNavigateMap,
  onNavigateHome,
  onNavigateProfile,
  onLogout,
  accountType = "Diner",
}: {
  onNavigateMap: () => void;
  onNavigateHome: () => void;
  onNavigateProfile: () => void;
  onLogout: () => void;
  accountType?: "Diner" | "Restaurant";
}) {
  const [conversations, setConversations] = useState<ConvRow[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [threadTitle, setThreadTitle] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [composer, setComposer] = useState("");
  const [myUserId, setMyUserId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loadingList, setLoadingList] = useState(true);

  const loadSession = useCallback(async () => {
    try {
      const r = await apiFetch("/api/auth/session/");
      const d = await r.json();
      if (d.authenticated && typeof d.user_id === "number") setMyUserId(d.user_id);
    } catch {
      /* ignore */
    }
  }, []);

  const loadConversations = useCallback(async () => {
    setLoadingList(true);
    setError(null);
    try {
      const r = await apiFetch("/api/messages/conversations/");
      if (!r.ok) {
        setError(`Could not load conversations (${r.status}).`);
        setConversations([]);
        return;
      }
      const data = await r.json();
      setConversations(data.results ?? []);
    } catch {
      setError("Network error loading messages.");
      setConversations([]);
    } finally {
      setLoadingList(false);
    }
  }, []);

  const loadThread = async (id: number) => {
    setError(null);
    try {
      const r = await apiFetch(`/api/messages/conversations/${id}/`);
      if (!r.ok) {
        setError(`Could not open conversation (${r.status}).`);
        return;
      }
      const data = await r.json();
      setThreadTitle(
        accountType === "Restaurant"
          ? `Diner: ${data.diner_username}`
          : data.restaurant_name
      );
      setMessages(data.messages ?? []);
    } catch {
      setError("Network error loading thread.");
    }
  };

  useEffect(() => {
    void loadSession();
    void loadConversations();
  }, [loadSession, loadConversations]);

  useEffect(() => {
    if (selectedId != null) void loadThread(selectedId);
  }, [selectedId, accountType]);

  const sendMessage = async () => {
    const body = composer.trim();
    if (!selectedId || !body) return;
    setError(null);
    try {
      const r = await apiFetch(`/api/messages/conversations/${selectedId}/send/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: body }),
      });
      if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        setError(typeof d.error === "string" ? d.error : "Could not send message.");
        return;
      }
      setComposer("");
      await loadThread(selectedId);
      await loadConversations();
    } catch {
      setError("Network error while sending.");
    }
  };

  return (
    <div className="size-full flex flex-col" style={{ backgroundColor: "#FFF9F5" }}>
      <nav className="w-full px-8 py-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-6">
          <button
            onClick={onNavigateHome}
            className="text-xl transition-all p-2 rounded-lg"
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "rgba(224, 110, 127, 0.1)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "transparent";
            }}
            style={{
              backgroundColor: "transparent",
              border: "none",
              cursor: "pointer",
              color: "#E06E7F",
              fontWeight: "normal",
            }}
            type="button"
          >
            ←
          </button>

          <h1 className="text-2xl" style={{ fontFamily: "Montserrat, sans-serif", color: "#E06E7F" }}>
            nomz
          </h1>
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={onNavigateMap}
            className="text-xl transition-all p-2 rounded-lg"
            style={{
              backgroundColor: "transparent",
              border: "none",
              cursor: "pointer",
              color: "#E06E7F",
            }}
            type="button"
          >
            🗺️
          </button>

          {accountType === "Diner" && (
            <button
              onClick={onNavigateProfile}
              className="text-xl transition-all p-2 rounded-lg"
              style={{
                backgroundColor: "transparent",
                border: "none",
                cursor: "pointer",
                color: "#E06E7F",
              }}
              type="button"
            >
              👤
            </button>
          )}

          <button
            onClick={onLogout}
            className="text-xl transition-all p-2 rounded-lg"
            style={{
              backgroundColor: "transparent",
              border: "none",
              cursor: "pointer",
              color: "#E06E7F",
            }}
            type="button"
          >
            →
          </button>
        </div>
      </nav>

      <main className="w-full py-6 px-6 flex-1 flex flex-col min-h-0">
        {error && (
          <p className="text-sm mb-2" style={{ fontFamily: "Montserrat, sans-serif", color: "#b91c1c" }}>
            {error}
          </p>
        )}
        <div className="flex-1 flex gap-4 min-h-0 max-w-6xl mx-auto w-full">
          <div
            className="w-72 shrink-0 rounded-lg overflow-y-auto flex flex-col"
            style={{ border: "2px solid rgba(224, 110, 127, 0.15)", backgroundColor: "white" }}
          >
            <div className="px-3 py-2 text-sm" style={{ backgroundColor: "#E06E7F", color: "white", fontFamily: "Montserrat, sans-serif" }}>
              Conversations
            </div>
            {loadingList ? (
              <p className="p-3 text-xs" style={{ color: "#999" }}>
                Loading…
              </p>
            ) : conversations.length === 0 ? (
              <p className="p-3 text-xs" style={{ fontFamily: "Montserrat, sans-serif", color: "#666" }}>
                No conversations yet.
              </p>
            ) : (
              conversations.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => setSelectedId(c.id)}
                  className="text-left px-3 py-3 border-b w-full"
                  style={{
                    fontFamily: "Montserrat, sans-serif",
                    borderColor: "rgba(224, 110, 127, 0.1)",
                    backgroundColor: selectedId === c.id ? "rgba(224, 110, 127, 0.08)" : "white",
                    cursor: "pointer",
                  }}
                >
                  <div className="text-xs font-medium" style={{ color: "#333" }}>
                    {accountType === "Restaurant" ? c.diner_username : c.restaurant_name}
                  </div>
                  <div className="text-xs mt-1 line-clamp-2" style={{ color: "#888" }}>
                    {c.last_message?.body ?? "—"}
                  </div>
                </button>
              ))
            )}
          </div>

          <div
            className="flex-1 flex flex-col rounded-lg min-h-0"
            style={{ border: "2px solid rgba(224, 110, 127, 0.15)", backgroundColor: "white" }}
          >
            <div className="px-4 py-3 shrink-0" style={{ borderBottom: "1px solid rgba(224, 110, 127, 0.15)" }}>
              <h2 className="text-sm m-0" style={{ fontFamily: "Montserrat, sans-serif", color: "#E06E7F" }}>
                {selectedId ? threadTitle || "Conversation" : "Select a conversation"}
              </h2>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {selectedId == null ? (
                <p className="text-sm" style={{ fontFamily: "Montserrat, sans-serif", color: "#666" }}>
                  Choose a thread on the left.
                </p>
              ) : (
                messages.map((m) => {
                  const mine = myUserId != null && m.sender_id === myUserId;
                  return (
                    <div key={m.id} className={`flex ${mine ? "justify-end" : "justify-start"}`}>
                      <div
                        className="max-w-[85%] px-3 py-2 rounded-lg text-xs"
                        style={{
                          backgroundColor: mine ? "rgba(224, 110, 127, 0.2)" : "rgba(0,0,0,0.05)",
                          fontFamily: "Montserrat, sans-serif",
                          color: "#333",
                        }}
                      >
                        <div style={{ color: "#888", fontSize: "10px", marginBottom: 4 }}>
                          {m.sender_username}
                        </div>
                        {m.body}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
            <div className="p-3 shrink-0 flex gap-2" style={{ borderTop: "1px solid rgba(224, 110, 127, 0.15)" }}>
              <input
                className="flex-1 px-3 py-2 rounded-lg text-sm border-2"
                style={{ borderColor: "rgba(224, 110, 127, 0.25)", fontFamily: "Montserrat, sans-serif" }}
                placeholder="Type a message…"
                value={composer}
                disabled={selectedId == null}
                onChange={(e) => setComposer(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), void sendMessage())}
              />
              <button
                type="button"
                disabled={selectedId == null || !composer.trim()}
                onClick={() => void sendMessage()}
                className="px-4 py-2 rounded-lg text-sm text-white"
                style={{
                  backgroundColor: selectedId == null || !composer.trim() ? "#ccc" : "#E06E7F",
                  border: "none",
                  fontFamily: "Montserrat, sans-serif",
                  cursor: selectedId == null || !composer.trim() ? "not-allowed" : "pointer",
                }}
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
