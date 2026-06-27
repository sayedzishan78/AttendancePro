import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { login, register } from "../api/auth";
import { useAuth } from "../state/AuthContext";

const Login = () => {
  const navigate = useNavigate();
  const { setToken, setRole, isAuthenticated } = useAuth();
  const authRef = useRef<HTMLDivElement>(null);
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [mode, setMode] = useState<"login" | "register">("login");
  const [showPanel, setShowPanel] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showLoginPassword, setShowLoginPassword] = useState(false);
  const [showRegisterPassword, setShowRegisterPassword] = useState(false);
  const [showRegisterConfirm, setShowRegisterConfirm] = useState(false);
  const [registerLoading, setRegisterLoading] = useState(false);
  const [registerError, setRegisterError] = useState<string | null>(null);
  const [registerForm, setRegisterForm] = useState({
    fullName: "",
    email: "",
    password: "",
    confirmPassword: "",
    role: "staff" as "staff" | "student",
    department: "",
    rollNumber: "",
    year: "",
    section: "",
    staffId: "",
    designation: "",
    note: "",
  });
  const [registerMessage, setRegisterMessage] = useState<string | null>(null);
  const [facePreview, setFacePreview] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await login(username, password);
      setToken(data.access_token);
      setRole(data.role);
      navigate("/app");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const submitRegistration = async (e: React.FormEvent) => {
    e.preventDefault();
    const missing: string[] = [];
    if (!registerForm.fullName) missing.push("Full Name");
    if (!registerForm.email) missing.push("Email");
    if (!registerForm.password) missing.push("Password");
    if (!registerForm.confirmPassword) missing.push("Confirm Password");
    if (registerForm.role === "student") {
      if (!registerForm.rollNumber) missing.push("Roll Number");
      if (!registerForm.department) missing.push("Department");
      if (!registerForm.year) missing.push("Year/Semester");
      if (!registerForm.section) missing.push("Section");
    } else {
      if (!registerForm.staffId) missing.push("Staff ID");
      if (!registerForm.department) missing.push("Department");
      if (!registerForm.designation) missing.push("Designation");
    }
    if (missing.length) {
      setRegisterError(`Please fill: ${missing.join(", ")}`);
      return;
    }
    if (registerForm.password !== registerForm.confirmPassword) {
      setRegisterError("Passwords do not match.");
      return;
    }
    setRegisterLoading(true);
    setRegisterError(null);
    setRegisterMessage(null);
    try {
      const extraNotes = [
        registerForm.note,
        registerForm.role === "student" && registerForm.rollNumber
          ? `Roll No: ${registerForm.rollNumber}`
          : null,
        registerForm.role === "student" && registerForm.year
          ? `Year/Semester: ${registerForm.year}`
          : null,
        registerForm.role === "student" && registerForm.section
          ? `Section: ${registerForm.section}`
          : null,
        registerForm.role === "staff" && registerForm.staffId
          ? `Employee ID: ${registerForm.staffId}`
          : null,
        registerForm.role === "staff" && registerForm.designation
          ? `Designation: ${registerForm.designation}`
          : null,
      ].filter(Boolean);
      await register({
        full_name: registerForm.fullName,
        email: registerForm.email,
        password: registerForm.password,
        role: registerForm.role,
        department: registerForm.department || undefined,
        note: extraNotes.length ? extraNotes.join(" | ") : undefined,
      });
      setRegisterMessage("Registration successful. You can now login.");
      setMode("login");
      setUsername(registerForm.email);
      setRegisterForm({
        fullName: "",
        email: "",
        password: "",
        confirmPassword: "",
        role: "staff",
        department: "",
        rollNumber: "",
        year: "",
        section: "",
        staffId: "",
        designation: "",
        note: "",
      });
      setFacePreview(null);
    } catch (err: any) {
      setRegisterError(err?.response?.data?.detail || "Registration failed");
    } finally {
      setRegisterLoading(false);
    }
  };

  const roles: Array<{
    id: "staff" | "student";
    title: string;
    description: string;
    hint: string;
  }> = [
    {
      id: "staff",
      title: "Staff",
      description: "Monitor attendance and view reports.",
      hint: "Best for faculty and supervisors.",
    },
    {
      id: "student",
      title: "Student (Optional)",
      description: "View your own attendance summary.",
      hint: "Optional role if enabled by faculty.",
    },
  ];

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    const target = authRef.current;
    if (!target) return;
    const rect = target.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - 0.5;
    const y = (event.clientY - rect.top) / rect.height - 0.5;
    target.style.setProperty("--bg-shift-x", `${x * 40}px`);
    target.style.setProperty("--bg-shift-y", `${y * 40}px`);
  };

  const handleMouseLeave = () => {
    const target = authRef.current;
    if (!target) return;
    target.style.setProperty("--bg-shift-x", "0px");
    target.style.setProperty("--bg-shift-y", "0px");
  };

  const handleFaceChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      setFacePreview(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setFacePreview(url);
  };
  
  const openPanel = (nextMode: "login" | "register") => {
    setMode(nextMode);
    setShowPanel(true);
  };

  return (
    <div
      className="auth-page"
      ref={authRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <div className="auth-bg" />
      <header className="auth-navbar">
        <div className="auth-logo">
          <div className="logo-icon" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
          <div className="logo-text">ATTENDANCEPRO</div>
          <div className="hero-badge">AI POWERED</div>
        </div>
        <div className="auth-buttons">
          <button className="neon-outline" onClick={() => openPanel("login")}>
            Login
          </button>
          <button className="neon-outline" onClick={() => openPanel("register")}>
            Register
          </button>
        </div>
      </header>
      <section className="auth-content">
        <div className="auth-branding">
          <h1>Secure Access to AttendancePro</h1>
          <p className="subheading">
            AI-powered attendance system for modern institutions.
            Fast, secure, and intelligent.
          </p>
          <ul>
            <li>Real-time face recognition</li>
            <li>Secure role-based access</li>
            <li>Smart attendance tracking</li>
          </ul>
          <div className="glow-orb orb-one" />
        </div>
        <div className="auth-form-wrap">
          {showPanel && (
            <div className="auth-panel-slide open">
              <div className="card auth-card template-card">
                <div className="auth-logo">AttendancePro</div>
                <div className="auth-header">
                  <h2>{mode === "login" ? "Login" : "Registration"}</h2>
                  <p className="muted">
                    {mode === "login"
                      ? "Use your credentials to access the monitoring system."
                      : "Request access and select the appropriate role."}
                  </p>
                </div>
                {mode === "register" ? (
                  <div className="auth-panel">
              <div className="panel-switch">
                <span className="muted">Already have an account?</span>
                <button type="button" className="link-button" onClick={() => openPanel("login")}>
                  Back to Login
                </button>
              </div>
              <div className="role-toggle">
                {roles.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    className={registerForm.role === item.id ? "toggle active" : "toggle"}
                    onClick={() =>
                      setRegisterForm({ ...registerForm, role: item.id })
                    }
                  >
                    {item.title}
                  </button>
                ))}
              </div>
              <div className="role-summary">
                <div className="role-title">
                  {roles.find((item) => item.id === registerForm.role)?.title}
                </div>
                <div className="role-desc">
                  {roles.find((item) => item.id === registerForm.role)?.description}
                </div>
                <div className="role-hint">
                  {roles.find((item) => item.id === registerForm.role)?.hint}
                </div>
              </div>
              <form className="form register-form" onSubmit={submitRegistration} noValidate>
                <div className="form-section">
                  <div className="section-title">Personal Information</div>
                  <div className="section-grid">
                    <label>
                      Full Name
                      <input
                        value={registerForm.fullName}
                        onChange={(e) =>
                          setRegisterForm({ ...registerForm, fullName: e.target.value })
                        }
                        required
                      />
                    </label>
                    <label>
                      Email
                      <input
                        type="email"
                        value={registerForm.email}
                        onChange={(e) =>
                          setRegisterForm({ ...registerForm, email: e.target.value })
                        }
                        required
                      />
                    </label>
                  </div>
                </div>

                <div className="form-section">
                  <div className="section-title">Academic / Professional Details</div>
                  <div className="section-grid">
                    {registerForm.role === "student" ? (
                      <>
                        <label>
                          Roll Number
                          <input
                            value={registerForm.rollNumber}
                            onChange={(e) =>
                              setRegisterForm({ ...registerForm, rollNumber: e.target.value })
                            }
                            required
                          />
                        </label>
                        <label>
                          Department
                          <select
                            value={registerForm.department}
                            onChange={(e) =>
                              setRegisterForm({ ...registerForm, department: e.target.value })
                            }
                            required
                          >
                            <option value="">Select Department</option>
                            <option value="computer-science">Computer Science</option>
                            <option value="mechanical"> Mechanical Engineering</option>
                            <option value="Ai"> Ai&DS Engineering</option>
                            <option value="electrical">Electrical Engineering</option>
                            <option value="civil">civil engineering</option>
                          </select>
                        </label>
                        <label>
                          Year / Semester
                          <select
                            value={registerForm.year}
                            onChange={(e) =>
                              setRegisterForm({ ...registerForm, year: e.target.value })
                            }
                            required
                          >
                            <option value="">Select Year/Semester</option>
                            <option value="1">Year 1 / Semester 1</option>
                            <option value="2">Year 1 / Semester 2</option>
                            <option value="3">Year 2 / Semester 3</option>
                            <option value="4">Year 2 / Semester 4</option>
                            <option value="5">Year 3 / Semester 5</option>
                            <option value="6">Year 3 / Semester 6</option>
                            <option value="7">Year 4 / Semester 7</option>
                            <option value="8">Year 4 / Semester 8</option>
                          </select>
                        </label>
                        <label>
                          Section
                          <input
                            value={registerForm.section}
                            onChange={(e) =>
                              setRegisterForm({ ...registerForm, section: e.target.value })
                            }
                            required
                          />
                        </label>
                      </>
                    ) : (
                      <>
                        <label>
                          Staff ID
                          <input
                            value={registerForm.staffId}
                            onChange={(e) =>
                              setRegisterForm({ ...registerForm, staffId: e.target.value })
                            }
                            required
                          />
                        </label>
                        <label>
                          Department
                          <select
                            value={registerForm.department}
                            onChange={(e) =>
                              setRegisterForm({ ...registerForm, department: e.target.value })
                            }
                            required
                          >
                            <option value="">Select Department</option>
                            <option value="computer-science">Computer Science</option>
                            <option value="mechanical"> Mechanical Engineering</option>
                            <option value="Ai"> Ai&DS Engineering</option>
                            <option value="electrical">Electrical Engineering</option>
                            <option value="civil">Civil Engineering</option>
                          </select>
                        </label>
                        <label>
                          Designation
                          <select
                            value={registerForm.designation}
                            onChange={(e) =>
                              setRegisterForm({ ...registerForm, designation: e.target.value })
                            }
                            required
                          >
                            <option value="">Select Designation</option>
                            <option value="lecturer">Lecturer</option>
                            <option value="assistant-professor">Assistant Professor</option>
                            <option value="associate-professor">Associate Professor</option>
                            <option value="professor">Professor</option>
                            <option value="lab-instructor">Lab Instructor</option>
                          </select>
                        </label>
                      </>
                    )}
                  </div>
                </div>

                <div className="form-section">
                  <div className="section-title">Security</div>
                  <div className="section-grid">
                    <label>
                      Password
                      <div className="password-field">
                        <input
                          type={showRegisterPassword ? "text" : "password"}
                          value={registerForm.password}
                          onChange={(e) =>
                            setRegisterForm({ ...registerForm, password: e.target.value })
                          }
                          required
                        />
                        <button
                          type="button"
                          className="toggle-visibility"
                          onClick={() => setShowRegisterPassword((value) => !value)}
                          aria-label={showRegisterPassword ? "Hide password" : "Show password"}
                        >
                          {showRegisterPassword ? "Hide" : "Show"}
                        </button>
                      </div>
                    </label>
                    <label>
                      Confirm Password
                      <div className="password-field">
                        <input
                          type={showRegisterConfirm ? "text" : "password"}
                          value={registerForm.confirmPassword}
                          onChange={(e) =>
                            setRegisterForm({
                              ...registerForm,
                              confirmPassword: e.target.value,
                            })
                          }
                          required
                        />
                        <button
                          type="button"
                          className="toggle-visibility"
                          onClick={() => setShowRegisterConfirm((value) => !value)}
                          aria-label={showRegisterConfirm ? "Hide password" : "Show password"}
                        >
                          {showRegisterConfirm ? "Hide" : "Show"}
                        </button>
                      </div>
                    </label>
                  </div>
                </div>

                {registerForm.role === "student" && (
                  <div className="form-section">
                    <div className="section-title">Face Upload</div>
                    <div className="upload-section">
                      <label className="dropzone">
                        <span>Drag & drop face image or click to upload</span>
                        <input
                          type="file"
                          accept="image/*"
                          onChange={handleFaceChange}
                        />
                      </label>
                      <div className="preview-box">
                        {facePreview ? (
                          <img src={facePreview} alt="Face preview" />
                        ) : (
                          <span>Preview</span>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                <label>
                  Note (optional)
                  <input
                    value={registerForm.note}
                    onChange={(e) =>
                      setRegisterForm({ ...registerForm, note: e.target.value })
                    }
                    placeholder="Reason for access"
                  />
                </label>
                <button className="primary" type="submit">
                  {registerLoading ? "Submitting..." : "Submit Request"}
                </button>
                {registerError && <div className="error">{registerError}</div>}
                {registerMessage && <div className="notice">{registerMessage}</div>}
                    </form>
                  </div>
                ) : (
                  <form className="form" onSubmit={onSubmit}>
                <label>
                  Email
                  <input
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="example@campus.edu"
                    autoComplete="username"
                  />
                </label>
                <label>
                  Password
                  <div className="password-field">
                    <input
                      type={showLoginPassword ? "text" : "password"}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter your password"
                      autoComplete="current-password"
                    />
                    <button
                      type="button"
                      className="toggle-visibility"
                      onClick={() => setShowLoginPassword((value) => !value)}
                      aria-label={showLoginPassword ? "Hide password" : "Show password"}
                    >
                      {showLoginPassword ? "Hide" : "Show"}
                    </button>
                  </div>
                </label>
                {error && <div className="error">{error}</div>}
                <button className="primary" type="submit" disabled={loading}>
                  {loading ? "Signing in..." : "Sign In"}
                </button>
                <div className="panel-switch">
                  <span className="muted">No account yet?</span>
                  <button
                    type="button"
                    className="link-button"
                    onClick={() => openPanel("register")}
                  >
                    Create account
                  </button>
                </div>
                  </form>
                )}
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default Login;
