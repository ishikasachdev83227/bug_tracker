import React, { useEffect, useState } from "react";
import { Routes, Route, Navigate, Link, useNavigate } from "react-router-dom";
import { api, getToken, setToken } from "./api";
import SignupPage from "./pages/SignupPage.jsx";
import ProjectsPage from "./pages/ProjectsPage.jsx";
import TeamsPage from "./pages/TeamsPage.jsx";
import ProjectIssuesPage from "./pages/ProjectIssuesPage.jsx";
import ProjectTeamPage from "./pages/ProjectTeamPage.jsx";
import IssueDetailPage from "./pages/IssueDetailPage.jsx";

// App wires top-level auth state, route guards, shared navigation, and toast notifications.
function LoginPage({ onAuth, notify }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await api("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      setToken(data.access_token);
      const me = await api("/me");
      await onAuth(me);
      notify("Logged in successfully", "success");
      navigate("/projects");
    } catch (err) {
      setError(err.message);
      notify(err.message, "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <h1>Login</h1>
      <form className="card" onSubmit={submit}>
        <label>Email</label>
        <input value={email} onChange={(e) => setEmail(e.target.value)} required />
        <label>Password</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        {error && <div className="error">{error}</div>}
        <button className="btn" disabled={loading}>{loading ? "Signing in..." : "Login"}</button>
      </form>
      <p>Don't have an account? <Link to="/signup">Sign up</Link></p>
    </div>
  );
}

export default function App() {
  const [me, setMe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [toasts, setToasts] = useState([]);
  const [maintainedProjects, setMaintainedProjects] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }
    api("/me")
      .then(async (data) => {
        setMe(data);
        try {
          const maintained = await api("/projects/maintained");
          setMaintainedProjects(maintained);
        } catch {
          setMaintainedProjects([]);
        }
      })
      .catch(() => setToken(null))
      .finally(() => setLoading(false));
  }, []);

  const handleAuth = async (user) => {
    setMe(user);
    try {
      const maintained = await api("/projects/maintained");
      setMaintainedProjects(maintained);
    } catch {
      setMaintainedProjects([]);
    }
  };

  const logout = () => {
    setToken(null);
    setMe(null);
    setMaintainedProjects([]);
    navigate("/login");
  };

  const notify = (message, type = "info") => {
    const id = `${Date.now()}-${Math.random()}`;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 2500);
  };

  if (loading) return <div className="page">Loading...</div>;

  const token = getToken();
  const hasMaintainerAccess = maintainedProjects.length > 0;

  return (
    <div>
      <header className="topbar">
        <div className="brand">IssueHub</div>
        <nav>
          {token && <Link to="/projects">Projects</Link>}
          {token && hasMaintainerAccess && <Link to="/teams">Teams</Link>}
        </nav>
        <div className="spacer" />
        {token ? (
          <button className="btn" onClick={logout}>Logout</button>
        ) : (
          <Link to="/login">Login</Link>
        )}
      </header>

      <Routes>
        <Route path="/" element={token ? <Navigate to="/projects" /> : <Navigate to="/login" />} />
        <Route path="/login" element={<LoginPage onAuth={handleAuth} notify={notify} />} />
        <Route path="/signup" element={<SignupPage onAuth={handleAuth} notify={notify} />} />
        <Route path="/projects" element={<ProjectsPage hasMaintainerAccess={hasMaintainerAccess} notify={notify} />} />
        <Route path="/teams" element={hasMaintainerAccess ? <TeamsPage notify={notify} /> : <Navigate to="/projects" />} />
        <Route path="/projects/:projectId" element={<ProjectIssuesPage me={me} notify={notify} />} />
        <Route path="/projects/:projectId/team" element={hasMaintainerAccess ? <ProjectTeamPage me={me} notify={notify} /> : <Navigate to="/projects" />} />
        <Route path="/issues/:issueId" element={<IssueDetailPage me={me} notify={notify} />} />
      </Routes>

      <div className="toast-wrap">
        {toasts.map((toast) => (
          <div key={toast.id} className={`toast ${toast.type}`}>
            {toast.message}
          </div>
        ))}
      </div>
    </div>
  );
}
