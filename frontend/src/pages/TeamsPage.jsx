import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

// TeamsPage handles maintainer-level team operations: invite existing users, onboard new users, and open project team pages.
export default function TeamsPage({ notify }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [inviteExisting, setInviteExisting] = useState({ projectId: "", email: "", role: "member" });
  const [onboardUser, setOnboardUser] = useState({ projectId: "", name: "", email: "", password: "", role: "member" });

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await api("/projects/maintained");
      setProjects(data);
      if (data.length && !inviteExisting.projectId) setInviteExisting((p) => ({ ...p, projectId: String(data[0].id) }));
      if (data.length && !onboardUser.projectId) setOnboardUser((p) => ({ ...p, projectId: String(data[0].id) }));
    } catch (err) {
      setError(err.message);
      notify(err.message, "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const submitInviteExisting = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api(`/projects/${inviteExisting.projectId}/members`, {
        method: "POST",
        body: JSON.stringify({ email: inviteExisting.email, role: inviteExisting.role }),
      });
      setInviteExisting((p) => ({ ...p, email: "", role: "member" }));
      notify("Existing user added to team", "success");
    } catch (err) {
      setError(err.message);
      notify(err.message, "error");
    }
  };

  const submitOnboard = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api(`/projects/${onboardUser.projectId}/members/onboard`, {
        method: "POST",
        body: JSON.stringify({
          name: onboardUser.name,
          email: onboardUser.email,
          password: onboardUser.password,
          role: onboardUser.role,
        }),
      });
      setOnboardUser((p) => ({ ...p, name: "", email: "", password: "", role: "member" }));
      notify("New user onboarded and added to team", "success");
    } catch (err) {
      setError(err.message);
      notify(err.message, "error");
    }
  };

  return (
    <div className="page">
      <h1>Teams</h1>
      <div className="card">
        <h3>Invite Existing User</h3>
        <form onSubmit={submitInviteExisting}>
          <label>Project</label>
          <select value={inviteExisting.projectId} onChange={(e) => setInviteExisting((p) => ({ ...p, projectId: e.target.value }))} required>
            {projects.map((p) => <option key={p.id} value={p.id}>{p.name} ({p.key})</option>)}
          </select>
          <label>Email</label>
          <input value={inviteExisting.email} onChange={(e) => setInviteExisting((p) => ({ ...p, email: e.target.value }))} required />
          <label>Role</label>
          <select value={inviteExisting.role} onChange={(e) => setInviteExisting((p) => ({ ...p, role: e.target.value }))}>
            <option value="member">Member</option>
            <option value="maintainer">Maintainer</option>
          </select>
          <button className="btn" disabled={!projects.length}>Add / Update Member</button>
        </form>

        <h3 style={{ marginTop: 16 }}>Onboard New User</h3>
        <form onSubmit={submitOnboard}>
          <label>Project</label>
          <select value={onboardUser.projectId} onChange={(e) => setOnboardUser((p) => ({ ...p, projectId: e.target.value }))} required>
            {projects.map((p) => <option key={p.id} value={p.id}>{p.name} ({p.key})</option>)}
          </select>
          <label>Name</label>
          <input value={onboardUser.name} onChange={(e) => setOnboardUser((p) => ({ ...p, name: e.target.value }))} required />
          <label>Email</label>
          <input value={onboardUser.email} onChange={(e) => setOnboardUser((p) => ({ ...p, email: e.target.value }))} required />
          <label>Temporary Password</label>
          <input type="password" value={onboardUser.password} onChange={(e) => setOnboardUser((p) => ({ ...p, password: e.target.value }))} required />
          <label>Role</label>
          <select value={onboardUser.role} onChange={(e) => setOnboardUser((p) => ({ ...p, role: e.target.value }))}>
            <option value="member">Member</option>
            <option value="maintainer">Maintainer</option>
          </select>
          <button className="btn" disabled={!projects.length}>Create User & Add to Team</button>
        </form>

        <h3 style={{ marginTop: 16 }}>Project Teams</h3>
        {loading ? (
          <div>Loading...</div>
        ) : (
          <ul className="list">
            {projects.map((p) => (
              <li key={p.id}>
                <div>
                  <strong>{p.name}</strong> <span className="muted">({p.key})</span>
                  <div className="muted">{p.description}</div>
                </div>
                <Link className="btn secondary" to={`/projects/${p.id}/team`}>Open Team</Link>
              </li>
            ))}
            {!projects.length && <li className="muted">No team memberships yet</li>}
          </ul>
        )}
        {error && <div className="error">{error}</div>}
      </div>
    </div>
  );
}
