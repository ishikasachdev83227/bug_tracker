import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";

// ProjectTeamPage handles team membership management (invite, role update, remove) for a single project.
export default function ProjectTeamPage({ me, notify }) {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [members, setMembers] = useState([]);
  const [invite, setInvite] = useState({ email: "", role: "member" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const [mems, projects] = await Promise.all([api(`/projects/${projectId}/members`), api("/projects")]);
      setMembers(mems);
      setProject(projects.find((p) => String(p.id) === String(projectId)) || null);
    } catch (err) {
      setError(err.message);
      notify(err.message, "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [projectId]);

  const inviteMember = async (e) => {
    e.preventDefault();
    try {
      await api(`/projects/${projectId}/members`, {
        method: "POST",
        body: JSON.stringify(invite),
      });
      setInvite({ email: "", role: "member" });
      notify("Member saved", "success");
      load();
    } catch (err) {
      setError(err.message);
      notify(err.message, "error");
    }
  };

  const updateRole = async (userId, nextRole) => {
    try {
      await api(`/projects/${projectId}/members/${userId}`, {
        method: "PATCH",
        body: JSON.stringify({ role: nextRole }),
      });
      notify("Member role updated", "success");
      load();
    } catch (err) {
      notify(err.message, "error");
      setError(err.message);
    }
  };

  const removeMember = async (userId) => {
    try {
      await api(`/projects/${projectId}/members/${userId}`, { method: "DELETE" });
      notify("Member removed", "success");
      load();
    } catch (err) {
      notify(err.message, "error");
      setError(err.message);
    }
  };

  const myMember = members.find((m) => m.user_id === me?.id);
  const isMaintainer = myMember?.role === "maintainer";

  return (
    <div className="page">
      <div className="row" style={{ marginBottom: 12 }}>
        <Link className="btn secondary" to="/teams">Back to Teams</Link>
      </div>
      <h1>Team & Roles</h1>
      {project && <div className="muted" style={{ marginBottom: 10 }}>{project.name} ({project.key}) - {project.description}</div>}
      <div className="card">
        {loading ? (
          <div>Loading...</div>
        ) : (
          <>
            {isMaintainer && (
              <form onSubmit={inviteMember}>
                <label>Invite by Email</label>
                <input value={invite.email} onChange={(e) => setInvite({ ...invite, email: e.target.value })} required />
                <label>Role</label>
                <select value={invite.role} onChange={(e) => setInvite({ ...invite, role: e.target.value })}>
                  <option value="member">Member</option>
                  <option value="maintainer">Maintainer</option>
                </select>
                <button className="btn">Add / Update Member</button>
              </form>
            )}

            {error && <div className="error">{error}</div>}

            <ul className="list" style={{ marginTop: 12 }}>
              {members.map((m) => (
                <li key={m.user_id}>
                  <div>
                    <strong>{m.name}</strong> <span className="muted">({m.email})</span>
                  </div>
                  <div className="row">
                    {isMaintainer ? (
                      <>
                        <select value={m.role} onChange={(e) => updateRole(m.user_id, e.target.value)}>
                          <option value="member">Member</option>
                          <option value="maintainer">Maintainer</option>
                        </select>
                        <button className="btn secondary" onClick={() => removeMember(m.user_id)}>Remove</button>
                      </>
                    ) : (
                      <span className="muted">{m.role}</span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
      <div className="row" style={{ marginTop: 12 }}>
        <Link className="btn secondary" to="/teams">Back to Teams</Link>
      </div>
    </div>
  );
}
