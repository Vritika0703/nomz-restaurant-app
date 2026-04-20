import { useCallback, useEffect, useState } from "react";
import { Footer } from "./Footer";
import { apiFetch } from "../api";

/* ── Types ─────────────────────────────────────────── */

type ConvRow = {
  id: number;
  name: string;
  is_group: boolean;
  creator_id: number;
  participants: { id: number; username: string }[];
  unread_count: number;
  last_message: {
    body: string;
    sender_username: string;
    created_at: string;
  } | null;
  updated_at: string;
};

type ChatMessage = {
  id: number;
  sender_id: number;
  sender_username: string;
  body: string;
  restaurant_recommendation: { id: number; name: string; cuisine?: string } | null;
  is_read: boolean;
  created_at: string;
};

type SharedRestaurant = {
  id: number;
  restaurant_id: number;
  restaurant_name: string;
  added_by: string;
  created_at: string;
};

type OtherUser = { id: number; username: string };

/* ── Component ─────────────────────────────────────── */

export function FriendChat({
  onNavigateHome,
  onNavigateMap,
  onNavigateProfile,
  onNavigateMessages,
  onSelectRestaurant,
  onLogout,
}: {
  onNavigateHome: () => void;
  onNavigateMap: () => void;
  onNavigateProfile: () => void;
  onNavigateMessages: () => void;
  onSelectRestaurant: (id: number) => void;
  onLogout: () => void;
}) {
  /* ── State ── */
  const [conversations, setConversations] = useState<ConvRow[]>([]);
  const [otherUsers, setOtherUsers] = useState<OtherUser[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [threadTitle, setThreadTitle] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sharedRestaurants, setSharedRestaurants] = useState<SharedRestaurant[]>([]);
  const [composer, setComposer] = useState("");
  const [myUserId, setMyUserId] = useState<number | null>(null);
  const [activePoll, setActivePoll] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadingList, setLoadingList] = useState(true);
  const [searching, setSearching] = useState(false);

  /* Tools State */
  const [recommendSearch, setRecommendSearch] = useState("");
  const [recommendMessage, setRecommendMessage] = useState("");
  const [recommendResults, setRecommendResults] = useState<{ id: number; name: string }[]>([]);
  const [selectedRecommendId, setSelectedRecommendId] = useState<number | null>(null);
  const [togetherSearch, setTogetherSearch] = useState("");
  const [togetherResults, setTogetherResults] = useState<{ id: number; name: string }[]>([]);
  const [memberSearch, setMemberSearch] = useState("");
  const [memberResults, setMemberResults] = useState<{ id: number; username: string }[]>([]);

  /* New-conversation modal */
  const [newChatOpen, setNewChatOpen] = useState(false);
  const [newChatUsername, setNewChatUsername] = useState("");
  const [newChatSubmitting, setNewChatSubmitting] = useState(false);

  const [newChatSearch, setNewChatSearch] = useState("");
  const [newChatResults, setNewChatResults] = useState<{ id: number; username: string }[]>([]);

  /* Group-creation modal */
  const [groupModalOpen, setGroupModalOpen] = useState(false);
  const [groupName, setGroupName] = useState("");
  const [groupSelectedIds, setGroupSelectedIds] = useState<number[]>([]);
  const [groupSubmitting, setGroupSubmitting] = useState(false);
  const [groupError, setGroupError] = useState<string | null>(null);
  const [groupSearch, setGroupSearch] = useState("");
  const [groupSearchResults, setGroupSearchResults] = useState<{ id: number; username: string }[]>([]);

  /* Leave Group Modal */
  const [leaveModalOpen, setLeaveModalOpen] = useState(false);
  const [leaveNewAdminId, setLeaveNewAdminId] = useState<number | null>(null);
  const [leaveConfirmStep, setLeaveConfirmStep] = useState(false);

  /* ── Data loaders ── */

  const loadSession = useCallback(async () => {
    try {
      const r = await apiFetch("/api/auth/session/");
      const d = await r.json();
      if (d.authenticated && typeof d.user_id === "number") setMyUserId(d.user_id);
    } catch { /* ignore */ }
  }, []);

  const loadConversations = useCallback(async () => {
    setLoadingList(true);
    try {
      const r = await apiFetch("/api/friends-chat/");
      if (r.ok) {
        const data = await r.json();
        setConversations(data.conversations ?? []);
        setOtherUsers(data.other_users ?? []);
      }
    } catch { /* ignore */ }
    finally { setLoadingList(false); }
  }, []);

  const loadThread = async (id: number) => {
    try {
      const r = await apiFetch(`/api/friends-chat/${id}/`);
      if (r.ok) {
        const data = await r.json();
        const conv = data.conversation as ConvRow | undefined;
        if (conv) {
          const title = conv.is_group 
            ? (conv.name || "Group Chat") 
            : conv.participants.find(p => p.id !== myUserId)?.username || "Chat";
          setThreadTitle(title);
        }
        setMessages(data.messages ?? []);
        setSharedRestaurants(data.shared_restaurants ?? []);
      }
    } catch { /* ignore */ }
  };

  /* ── Effects ── */

  useEffect(() => {
    void loadSession();
    void loadConversations();
  }, [loadSession, loadConversations]);

  useEffect(() => {
    if (selectedId != null) {
      void loadThread(selectedId);
      setActivePoll(true);
    } else {
      setActivePoll(false);
    }
  }, [selectedId, myUserId]);

  const [totalUnread, setTotalUnread] = useState(0);

  /* Poll for global unread updates */
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const r = await apiFetch("/api/unread-counts/");
        if (r.ok && !cancelled) {
          const d = await r.json();
          setTotalUnread(d.total_unread || 0);
        }
      } catch {}
    })();

    const rInterval = setInterval(async () => {
      try {
        const r = await apiFetch("/api/unread-counts/");
        if (r.ok && !cancelled) {
          const d = await r.json();
          setTotalUnread(d.total_unread || 0);
        }
      } catch {}
    }, 10000);

    return () => {
      cancelled = true;
      clearInterval(rInterval);
    };
  }, []);

  /* Poll for updates */
  useEffect(() => {
    if (!activePoll || selectedId == null) return;
    const interval = setInterval(() => {
      void loadThread(selectedId);
      void loadConversations();
    }, 5000);
    return () => clearInterval(interval);
  }, [activePoll, selectedId, loadConversations]);

  /* ── Actions ── */

  const sendMessage = async () => {
    const body = composer.trim();
    if (!selectedId || !body) return;
    try {
      const r = await apiFetch(`/api/friends-chat/${selectedId}/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ body }),
      });
      if (r.ok) {
        setComposer("");
        await loadThread(selectedId);
        await loadConversations();
      }
    } catch { /* ignore */ }
  };

  const startNewChat = async () => {
    const username = newChatUsername.trim();
    if (!username) return;
    setNewChatSubmitting(true);
    try {
      const r = await apiFetch("/api/friends-chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username }),
      });
      if (r.ok) {
        const d = await r.json();
        setNewChatOpen(false);
        setNewChatUsername("");
        if (d.conversation?.id) setSelectedId(d.conversation.id);
        await loadConversations();
      }
    } catch { /* ignore */ }
    finally { setNewChatSubmitting(false); }
  };

  const createGroup = async () => {
    const name = groupName.trim();
    if (!name) return;
    setGroupSubmitting(true);
    try {
      const r = await apiFetch("/api/friends-chat/group/create/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, participant_ids: groupSelectedIds }),
      });
      if (r.ok) {
        const d = await r.json();
        setGroupModalOpen(false);
        setGroupName("");
        setGroupSelectedIds([]);
        setGroupError(null);
        if (d.conversation?.id) setSelectedId(d.conversation.id);
        await loadConversations();
      } else {
        const d = await r.json();
        setGroupError(d.error || d.detail || d.message || "Failed to create group.");
      }
    } catch {
      setGroupError("Network error.");
    } finally {
      setGroupSubmitting(false);
    }
  };

  const searchItems = async (q: string, type: 'recommend' | 'together' | 'member' | 'newchat' | 'groupchat') => {
    if (type === 'recommend') {
      setRecommendSearch(q);
      setSelectedRecommendId(null);
    }
    if (type === 'together') setTogetherSearch(q);
    if (type === 'member') setMemberSearch(q);
    if (type === 'newchat') setNewChatSearch(q);
    if (type === 'groupchat') setGroupSearch(q);

    if (q.length < 1) {
      if (type === 'recommend') setRecommendResults([]);
      if (type === 'together') setTogetherResults([]);
      if (type === 'member') setMemberResults([]);
      if (type === 'newchat') setNewChatResults([]);
      if (type === 'groupchat') setGroupSearchResults([]);
      return;
    }

    setSearching(true);
    try {
      const endpoint = ['member', 'newchat', 'groupchat'].includes(type) 
        ? `/api/friends-chat/search-users/?q=${encodeURIComponent(q)}` 
        : `/api/search/?q=${encodeURIComponent(q)}&limit=10`;
      const r = await apiFetch(endpoint);
      if (r.ok) {
        const d = await r.json();
        const results = d.results || d.users || [];
        if (type === 'recommend') setRecommendResults(results);
        if (type === 'together') setTogetherResults(results);
        if (type === 'member') setMemberResults(results);
        if (type === 'newchat') setNewChatResults(results);
        if (type === 'groupchat') setGroupSearchResults(results);
      }
    } catch { /* ignore */ }
    finally { setSearching(false); }
  };

  const sendRecommendation = async (rid: number) => {
    if (!selectedId) return;
    try {
      await apiFetch(`/api/friends-chat/${selectedId}/recommend/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ restaurant_id: rid, body: recommendMessage }),
      });
      setRecommendSearch("");
      setRecommendMessage("");
      setRecommendResults([]);
      setSelectedRecommendId(null);
      await loadThread(selectedId);
    } catch { /* ignore */ }
  };

  const toggleShared = async (restaurantId: number, isShared: boolean) => {
    if (!selectedId) return;
    try {
      await apiFetch(`/api/friends-chat/${selectedId}/toggle-shared/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ restaurant_id: restaurantId, action: isShared ? "remove" : "add" }),
      });
      setTogetherSearch("");
      setTogetherResults([]);
      await loadThread(selectedId);
    } catch { /* ignore */ }
  };

  const manageMember = async (userId: number, action: 'add' | 'remove') => {
    if (!selectedId) return;
    try {
      const r = await apiFetch(`/api/friends-chat/group/${selectedId}/manage/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, action }),
      });
      if (r.ok) {
        setMemberSearch("");
        setMemberResults([]);
        await loadThread(selectedId);
      }
    } catch { /* ignore */ }
  };

  const submitLeaveGroup = async () => {
    if (!selectedId) return;
    try {
      const body = (myUserId === selectedConv?.creator_id && leaveNewAdminId) 
        ? JSON.stringify({ new_admin_id: leaveNewAdminId }) 
        : undefined;

      const r = await apiFetch(`/api/friends-chat/group/${selectedId}/leave/`, {
        method: "POST",
        headers: body ? { "Content-Type": "application/json" } : undefined,
        body,
      });
      if (r.ok) {
        setSelectedId(null);
        setLeaveModalOpen(false);
        await loadConversations();
      } else {
        const d = await r.json().catch(() => ({}));
        setError(d.error || "Could not leave group.");
      }
    } catch { 
      setError("Network error while leaving group.");
    }
  };

  const toggleGroupUserDraft = (uid: number) => {
    setGroupSelectedIds((prev) =>
      prev.includes(uid) ? prev.filter((id) => id !== uid) : [...prev, uid]
    );
  };

  const selectedConv = conversations.find((c) => c.id === selectedId);

  return (
    <div className="size-full flex flex-col" style={{ backgroundColor: "#FFF9F5" }}>
      {/* ── Header ── */}
      <nav className="w-full px-8 py-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-6">
          <button
            onClick={onNavigateHome}
            className="text-xl transition-all p-2 rounded-lg"
            title="Home"
            onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = "rgba(224, 110, 127, 0.1)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = "transparent"; }}
            style={{ backgroundColor: "transparent", border: "none", cursor: "pointer", color: "#E06E7F", fontWeight: "normal" }}
            type="button"
          >
            ←
          </button>
          <h1 className="text-2xl" style={{ fontFamily: "Montserrat, sans-serif", color: "#E06E7F" }}>
            nomz
          </h1>
        </div>

        <div className="flex items-center gap-4">
          {/* Map Icon Restored */}
          <button
            onClick={onNavigateMap}
            className="text-xl transition-all p-2 rounded-lg"
            title="Map"
            onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = "rgba(224, 110, 127, 0.1)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = "transparent"; }}
            style={{ backgroundColor: "transparent", border: "none", cursor: "pointer", color: "#E06E7F" }}
            type="button"
          >
            🗺️
          </button>
          <button
            onClick={onNavigateMessages}
            className="text-xl transition-all p-2 rounded-lg"
            title="Restaurant Messages"
            onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = "rgba(224, 110, 127, 0.1)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = "transparent"; }}
            style={{ backgroundColor: "transparent", border: "none", cursor: "pointer", color: "#E06E7F" }}
            type="button"
          >
            💬
          </button>

          <button
            onClick={onNavigateProfile}
            className="text-xl transition-all p-2 rounded-lg"
            title="Profile"
            onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = "rgba(224, 110, 127, 0.1)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = "transparent"; }}
            style={{ backgroundColor: "transparent", border: "none", cursor: "pointer", color: "#E06E7F" }}
            type="button"
          >
            👤
          </button>
          <button
            onClick={onLogout}
            className="text-xl transition-all p-2 rounded-lg"
            title="Logout"
            onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = "rgba(224, 110, 127, 0.1)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = "transparent"; }}
            style={{ backgroundColor: "transparent", border: "none", cursor: "pointer", color: "#E06E7F" }}
            type="button"
          >
            →
          </button>
        </div>
      </nav>

      {/* ── Main Area ── */}
      <main className="w-full py-6 px-6 flex-1 flex flex-col min-h-0 relative">
        
        {error && <p className="text-sm mb-2" style={{ fontFamily: "Montserrat, sans-serif", color: "#b91c1c" }}>{error}</p>}

        <div className="flex-1 flex gap-4 min-h-0 max-w-6xl mx-auto w-full">
          
          {/* LEFT: Conversations */}
          <div
            className="w-72 shrink-0 rounded-lg overflow-y-auto flex flex-col"
            style={{ border: "2px solid rgba(224, 110, 127, 0.15)", backgroundColor: "white" }}
          >
            <div
              className="px-3 py-2 text-sm flex items-center justify-between"
              style={{ backgroundColor: "#E06E7F", color: "white", fontFamily: "Montserrat, sans-serif" }}
            >
              <span>Conversations</span>
              <div className="flex gap-2">
                <button onClick={() => setGroupModalOpen(true)} className="text-white bg-transparent border-none cursor-pointer" title="New Group">👥</button>
                <button onClick={() => setNewChatOpen(true)} className="text-white bg-transparent border-none cursor-pointer" title="New Chat">+</button>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto">
                {loadingList ? (
                <p className="p-3 text-xs" style={{ color: "#999" }}>Loading…</p>
                ) : conversations.length === 0 ? (
                <p className="p-3 text-xs" style={{ fontFamily: "Montserrat, sans-serif", color: "#666" }}>No conversations yet.</p>
                ) : (
                conversations.map((c) => {
                    const label = c.is_group ? (c.name || "Group") : c.participants.find(p => p.id !== myUserId)?.username || "Chat";
                    return (
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
                        <div className="flex items-center justify-between">
                            <div className="text-xs font-medium" style={{ color: "#333" }}>{label}</div>
                            {c.unread_count > 0 && (
                                <span className="text-[10px] px-1.5 py-0.5 rounded-full text-white" style={{ backgroundColor: "#E06E7F" }}>{c.unread_count}</span>
                            )}
                        </div>
                        <div className="text-xs mt-1 line-clamp-1 truncate" style={{ color: "#888" }}>
                            {c.last_message ? `${c.last_message.sender_username}: ${c.last_message.body}` : "—"}
                        </div>
                    </button>
                    );
                })
                )}
            </div>
          </div>

          {/* MIDDLE: Chat Window */}
          <div className="flex-1 flex flex-col rounded-lg min-h-0" style={{ border: "2px solid rgba(224, 110, 127, 0.15)", backgroundColor: "white" }}>
            {!selectedId ? (
                <div className="flex-1 flex flex-col items-center justify-center p-10 text-center">
                    <div className="text-4xl mb-4">👋</div>
                    <h2 className="text-base font-bold text-[#E06E7F] mb-1" style={{ fontFamily: "Montserrat, sans-serif" }}>Connect with your friends!</h2>
                    <p className="text-xs text-gray-400 max-w-sm mb-6" style={{ fontFamily: "Montserrat, sans-serif" }}>
                        Share restaurant recommendations and build your Together List. Choose an action from the sidebar to start.
                    </p>
                    <div className="flex gap-4 text-[10px] text-gray-300">
                        <span>Click <span className="text-[#E06E7F]">+</span> for New Chat</span>
                        <span>Click <span className="text-[#E06E7F]">👥</span> for Group Chat</span>
                    </div>
                </div>
            ) : (
              <>
                <div className="px-4 py-3 shrink-0 border-b" style={{ borderColor: "rgba(224, 110, 127, 0.15)" }}>
                  <h2 className="text-sm m-0 font-semibold" style={{ fontFamily: "Montserrat, sans-serif", color: "#E06E7F" }}>
                    {threadTitle}
                  </h2>
                </div>
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.map((m) => {
                    const mine = myUserId != null && m.sender_id === myUserId;
                    return (
                      <div key={m.id} className={`flex flex-col ${mine ? "items-end" : "items-start"}`}>
                        {!mine && <div style={{ color: "#888", fontSize: "10px", marginBottom: 2, marginLeft: 4 }}>{m.sender_username}</div>}
                        <div
                          className="max-w-[85%] px-3 py-2 rounded-lg text-xs shadow-sm"
                          style={{
                            backgroundColor: mine ? "rgba(224, 110, 127, 0.15)" : "#f3f4f6",
                            fontFamily: "Montserrat, sans-serif",
                            color: "#333",
                            borderRadius: mine ? "12px 12px 0 12px" : "12px 12px 12px 0"
                          }}
                        >
                          {m.restaurant_recommendation && (
                            <div className="w-48 py-1 border-b mb-2" style={{ borderColor: "rgba(0,0,0,0.05)" }}>
                                <div className="text-[9px] font-bold text-[#E06E7F] flex items-center mb-1">⭐ Recommended</div>
                                <div className="font-bold text-gray-800 mb-0.5">{m.restaurant_recommendation.name}</div>
                                <div className="text-[10px] text-gray-400 mb-3">{m.restaurant_recommendation.cuisine || "other"}</div>
                                <div className="flex gap-2">
                                    <button onClick={() => onSelectRestaurant(m.restaurant_recommendation!.id)} className="flex-1 py-1 text-[10px] bg-[#E06E7F] text-white rounded font-bold border-none cursor-pointer">View</button>
                                    <button 
                                        onClick={() => toggleShared(m.restaurant_recommendation!.id, sharedRestaurants.some(s => s.restaurant_id === m.restaurant_recommendation!.id))}
                                        className="flex-1 py-1 text-[10px] border border-gray-200 text-gray-600 rounded font-bold bg-white cursor-pointer"
                                    >
                                        {sharedRestaurants.some(s => s.restaurant_id === m.restaurant_recommendation!.id) ? "Untogether" : "Together"}
                                    </button>
                                </div>
                            </div>
                          )}
                          <div className="leading-relaxed">{m.body}</div>
                        </div>
                      </div>
                    );
                  })}
                </div>
                {/* Input area */}
                <div className="p-3 shrink-0 flex gap-2 border-t" style={{ borderColor: "rgba(224, 110, 127, 0.15)" }}>
                  <input
                    className="flex-1 px-3 py-2 rounded-lg text-sm border-2 bg-gray-50"
                    style={{ borderColor: "transparent", fontFamily: "Montserrat, sans-serif", outline: "none" }}
                    placeholder="Type a message…"
                    value={composer}
                    onChange={(e) => setComposer(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), void sendMessage())}
                  />
                  <button
                    type="button"
                    disabled={!composer.trim()}
                    onClick={() => void sendMessage()}
                    className="px-4 py-2 rounded-lg text-sm text-white font-bold transition-transform active:scale-95"
                    style={{
                      backgroundColor: !composer.trim() ? "#ccc" : "#E06E7F",
                      border: "none",
                      fontFamily: "Montserrat, sans-serif",
                      cursor: !composer.trim() ? "not-allowed" : "pointer",
                    }}
                  >
                    Send
                  </button>
                </div>
              </>
            )}
          </div>

          {/* RIGHT: Tools Sidebar */}
          <div className="w-64 flex flex-col gap-4 overflow-y-auto">
            
            {/* Recommend Restaurant */}
            <div className="bg-white rounded-lg border border-gray-100 shadow-sm" style={{ border: "2px solid rgba(224, 110, 127, 0.15)", position: "relative" }}>
              <div className="bg-[#E06E7F] text-white px-3 py-2 text-xs font-bold rounded-t-md" style={{ fontFamily: "Montserrat, sans-serif" }}>Recommend Restaurant</div>
              <div className="p-3 flex flex-col gap-2">
                {!selectedId ? (
                    <p className="text-[10px] text-center text-gray-400 py-4" style={{ fontFamily: "Montserrat, sans-serif" }}>Select a conversation to recommend a restaurant to a friend.</p>
                ) : (
                    <>
                        <div className="relative">
                            <input 
                                value={recommendSearch}
                                onChange={(e) => void searchItems(e.target.value, 'recommend')}
                                placeholder="Search..." 
                                className="w-full px-2 py-1.5 bg-gray-50 rounded text-[10px] border-none outline-none"
                                style={{ fontFamily: "Montserrat, sans-serif" }}
                            />
                            {recommendResults.length > 0 && (
                                <div className="absolute top-full left-0 w-full bg-white shadow-xl rounded border z-[100] max-h-40 overflow-y-auto">
                                    {recommendResults.map(r => (
                                        <button key={r.id} onClick={() => { setRecommendSearch(r.name); setSelectedRecommendId(r.id); setRecommendResults([]); }} className="w-full text-left p-2 text-[10px] hover:bg-gray-50 border-b last:border-none focus:bg-gray-100 outline-none">{r.name}</button>
                                    ))}
                                </div>
                            )}
                            {searching && recommendSearch.length >= 1 && recommendResults.length === 0 && (
                                <div className="absolute top-full left-0 w-full bg-white p-2 text-[9px] text-gray-400 italic border rounded shadow-sm z-[100]">Searching…</div>
                            )}
                        </div>
                        <input 
                            value={recommendMessage}
                            onChange={(e) => setRecommendMessage(e.target.value)}
                            placeholder="Optional message" 
                            className="w-full px-2 py-1.5 bg-gray-50 rounded text-[10px] border-none outline-none"
                            style={{ fontFamily: "Montserrat, sans-serif" }}
                        />
                        <button 
                            disabled={!selectedRecommendId}
                            onClick={() => {
                                if (selectedRecommendId) {
                                    sendRecommendation(selectedRecommendId);
                                }
                            }}
                            className="bg-[#E06E7F] text-white py-1.5 rounded text-[10px] font-bold border-none cursor-pointer disabled:opacity-50"
                            style={{ fontFamily: "Montserrat, sans-serif" }}
                        >
                            Send Recommendation
                        </button>
                    </>
                )}
              </div>
            </div>

            {/* Together List */}
            <div className="bg-white rounded-lg border border-gray-100 shadow-sm" style={{ border: "2px solid rgba(224, 110, 127, 0.15)", position: "relative" }}>
              <div className="bg-[#E06E7F] text-white px-3 py-2 text-xs font-bold rounded-t-md" style={{ fontFamily: "Montserrat, sans-serif" }}>Together List</div>
              <div className="p-3 flex flex-col gap-2">
                {!selectedId ? (
                    <p className="text-[10px] text-center text-gray-400 py-4" style={{ fontFamily: "Montserrat, sans-serif" }}>Select a conversation to view and manage your Together List.</p>
                ) : (
                    <>
                        {sharedRestaurants.length > 0 ? (
                            <div className="space-y-1.5 max-h-32 overflow-y-auto">
                                {sharedRestaurants.map(sr => (
                                    <div key={sr.id} className="flex items-center justify-between bg-gray-50 p-1.5 rounded">
                                        <span className="text-[9px] text-gray-700 font-medium truncate flex-1" style={{ fontFamily: "Montserrat, sans-serif" }}>{sr.restaurant_name}</span>
                                        <div className="flex gap-1 ml-1">
                                            <button onClick={() => onSelectRestaurant(sr.restaurant_id)} className="bg-[#E06E7F] text-white text-[8px] px-1 rounded border-none cursor-pointer">View</button>
                                            <button onClick={() => toggleShared(sr.restaurant_id, true)} className="text-gray-400 text-[9px] hover:text-red-500 bg-transparent border-none cursor-pointer">✕</button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-[9px] text-center text-gray-400 py-1" style={{ fontFamily: "Montserrat, sans-serif" }}>No shared restaurants.</p>
                        )}
                        <div className="text-[9px] font-bold text-[#E06E7F] mt-1">Add to List</div>
                        <div className="relative">
                            <input 
                                value={togetherSearch}
                                onChange={(e) => void searchItems(e.target.value, 'together')}
                                placeholder="Search and add..." 
                                className="w-full px-2 py-1.5 bg-gray-50 rounded text-[10px] border-none outline-none"
                                style={{ fontFamily: "Montserrat, sans-serif" }}
                            />
                            {togetherResults.length > 0 && (
                                <div className="absolute top-full left-0 w-full bg-white shadow-xl rounded border z-[100] max-h-40 overflow-y-auto">
                                    {togetherResults.map(r => (
                                        <button key={r.id} onClick={() => { toggleShared(r.id, false); setTogetherSearch(""); setTogetherResults([]); }} className="w-full text-left p-2 text-[10px] hover:bg-gray-50 border-b last:border-none focus:bg-gray-100 outline-none">{r.name}</button>
                                    ))}
                                </div>
                            )}
                            {searching && togetherSearch.length >= 1 && togetherResults.length === 0 && (
                                <div className="absolute top-full left-0 w-full bg-white p-2 text-[9px] text-gray-400 italic border rounded shadow-sm z-[100]">Searching…</div>
                            )}
                        </div>
                    </>
                )}
              </div>
            </div>

            {selectedConv?.is_group && (
                <div className="bg-white rounded-lg border border-gray-100 shadow-sm" style={{ border: "2px solid rgba(224, 110, 127, 0.15)" }}>
                    <div className="bg-[#E06E7F] text-white px-3 py-2 text-xs font-bold" style={{ fontFamily: "Montserrat, sans-serif" }}>Members</div>
                    <div className="p-3 flex flex-col gap-2">
                        <div className="flex flex-wrap gap-1">
                            {selectedConv.participants.map(p => (
                                <div key={p.id} className="bg-gray-50 px-1.5 py-0.5 rounded flex items-center gap-1 border border-gray-100">
                                    <span className="text-[9px] text-gray-600" style={{ fontFamily: "Montserrat, sans-serif" }}>{p.username} {p.id === selectedConv.creator_id ? "👑" : ""}</span>
                                    {myUserId === selectedConv.creator_id && p.id !== myUserId && (
                                        <button onClick={() => manageMember(p.id, 'remove')} className="text-gray-400 text-[10px] hover:text-red-500 bg-transparent border-none cursor-pointer">✕</button>
                                    )}
                                </div>
                            ))}
                        </div>
                         {myUserId === selectedConv.creator_id && (
                            <>
                                <div className="text-[9px] font-bold text-[#E06E7F] mt-1">Add Member</div>
                                <div className="relative">
                                    <input 
                                        value={memberSearch}
                                        onChange={(e) => void searchItems(e.target.value, 'member')}
                                        placeholder="Username…" 
                                        className="w-full px-2 py-1.5 bg-gray-50 rounded text-[10px] border-none outline-none"
                                        style={{ fontFamily: "Montserrat, sans-serif" }}
                                    />
                                    {memberResults.length > 0 && (
                                        <div className="absolute top-full left-0 w-full bg-white shadow-xl rounded border z-[100] max-h-40 overflow-y-auto">
                                            {memberResults.map(u => {
                                                const isAdded = selectedConv.participants.some(p => p.id === u.id);
                                                return isAdded ? (
                                                    <div key={u.id} className="w-full text-left p-2 text-[10px] text-gray-400 bg-gray-50 border-b last:border-none cursor-not-allowed">
                                                        {u.username} <span className="opacity-50 italic float-right">Added</span>
                                                    </div>
                                                ) : (
                                                    <button key={u.id} onClick={() => manageMember(u.id, 'add')} className="w-full text-left p-2 text-[10px] hover:bg-gray-50 border-b last:border-none focus:bg-gray-100 outline-none cursor-pointer">{u.username}</button>
                                                );
                                            })}
                                        </div>
                                    )}
                                    {searching && memberSearch.length >= 1 && memberResults.length === 0 && (
                                        <div className="absolute top-full left-0 w-full bg-white p-2 text-[9px] text-gray-400 italic border rounded shadow-sm z-[100]">Searching…</div>
                                    )}
                                </div>
                            </>
                        )}
                        <div className="mt-1 pt-2 border-t" style={{ borderColor: 'rgba(224, 110, 127, 0.1)' }}>
                            <button onClick={() => { setLeaveModalOpen(true); setLeaveConfirmStep(false); setLeaveNewAdminId(null); }} className="w-full text-[#E06E7F] font-bold hover:bg-[#FFF2F4] py-1.5 rounded text-[10px] bg-transparent border border-[#E06E7F]/20 cursor-pointer transition-colors" style={{ fontFamily: "Montserrat, sans-serif" }}>Leave Group</button>
                        </div>
                    </div>
                </div>
            )}

          </div>

        </div>
      </main>

      {/* New Chat Modal */}
      {newChatOpen && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4">
            <div className="bg-white w-full max-w-sm rounded-xl p-6 shadow-2xl" style={{ border: "2px solid rgba(224, 110, 127, 0.2)" }}>
                <h3 className="text-base font-bold text-[#E06E7F] mb-1" style={{ fontFamily: "Montserrat, sans-serif" }}>Start a Chat</h3>
                <p className="text-xs text-gray-400 mb-6" style={{ fontFamily: "Montserrat, sans-serif" }}>Choose a friend to start a direct chat with.</p>
                
                <div className="relative mb-6">
                  <input 
                    value={newChatSearch}
                    onChange={(e) => {
                      setNewChatSearch(e.target.value);
                      if (newChatUsername) setNewChatUsername("");
                      void searchItems(e.target.value, 'newchat');
                    }}
                    placeholder="Search username…" 
                    className="w-full px-2 py-2 bg-gray-50 rounded border outline-none text-sm"
                    style={{ fontFamily: "Montserrat, sans-serif", borderColor: "rgba(224, 110, 127, 0.2)" }}
                  />
                  {newChatResults.length > 0 && !newChatUsername && (
                      <div className="absolute top-full mt-1 left-0 w-full bg-white shadow-xl rounded border z-10 max-h-40 overflow-y-auto">
                          {newChatResults.map(u => (
                              <button 
                                key={u.id} 
                                onClick={() => {
                                  setNewChatUsername(u.username);
                                  setNewChatSearch(u.username);
                                  setNewChatResults([]);
                                }} 
                                className="w-full text-left p-2 text-sm hover:bg-gray-50 border-b last:border-none cursor-pointer"
                              >
                                {u.username}
                              </button>
                          ))}
                      </div>
                  )}
                  {searching && newChatSearch.length >= 1 && newChatResults.length === 0 && (
                      <div className="absolute top-full mt-1 left-0 w-full bg-white p-2 text-sm text-gray-400 italic border rounded shadow-sm z-10">Searching…</div>
                  )}
                </div>

                <div className="flex gap-2">
                    <button onClick={() => setNewChatOpen(false)} className="flex-1 py-2 text-sm font-bold text-[#E06E7F] bg-[#FFF2F4] rounded-lg border-none cursor-pointer transition-all hover:bg-opacity-80">Cancel</button>
                    <button onClick={startNewChat} disabled={!newChatUsername || newChatSubmitting} className="flex-1 py-2 text-sm font-bold text-white bg-[#E06E7F] rounded-lg border-none cursor-pointer disabled:opacity-50 transition-all hover:opacity-90">Start</button>
                </div>
            </div>
        </div>
      )}

      {/* Group Chat Modal */}
      {groupModalOpen && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4">
            <div className="bg-white w-full max-w-sm rounded-xl p-6 shadow-2xl" style={{ border: "2px solid rgba(224, 110, 127, 0.2)" }}>
                <h3 className="text-base font-bold text-[#E06E7F] mb-1" style={{ fontFamily: "Montserrat, sans-serif" }}>Create Group Chat</h3>
                <p className="text-xs text-gray-400 mb-4" style={{ fontFamily: "Montserrat, sans-serif" }}>Invite at least 2 friends to start a group chat.</p>
                {groupError && <p className="text-[10px] text-red-500 mb-3 font-bold" style={{ fontFamily: "Montserrat, sans-serif" }}>{groupError}</p>}
                <input 
                    value={groupName}
                    onChange={(e) => setGroupName(e.target.value)}
                    placeholder="Group name" 
                    className="w-full p-2 bg-gray-50 border outline-none rounded-lg text-sm mb-4"
                    style={{ borderColor: "rgba(224, 110, 127, 0.2)" }}
                />
                <div className="text-[10px] font-bold text-gray-400 mb-2 uppercase" style={{ fontFamily: "Montserrat, sans-serif" }}>Select members:</div>
                <div className="relative mb-6">
                    <input 
                        value={groupSearch}
                        onChange={(e) => void searchItems(e.target.value, 'groupchat')}
                        placeholder="Search username…" 
                        className="w-full px-2 py-2 bg-gray-50 rounded border outline-none text-sm mb-2"
                        style={{ fontFamily: "Montserrat, sans-serif", borderColor: "rgba(224, 110, 127, 0.2)" }}
                    />
                    {groupSearchResults.length > 0 && (
                      <div className="absolute top-[42px] left-0 w-full bg-white shadow-xl rounded border z-10 max-h-40 overflow-y-auto">
                          {groupSearchResults.map(u => (
                              <button 
                                key={u.id} 
                                onClick={() => {
                                  toggleGroupUserDraft(u.id);
                                  setGroupSearch("");
                                  setGroupSearchResults([]);
                                }} 
                                className="w-full text-left p-2 text-sm hover:bg-gray-50 border-b last:border-none cursor-pointer"
                              >
                                {u.username}
                              </button>
                          ))}
                      </div>
                    )}
                    {groupSelectedIds.length > 0 && (
                      <div className="max-h-32 overflow-y-auto space-y-1 border rounded-lg p-2" style={{ borderColor: "rgba(224, 110, 127, 0.1)" }}>
                          {groupSelectedIds.map(uid => {
                              // We can look up username from memberResults, otherUsers, groupSearchResults
                              const u = otherUsers.find(ou => ou.id === uid) || groupSearchResults.find(ou => ou.id === uid) || memberResults.find(ou => ou.id === uid) || { id: uid, username: `User ${uid}` };
                              return (
                                  <div key={uid} className="flex justify-between items-center p-2 rounded text-[12px] bg-[#FFF2F4] text-[#E06E7F] font-bold" style={{ fontFamily: "Montserrat, sans-serif" }}>
                                      <span>{u.username}</span>
                                      <button onClick={() => toggleGroupUserDraft(uid)} className="bg-transparent border-none text-[#E06E7F] cursor-pointer" title="Remove">✕</button>
                                  </div>
                              )
                          })}
                      </div>
                    )}
                </div>
                <div className="flex gap-2">
                    <button onClick={() => setGroupModalOpen(false)} className="flex-1 py-2 text-sm font-bold text-[#E06E7F] bg-[#FFF2F4] rounded-lg border-none cursor-pointer transition-all hover:bg-opacity-80">Cancel</button>
                    <button onClick={createGroup} disabled={!groupName} className="flex-1 py-2 text-sm font-bold text-white bg-[#E06E7F] rounded-lg border-none cursor-pointer disabled:opacity-50 transition-all hover:opacity-90">Create</button>
                </div>
            </div>
        </div>
      )}

      {/* Leave Group Modal */}
      {leaveModalOpen && selectedConv && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4">
            <div className="bg-white w-full max-w-sm rounded-xl p-6 shadow-2xl" style={{ border: "2px solid rgba(224, 110, 127, 0.2)" }}>
                 {myUserId === selectedConv.creator_id && !leaveConfirmStep ? (
                     <>
                        <h3 className="text-base font-bold text-[#E06E7F] mb-1" style={{ fontFamily: "Montserrat, sans-serif" }}>Reassign Admin</h3>
                        <p className="text-xs text-gray-400 mb-4" style={{ fontFamily: "Montserrat, sans-serif" }}>You must assign a new admin before leaving the group.</p>
                        
                        <div className="flex flex-col gap-2 mb-4">
                            {selectedConv.participants.filter(p => p.id !== myUserId).map(p => (
                                <button 
                                    key={p.id}
                                    onClick={() => setLeaveNewAdminId(p.id)}
                                    className={`w-full text-left p-2 rounded text-sm ${leaveNewAdminId === p.id ? 'bg-[#FFF2F4] text-[#E06E7F] border-[#E06E7F]' : 'bg-gray-50 border-gray-200'} border cursor-pointer font-bold`}
                                >
                                    {p.username}
                                </button>
                            ))}
                            {selectedConv.participants.filter(p => p.id !== myUserId).length === 0 && (
                                <p className="text-xs text-red-500 italic">No other members to assign.</p>
                            )}
                        </div>

                        <div className="flex gap-2">
                           <button onClick={() => setLeaveModalOpen(false)} className="flex-1 py-2 text-sm font-bold text-[#E06E7F] bg-[#FFF2F4] rounded-lg border-none cursor-pointer transition-all hover:bg-opacity-80">Cancel</button>
                           <button onClick={() => setLeaveConfirmStep(true)} disabled={!leaveNewAdminId} className="flex-1 py-2 text-sm font-bold text-white bg-[#E06E7F] rounded-lg border-none cursor-pointer disabled:opacity-50 transition-all hover:opacity-90">Next</button>
                        </div>
                     </>
                 ) : (
                     <>
                        <h3 className="text-base font-bold text-[#E06E7F] mb-1" style={{ fontFamily: "Montserrat, sans-serif" }}>Leave Group</h3>
                        <p className="text-xs text-gray-800 mb-4 font-bold" style={{ fontFamily: "Montserrat, sans-serif" }}>Are you sure you want to leave this group?</p>
                        {myUserId === selectedConv.creator_id && leaveNewAdminId && (
                            <p className="text-xs text-gray-500 mb-4" style={{ fontFamily: "Montserrat, sans-serif" }}>This will automatically transfer ownership to the selected new admin.</p>
                        )}
                        <div className="flex gap-2">
                           <button onClick={() => setLeaveModalOpen(false)} className="flex-1 py-2 text-sm font-bold text-[#E06E7F] bg-[#FFF2F4] rounded-lg border-none cursor-pointer transition-all hover:bg-opacity-80">Don't Leave</button>
                           <button onClick={submitLeaveGroup} className="flex-1 py-2 text-sm font-bold text-white bg-[#E06E7F] rounded-lg border-none cursor-pointer transition-all hover:opacity-90">Leave</button>
                        </div>
                     </>
                 )}
            </div>
        </div>
      )}

      {/* Footer Restored to one version */}
      <Footer />
    </div>
  );
}
