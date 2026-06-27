import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../state/AuthContext";
import { fetchAttendanceSummary, fetchAttendance } from "../api/attendance";

const Dashboard = () => {
  const [summary, setSummary] = useState<{
    date: string;
    total_people: number;
    present: number;
    attendance_rate: number;
  } | null>(null);
  const [recent, setRecent] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const { role } = useAuth();

  useEffect(() => {
    const load = async () => {
      try {
        const summaryData = await fetchAttendanceSummary();
        const recentData = await fetchAttendance();
        setSummary(summaryData);
        setRecent(recentData.records.slice(0, 5));
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return <div className="card">Loading dashboard...</div>;
  }

  return (
    <div className="stack">
      <div className="card hero-card">
        <div>
          <h2>Welcome to AttendancePro</h2>
          <p className="muted">
            Monitor face recognition, review attendance trends, and keep records accurate.
          </p>
        </div>
        <div className="hero-actions">
          <Link className="primary" to="/app/monitoring">
            Start Monitoring
          </Link>
          <Link className="ghost-button ghost-dark" to="/app/attendance">
            View Attendance
          </Link>
        </div>
      </div>
      <div className="grid-3">
        <div className="card stat">
          <div className="stat-label">Total People</div>
          <div className="stat-value">{summary?.total_people ?? 0}</div>
        </div>
        <div className="card stat">
          <div className="stat-label">Present Today</div>
          <div className="stat-value">{summary?.present ?? 0}</div>
        </div>
        <div className="card stat">
          <div className="stat-label">Attendance Rate</div>
          <div className="stat-value">{summary?.attendance_rate ?? 0}%</div>
        </div>
      </div>

      <div className="card">
        <h3>Latest Attendance</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Check-in</th>
            </tr>
          </thead>
          <tbody>
            {recent.map((record) => (
              <tr key={record.id}>
                <td>{record.name}</td>
                <td className="badge">{record.person_type}</td>
                <td>{new Date(record.check_in_time).toLocaleString()}</td>
              </tr>
            ))}
            {!recent.length && (
              <tr>
                <td colSpan={3} className="muted">
                  No attendance records yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div className="card">
        <div className="row-between">
          <div>
            <h3>Quick Actions</h3>
            <p className="muted">Common tasks to keep operations smooth.</p>
          </div>
        </div>
        <div className="action-grid">
          {role === "admin" && (
            <Link className="action-card" to="/app/people">
              <div className="action-title">Manage People</div>
              <p className="muted">Add students or staff and train faces.</p>
            </Link>
          )}
          {(role === "admin" || role === "staff") && (
            <Link className="action-card" to="/app/attendance">
              <div className="action-title">Attendance Reports</div>
              <p className="muted">Filter by date or person type.</p>
            </Link>
          )}
          {role === "admin" && (
            <Link className="action-card" to="/app/settings">
              <div className="action-title">System Settings</div>
              <p className="muted">Adjust recognition thresholds.</p>
            </Link>
          )}
          {role === "student" && (
            <div className="action-card">
              <div className="action-title">Student Access</div>
              <p className="muted">Ask admin to enable student reports.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
