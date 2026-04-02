import { useState } from "react";

interface LogEntry {
  id: number;
  timestamp: string;
  admin: string;
  action: string;
  target: string;
  details: string;
}

export function AdminLogs({
  onBack
}: {
  onBack: () => void;
}) {
  const [logs] = useState<LogEntry[]>([
    {
      id: 1,
      timestamp: 'Apr 02, 2026 11:45 AM',
      admin: 'admin_user_1',
      action: 'Resolved Report',
      target: 'Report #124',
      details: 'Deleted inappropriate review from user @jane_smith'
    },
    {
      id: 2,
      timestamp: 'Apr 02, 2026 10:23 AM',
      admin: 'admin_user_2',
      action: 'Approved Registration',
      target: 'Tony\'s Pizzeria',
      details: 'Verified business documents and approved listing'
    },
    {
      id: 3,
      timestamp: 'Apr 01, 2026 03:50 PM',
      admin: 'admin_user_1',
      action: 'Suspended Account',
      target: '@bot_spam_123',
      details: 'Detected automated review pattern. Account suspended for 30 days'
    },
    {
      id: 4,
      timestamp: 'Apr 01, 2026 02:30 PM',
      admin: 'admin_user_2',
      action: 'Updated User Status',
      target: '@user_flagged_456',
      details: 'Flagged account due to suspicious activity pattern'
    },
    {
      id: 5,
      timestamp: 'Mar 31, 2026 04:15 PM',
      admin: 'admin_user_1',
      action: 'Rejected Registration',
      target: 'Fake Restaurant LLC',
      details: 'Business documents failed verification'
    },
    {
      id: 6,
      timestamp: 'Mar 31, 2026 01:22 PM',
      admin: 'admin_user_3',
      action: 'Flagged Content',
      target: 'Review #5634',
      details: 'Marked for review - contains potential spam'
    },
    {
      id: 7,
      timestamp: 'Mar 30, 2026 11:40 AM',
      admin: 'admin_user_2',
      action: 'Approved Registration',
      target: 'Sushi Haven',
      details: 'Verified business documents and approved listing'
    },
    {
      id: 8,
      timestamp: 'Mar 30, 2026 09:15 AM',
      admin: 'admin_user_1',
      action: 'Resolved Report',
      target: 'Report #120',
      details: 'Dismissed user dispute - no violation found'
    }
  ]);

  const [filterAction, setFilterAction] = useState('all');

  const actions = ['Resolved Report', 'Approved Registration', 'Rejected Registration', 'Suspended Account', 'Updated User Status', 'Flagged Content'];
  const filteredLogs = filterAction === 'all' 
    ? logs 
    : logs.filter(l => l.action === filterAction);

  const getActionColor = (action: string) => {
    switch (action) {
      case 'Approved Registration':
        return '#4CAF50';
      case 'Resolved Report':
        return '#2196F3';
      case 'Suspended Account':
        return '#D4183D';
      case 'Rejected Registration':
        return '#FF9800';
      case 'Flagged Content':
        return '#FFC107';
      default:
        return '#E06E7F';
    }
  };

  return (
    <div className="size-full flex flex-col overflow-y-auto" style={{ backgroundColor: '#FFF9F5' }}>
      {/* Navigation */}
      <nav className="w-full px-8 py-4 flex items-center gap-4 border-b" style={{ borderColor: 'rgba(224, 110, 127, 0.1)' }}>
        <button
          onClick={onBack}
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
          ←
        </button>
        <h1 className="text-2xl" style={{
          fontFamily: 'Montserrat, sans-serif',
          color: '#E06E7F'
        }}>
          Admin Logs
        </h1>
      </nav>

      {/* Main Content */}
      <main className="w-full py-8 px-8 flex-1">
        <div className="max-w-6xl mx-auto">
          {/* Filters */}
          <div className="mb-8">
            <p className="text-sm mb-4" style={{
              fontFamily: 'Montserrat, sans-serif',
              color: '#999'
            }}>
              Filter by Action
            </p>
            <div className="overflow-x-auto pb-2">
              <div className="flex gap-2 min-w-max">
                <button
                  onClick={() => setFilterAction('all')}
                  className="px-4 py-2 rounded-lg transition-all text-sm whitespace-nowrap"
                  style={{
                    backgroundColor: filterAction === 'all' ? '#E06E7F' : 'white',
                    color: filterAction === 'all' ? 'white' : '#E06E7F',
                    border: '2px solid rgba(224, 110, 127, 0.2)',
                    cursor: 'pointer',
                    fontFamily: 'Montserrat, sans-serif'
                  }}
                >
                  All
                </button>
                {actions.map((action) => (
                  <button
                    key={action}
                    onClick={() => setFilterAction(action)}
                    className="px-4 py-2 rounded-lg transition-all text-sm whitespace-nowrap"
                    style={{
                      backgroundColor: filterAction === action ? '#E06E7F' : 'white',
                      color: filterAction === action ? 'white' : '#E06E7F',
                      border: '2px solid rgba(224, 110, 127, 0.2)',
                      cursor: 'pointer',
                      fontFamily: 'Montserrat, sans-serif'
                    }}
                  >
                    {action}
                  </button>
                ))}
              </div>
            </div>
            <p className="text-sm mt-4" style={{
              fontFamily: 'Montserrat, sans-serif',
              color: '#999'
            }}>
              {filteredLogs.length} log entry/entries found
            </p>
          </div>

          {/* Logs Timeline */}
          <div className="space-y-4">
            {filteredLogs.map((log, idx) => (
              <div
                key={log.id}
                className="p-6 rounded-lg"
                style={{
                  backgroundColor: 'white',
                  border: '2px solid rgba(224, 110, 127, 0.1)'
                }}
              >
                <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
                  {/* Timeline dot */}
                  <div className="hidden md:flex items-start justify-center pt-1">
                    <div
                      style={{
                        width: '12px',
                        height: '12px',
                        borderRadius: '50%',
                        backgroundColor: getActionColor(log.action)
                      }}
                    />
                  </div>

                  {/* Timestamp */}
                  <div>
                    <p className="text-xs mb-1" style={{
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Timestamp
                    </p>
                    <p style={{
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#333',
                      fontSize: '14px'
                    }}>
                      {log.timestamp}
                    </p>
                  </div>

                  {/* Admin */}
                  <div>
                    <p className="text-xs mb-1" style={{
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Admin
                    </p>
                    <p style={{
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#333',
                      fontSize: '14px'
                    }}>
                      @{log.admin}
                    </p>
                  </div>

                  {/* Action */}
                  <div>
                    <p className="text-xs mb-1" style={{
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Action
                    </p>
                    <span
                      className="text-xs px-3 py-1 rounded inline-block"
                      style={{
                        backgroundColor: getActionColor(log.action),
                        color: 'white',
                        fontFamily: 'Montserrat, sans-serif'
                      }}
                    >
                      {log.action}
                    </span>
                  </div>

                  {/* Target */}
                  <div>
                    <p className="text-xs mb-1" style={{
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Target
                    </p>
                    <p style={{
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#333',
                      fontSize: '14px'
                    }}>
                      {log.target}
                    </p>
                  </div>

                  {/* Details */}
                  <div>
                    <p className="text-xs mb-1" style={{
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Details
                    </p>
                    <p style={{
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#666',
                      fontSize: '13px'
                    }}>
                      {log.details}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredLogs.length === 0 && (
            <div className="text-center py-12 px-8 rounded-lg" style={{
              backgroundColor: 'white',
              border: '2px solid rgba(224, 110, 127, 0.1)'
            }}>
              <span style={{ fontSize: '48px' }}>📋</span>
              <h3 className="mt-4 text-lg" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#E06E7F'
              }}>
                No Logs Found
              </h3>
              <p style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#999'
              }}>
                No log entries match the selected filter
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
