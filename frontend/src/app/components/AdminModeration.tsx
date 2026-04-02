import { useState } from "react";

interface Report {
  id: number;
  date: string;
  reporter: string;
  reason: string;
  target: string;
  targetType: 'review' | 'user' | 'restaurant';
  details: string;
  severity: 'low' | 'medium' | 'high';
}

export function AdminModeration({
  onBack
}: {
  onBack: () => void;
}) {
  const [reports, setReports] = useState<Report[]>([
    {
      id: 1,
      date: 'Apr 02, 2026 10:23 AM',
      reporter: 'john_doe',
      reason: 'Inappropriate Content',
      target: 'Review by @jane_smith',
      targetType: 'review',
      details: 'Offensive language and harassment in restaurant review',
      severity: 'high'
    },
    {
      id: 2,
      date: 'Apr 01, 2026 03:45 PM',
      reporter: 'alex_user',
      reason: 'Spam/Scam',
      target: 'Restaurant: "Flash Discounts"',
      targetType: 'restaurant',
      details: 'Suspicious promotions and fake reviews detected',
      severity: 'high'
    },
    {
      id: 3,
      date: 'Mar 31, 2026 02:15 PM',
      reporter: 'user_monitor',
      reason: 'Suspicious Account',
      target: 'User: @bot_account_123',
      targetType: 'user',
      details: 'Multiple accounts from same IP with identical review patterns',
      severity: 'medium'
    },
    {
      id: 4,
      date: 'Mar 30, 2026 11:22 AM',
      reporter: 'susan_m',
      reason: 'Misinformation',
      target: 'Review by @tourist_2024',
      targetType: 'review',
      details: 'False claims about restaurant hours and pricing',
      severity: 'low'
    }
  ]);

  const [selectedReport, setSelectedReport] = useState<number | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [action, setAction] = useState('dismiss');
  const [notes, setNotes] = useState('');

  const handleAction = (reportId: number) => {
    setSelectedReport(reportId);
    setShowModal(true);
  };

  const handleSubmitAction = () => {
    setReports(reports.filter(r => r.id !== selectedReport));
    setShowModal(false);
    setAction('dismiss');
    setNotes('');
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return '#D4183D';
      case 'medium':
        return '#E06E7F';
      default:
        return '#FFB6C1';
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
          Content Moderation
        </h1>
      </nav>

      {/* Main Content */}
      <main className="w-full py-8 px-8 flex-1">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl mb-2" style={{
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#E06E7F'
                }}>
                  Pending Reports
                </h2>
                <p className="text-sm" style={{
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#999'
                }}>
                  {reports.length} report(s) awaiting review
                </p>
              </div>
            </div>
          </div>

          {/* Reports Table */}
          {reports.length > 0 ? (
            <div className="space-y-4">
              {reports.map((report) => (
                <div
                  key={report.id}
                  className="p-6 rounded-lg"
                  style={{
                    backgroundColor: 'white',
                    border: '2px solid rgba(224, 110, 127, 0.1)'
                  }}
                >
                  <div className="grid grid-cols-6 gap-4 items-center mb-4">
                    <div>
                      <p className="text-xs" style={{
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#999'
                      }}>
                        Date
                      </p>
                      <p className="text-sm" style={{
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#333'
                      }}>
                        {report.date}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs" style={{
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#999'
                      }}>
                        Reporter
                      </p>
                      <p className="text-sm" style={{
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#333'
                      }}>
                        @{report.reporter}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs" style={{
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#999'
                      }}>
                        Reason
                      </p>
                      <span
                        className="text-xs px-3 py-1 rounded"
                        style={{
                          backgroundColor: 'rgba(224, 110, 127, 0.1)',
                          color: '#E06E7F',
                          fontFamily: 'Montserrat, sans-serif'
                        }}
                      >
                        {report.reason}
                      </span>
                    </div>
                    <div>
                      <p className="text-xs" style={{
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#999'
                      }}>
                        Severity
                      </p>
                      <span
                        className="text-xs px-3 py-1 rounded uppercase"
                        style={{
                          backgroundColor: getSeverityColor(report.severity),
                          color: 'white',
                          fontFamily: 'Montserrat, sans-serif'
                        }}
                      >
                        {report.severity}
                      </span>
                    </div>
                    <div className="col-span-2">
                      <p className="text-xs" style={{
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#999'
                      }}>
                        Target
                      </p>
                      <p className="text-sm" style={{
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#333'
                      }}>
                        {report.target}
                      </p>
                    </div>
                  </div>

                  <div className="mb-4 p-4 rounded" style={{
                    backgroundColor: 'rgba(224, 110, 127, 0.05)'
                  }}>
                    <p className="text-xs mb-2" style={{
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Details
                    </p>
                    <p style={{
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#666',
                      fontSize: '14px'
                    }}>
                      {report.details}
                    </p>
                  </div>

                  <button
                    onClick={() => handleAction(report.id)}
                    className="px-6 py-2 rounded-lg transition-all text-sm"
                    style={{
                      backgroundColor: '#E06E7F',
                      color: 'white',
                      border: 'none',
                      cursor: 'pointer',
                      fontFamily: 'Montserrat, sans-serif'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#D85870'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#E06E7F'}
                  >
                    Take Action
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 px-8 rounded-lg" style={{
              backgroundColor: 'white',
              border: '2px solid rgba(224, 110, 127, 0.1)'
            }}>
              <span style={{ fontSize: '48px' }}>✓</span>
              <h3 className="mt-4 text-lg" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#E06E7F'
              }}>
                All Clear!
              </h3>
              <p style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#999'
              }}>
                No pending reports to review
              </p>
            </div>
          )}
        </div>
      </main>

      {/* Action Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4" style={{
            boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)'
          }}>
            <h2 className="text-xl mb-6" style={{
              fontFamily: 'Montserrat, sans-serif',
              color: '#E06E7F'
            }}>
              Take Action on Report
            </h2>

            <div className="space-y-4 mb-6">
              <div>
                <label className="text-sm mb-2 block" style={{
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#333'
                }}>
                  Action
                </label>
                <select
                  value={action}
                  onChange={(e) => setAction(e.target.value)}
                  className="w-full px-4 py-2 border-2 rounded-lg"
                  style={{
                    borderColor: 'rgba(224, 110, 127, 0.2)',
                    fontFamily: 'Montserrat, sans-serif'
                  }}
                >
                  <option value="dismiss">Dismiss Report (No action)</option>
                  <option value="flag_fraud">Flag as Fraudulent</option>
                  <option value="delete">Delete Content</option>
                  <option value="suspend">Suspend User Account</option>
                </select>
              </div>

              <div>
                <label className="text-sm mb-2 block" style={{
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#333'
                }}>
                  Moderator Notes
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Reason for this action..."
                  className="w-full px-4 py-2 border-2 rounded-lg"
                  rows={3}
                  style={{
                    borderColor: 'rgba(224, 110, 127, 0.2)',
                    fontFamily: 'Montserrat, sans-serif'
                  }}
                />
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowModal(false)}
                className="flex-1 px-4 py-2 rounded-lg"
                style={{
                  backgroundColor: 'transparent',
                  color: '#E06E7F',
                  border: '2px solid #E06E7F',
                  cursor: 'pointer',
                  fontFamily: 'Montserrat, sans-serif'
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleSubmitAction}
                className="flex-1 px-4 py-2 rounded-lg"
                style={{
                  backgroundColor: '#E06E7F',
                  color: 'white',
                  border: 'none',
                  cursor: 'pointer',
                  fontFamily: 'Montserrat, sans-serif'
                }}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
