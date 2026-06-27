import { useEffect, useState } from "react";
import { fetchAttendance, AttendanceRecord } from "../api/attendance";
import { PersonType } from "../api/persons";

const Attendance = () => {
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [filters, setFilters] = useState({
    start_date: "",
    end_date: "",
    person_type: "" as "" | PersonType,
  });
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchAttendance({
        start_date: filters.start_date || undefined,
        end_date: filters.end_date || undefined,
        person_type: filters.person_type || undefined,
      });
      setRecords(data.records);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="stack">
      <div className="card">
        <div className="row-between">
          <h3>Attendance History</h3>
          <button className="primary" onClick={load} disabled={loading}>
            {loading ? "Loading..." : "Refresh"}
          </button>
        </div>
        <div className="filters">
          <label>
            Start Date
            <input
              type="date"
              value={filters.start_date}
              onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
            />
          </label>
          <label>
            End Date
            <input
              type="date"
              value={filters.end_date}
              onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
            />
          </label>
          <label>
            Person Type
            <select
              value={filters.person_type}
              onChange={(e) =>
                setFilters({ ...filters, person_type: e.target.value as any })
              }
            >
              <option value="">All</option>
              <option value="student">Students</option>
              <option value="staff">Staff</option>
            </select>
          </label>
        </div>
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Date</th>
              <th>Check-in</th>
              <th>Check-out</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody>
            {records.map((record) => (
              <tr key={record.id}>
                <td>{record.name}</td>
                <td className="badge">{record.person_type}</td>
                <td>{record.date}</td>
                <td>{new Date(record.check_in_time).toLocaleTimeString()}</td>
                <td>
                  {record.check_out_time
                    ? new Date(record.check_out_time).toLocaleTimeString()
                    : "-"}
                </td>
                <td>{(record.confidence * 100).toFixed(1)}%</td>
              </tr>
            ))}
            {!records.length && (
              <tr>
                <td colSpan={6} className="muted">
                  No attendance records yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Attendance;
