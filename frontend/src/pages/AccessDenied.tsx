import { Link } from "react-router-dom";

const AccessDenied = () => {
  return (
    <div className="card access-card">
      <div className="access-icon">🔒</div>
      <h3>Access Restricted</h3>
      <p className="muted">
        Your current role does not have permission to view this section. Please
        switch roles or contact the administrator.
      </p>
      <Link className="primary" to="/app">
        Back to Dashboard
      </Link>
    </div>
  );
};

export default AccessDenied;
