import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../state/AuthContext";

const AppLayout = () => {
  const { setToken, role } = useAuth();
  const today = new Date();
  const roleLabel = role.charAt(0).toUpperCase() + role.slice(1);
  const navItems = [
    { to: "/app", label: "Dashboard", roles: ["admin", "staff", "student"] },
    { to: "/app/monitoring", label: "Live Monitoring", roles: ["admin", "staff"] },
    { to: "/app/people", label: "Students & Staff", roles: ["admin"] },
    { to: "/app/attendance", label: "Attendance", roles: ["admin", "staff"] },
    { to: "/app/settings", label: "Settings", roles: ["admin"] },
  ];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">AttendancePro</div>
        <nav>
          {navItems.map((item) =>
            item.roles.includes(role) ? (
              <NavLink key={item.to} to={item.to} end={item.to === "/app"}>
                {item.label}
              </NavLink>
            ) : (
              <span key={item.to} className="nav-disabled">
                {item.label}
                <small>Restricted</small>
              </span>
            )
          )}
        </nav>
        <button className="ghost-button" onClick={() => setToken(null)}>
          Logout
        </button>
      </aside>
      <main className="content">
        <header className="topbar">
          <div className="topbar-title">
            <div className="title">Attendance Monitoring System</div>
            <div className="muted">
              {today.toLocaleDateString(undefined, {
                weekday: "long",
                month: "short",
                day: "numeric",
              })}
            </div>
          </div>
          <div className="topbar-actions">
            <span className="role-pill">{roleLabel} Access</span>
          </div>
        </header>
        <section className="page">
          <Outlet />
        </section>
      </main>
    </div>
  );
};

export default AppLayout;
