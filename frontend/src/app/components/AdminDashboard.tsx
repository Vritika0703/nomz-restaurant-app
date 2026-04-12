import { useEffect, useState } from "react";
import { Footer } from "./Footer";
import { apiFetch } from "../api";

export function AdminDashboard({ 
  onLogout, 
  onNavigateMap,
  onViewModeration, 
  onViewPendingApprovals, 
  onViewPendingUsers,
  onViewLogs,
  onViewApprovedAccounts,
  onViewRejectedAccounts,
}: { 
  onLogout: () => void; 
  onNavigateMap: () => void;
  onViewModeration: () => void; 
  onViewPendingApprovals: () => void; 
  onViewPendingUsers: () => void;
  onViewLogs: () => void;
  onViewApprovedAccounts: () => void;
  onViewRejectedAccounts: () => void;
}) {
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalRestaurants: 0,
    pendingReports: 0,
    pendingApprovals: 0,
    suspiciousAccounts: 0,
    flaggedContent: 0,
  });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const r = await apiFetch("/api/admin/dashboard-summary/");
        if (!r.ok) return;
        const d = await r.json();
        if (cancelled) return;
        setStats({
          totalUsers: d.total_users ?? 0,
          totalRestaurants: d.total_restaurants ?? 0,
          pendingReports: d.pending_reports ?? 0,
          pendingApprovals: d.pending_approvals ?? 0,
          suspiciousAccounts: d.suspicious_accounts ?? 0,
          flaggedContent: d.flagged_content ?? 0,
        });
      } catch {
        /* keep zeros */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="size-full flex flex-col overflow-y-auto" style={{ backgroundColor: '#FFF9F5' }}>
      {/* Navigation Bar */}
      <nav className="w-full px-8 py-4 flex items-center justify-between">
        <h1 className="text-2xl" style={{
          fontFamily: 'Montserrat, sans-serif',
          color: '#E06E7F'
        }}>
          nomz Admin
        </h1>

        <div className="flex items-center gap-4">
          <button
            onClick={onNavigateMap}
            className="text-xl transition-all p-2 rounded-lg"
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.1)'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
            style={{
              backgroundColor: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: '#E06E7F'
            }}
          >
            🗺️
          </button>

          <button
            onClick={onLogout}
          className="text-xl transition-all p-2 rounded-lg"
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.1)'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          style={{
            backgroundColor: 'transparent',
            border: 'none',
            cursor: 'pointer',
            color: '#E06E7F',
            fontWeight: 'normal'
          }}
        >
          →
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="w-full py-12 px-8 flex-1">
        <div className="max-w-7xl mx-auto">
          {/* Page Title */}
          <div className="mb-10">
            <h2 className="text-3xl mb-2" style={{
              fontFamily: 'Montserrat, sans-serif',
              color: '#E06E7F'
            }}>
              Admin Dashboard
            </h2>
            <p className="text-sm" style={{
              fontFamily: 'Montserrat, sans-serif',
              color: '#999'
            }}>
              Welcome back! Here's what's happening on your platform.
            </p>
          </div>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
            {/* Total Users */}
            <div className="p-6 rounded-lg" style={{
              backgroundColor: 'white',
              border: '2px solid rgba(224, 110, 127, 0.1)'
            }}>
              <div className="flex items-center justify-between mb-4">
                <span style={{ fontSize: '28px' }}>👥</span>
                <span className="text-sm" style={{
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#999'
                }}>
                  Total
                </span>
              </div>
              <p className="text-4xl font-bold mb-2" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#E06E7F'
              }}>
                {stats.totalUsers}
              </p>
              <p className="text-xs" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#999'
              }}>
                Active Users
              </p>
            </div>

            {/* Total Restaurants */}
            <div className="p-6 rounded-lg" style={{
              backgroundColor: 'white',
              border: '2px solid rgba(224, 110, 127, 0.1)'
            }}>
              <div className="flex items-center justify-between mb-4">
                <span style={{ fontSize: '28px' }}>🍽️</span>
                <span className="text-sm" style={{
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#999'
                }}>
                  Listed
                </span>
              </div>
              <p className="text-4xl font-bold mb-2" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#E06E7F'
              }}>
                {stats.totalRestaurants}
              </p>
              <p className="text-xs" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#999'
              }}>
                Restaurants
              </p>
            </div>

            {/* Pending Approvals */}
            <div className="p-6 rounded-lg" style={{
              backgroundColor: 'white',
              border: '2px solid rgba(224, 110, 127, 0.1)'
            }}>
              <div className="flex items-center justify-between mb-4">
                <span style={{ fontSize: '28px' }}>⏳</span>
                <span className="text-sm" style={{
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#999',
                  backgroundColor: '#FFE5EC',
                  padding: '4px 8px',
                  borderRadius: '4px'
                }}>
                  Urgent
                </span>
              </div>
              <p className="text-4xl font-bold mb-2" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#E06E7F'
              }}>
                {stats.pendingApprovals}
              </p>
              <p className="text-xs" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#999'
              }}>
                Pending Approvals
              </p>
            </div>

            {/* Pending Reports */}
            <div className="p-6 rounded-lg" style={{
              backgroundColor: 'white',
              border: '2px solid rgba(224, 110, 127, 0.1)'
            }}>
              <div className="flex items-center justify-between mb-4">
                <span style={{ fontSize: '28px' }}>🚨</span>
              </div>
              <p className="text-4xl font-bold mb-2" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#E06E7F'
              }}>
                {stats.pendingReports}
              </p>
              <p className="text-xs" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#999'
              }}>
                Content Reports
              </p>
            </div>

            {/* Suspicious Accounts */}
            <div className="p-6 rounded-lg" style={{
              backgroundColor: 'white',
              border: '2px solid rgba(224, 110, 127, 0.1)'
            }}>
              <div className="flex items-center justify-between mb-4">
                <span style={{ fontSize: '28px' }}>⚠️</span>
              </div>
              <p className="text-4xl font-bold mb-2" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#E06E7F'
              }}>
                {stats.suspiciousAccounts}
              </p>
              <p className="text-xs" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#999'
              }}>
                Suspicious Accounts
              </p>
            </div>

            {/* Flagged Content */}
            <div className="p-6 rounded-lg" style={{
              backgroundColor: 'white',
              border: '2px solid rgba(224, 110, 127, 0.1)'
            }}>
              <div className="flex items-center justify-between mb-4">
                <span style={{ fontSize: '28px' }}>🚩</span>
              </div>
              <p className="text-4xl font-bold mb-2" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#E06E7F'
              }}>
                {stats.flaggedContent}
              </p>
              <p className="text-xs" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#999'
              }}>
                Flagged Content
              </p>
            </div>
          </div>

          {/* Action Buttons Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Moderation */}
            <button
              onClick={onViewModeration}
              className="p-8 rounded-lg text-left transition-all"
              style={{
                backgroundColor: 'white',
                border: '2px solid rgba(224, 110, 127, 0.1)',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.05)';
                e.currentTarget.style.borderColor = '#E06E7F';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'white';
                e.currentTarget.style.borderColor = 'rgba(224, 110, 127, 0.1)';
              }}
            >
              <h3 className="text-2xl mb-2" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#E06E7F'
              }}>
                🔍 Content Moderation
              </h3>
              <p className="text-sm" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#666'
              }}>
                Review and moderate reported content and user behavior
              </p>
            </button>

            {/* Pending Approvals */}
            <button
              onClick={onViewPendingApprovals}
              className="p-8 rounded-lg text-left transition-all"
              style={{
                backgroundColor: 'white',
                border: '2px solid rgba(224, 110, 127, 0.1)',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.05)';
                e.currentTarget.style.borderColor = '#E06E7F';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'white';
                e.currentTarget.style.borderColor = 'rgba(224, 110, 127, 0.1)';
              }}
            >
              <h3 className="text-2xl mb-2" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#E06E7F'
              }}>
                ✅ Business Approvals
              </h3>
              <p className="text-sm" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#666'
              }}>
                Approve or reject pending restaurant registrations
              </p>
            </button>

            {/* Manage Users */}
            <button
              onClick={onViewPendingUsers}
              className="p-8 rounded-lg text-left transition-all"
              style={{
                backgroundColor: 'white',
                border: '2px solid rgba(224, 110, 127, 0.1)',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.05)';
                e.currentTarget.style.borderColor = '#E06E7F';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'white';
                e.currentTarget.style.borderColor = 'rgba(224, 110, 127, 0.1)';
              }}
            >
              <h3 className="text-2xl mb-2" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#E06E7F'
              }}>
                👤 Manage Users
              </h3>
              <p className="text-sm" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#666'
              }}>
                View and manage user accounts and permissions
              </p>
            </button>

            {/* Admin Logs */}
            <button
              onClick={onViewLogs}
              className="p-8 rounded-lg text-left transition-all"
              style={{
                backgroundColor: 'white',
                border: '2px solid rgba(224, 110, 127, 0.1)',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.05)';
                e.currentTarget.style.borderColor = '#E06E7F';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'white';
                e.currentTarget.style.borderColor = 'rgba(224, 110, 127, 0.1)';
              }}
            >
              <h3 className="text-2xl mb-2" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#E06E7F'
              }}>
                📋 Admin Logs
              </h3>
              <p className="text-sm" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#666'
              }}>
                View system logs and admin activity history
              </p>
            </button>

            {/* Approved accounts (JSON + SPA; replaces nomz-admin/approved-accounts/ list for day-to-day use) */}
            <button
              type="button"
              onClick={onViewApprovedAccounts}
              className="p-8 rounded-lg text-left transition-all"
              style={{
                backgroundColor: 'white',
                border: '2px solid rgba(224, 110, 127, 0.1)',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.05)';
                e.currentTarget.style.borderColor = '#E06E7F';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'white';
                e.currentTarget.style.borderColor = 'rgba(224, 110, 127, 0.1)';
              }}
            >
              <h3 className="text-2xl mb-2" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#E06E7F'
              }}>
                ✓ Approved businesses
              </h3>
              <p className="text-sm" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#666'
              }}>
                Restaurant accounts already approved; revoke if needed
              </p>
            </button>

            <button
              type="button"
              onClick={onViewRejectedAccounts}
              className="p-8 rounded-lg text-left transition-all"
              style={{
                backgroundColor: 'white',
                border: '2px solid rgba(224, 110, 127, 0.1)',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.05)';
                e.currentTarget.style.borderColor = '#E06E7F';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'white';
                e.currentTarget.style.borderColor = 'rgba(224, 110, 127, 0.1)';
              }}
            >
              <h3 className="text-2xl mb-2" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#E06E7F'
              }}>
                ✕ Rejected businesses
              </h3>
              <p className="text-sm" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#666'
              }}>
                Denied or revoked accounts; approve again if appropriate
              </p>
            </button>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
