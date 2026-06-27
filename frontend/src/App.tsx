import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./state/AuthContext";
import Login from "./pages/Login";
import Welcome from "./pages/Welcome";
import Dashboard from "./pages/Dashboard";
import LiveMonitoring from "./pages/LiveMonitoring";
import People from "./pages/People";
import Attendance from "./pages/Attendance";
import Settings from "./pages/Settings";
import AppLayout from "./components/AppLayout";
import AccessDenied from "./pages/AccessDenied";

const RequireAuth: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

const RequireRole: React.FC<{
  allowed: Array<"admin" | "staff" | "student">;
  children: React.ReactNode;
}> = ({ allowed, children }) => {
  const { role } = useAuth();
  if (!allowed.includes(role)) {
    return <AccessDenied />;
  }
  return <>{children}</>;
};

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<Welcome />} />
      <Route path="/login" element={<Navigate to="/auth" replace />} />
      <Route path="/auth" element={<Login />} />
      <Route
        path="/app"
        element={
          <RequireAuth>
            <AppLayout />
          </RequireAuth>
        }
      >
        <Route index element={<Dashboard />} />
        <Route
          path="monitoring"
          element={
            <RequireRole allowed={["admin", "staff"]}>
              <LiveMonitoring />
            </RequireRole>
          }
        />
        <Route
          path="people"
          element={
            <RequireRole allowed={["admin"]}>
              <People />
            </RequireRole>
          }
        />
        <Route
          path="attendance"
          element={
            <RequireRole allowed={["admin", "staff"]}>
              <Attendance />
            </RequireRole>
          }
        />
        <Route
          path="settings"
          element={
            <RequireRole allowed={["admin"]}>
              <Settings />
            </RequireRole>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default App;
