import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

// ProjectsPage handles listing projects the current user belongs to and project creation for allowed users.
export default function ProjectsPage({ hasMaintainerAccess, notify }) {
  const [projects, setProjects] = useState([]);
  const [name, setName] = useState("");
  const [key, setKey] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    api("/projects")
      .then(setProjects)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const create = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api("/projects", {
        method: "POST",
        body: JSON.stringify({ name, key, description }),
      });
      setName("");
      setKey("");
      setDescription("");
      notify("Project created", "success");
      load();
    } catch (err) {
      setError(err.message);
      notify(err.message, "error");
    }
  };

  const canCreateProject = hasMaintainerAccess || projects.length === 0;

  return (
    <div className="page">
      <h1>Your Projects</h1>
      <div className="grid">
        {canCreateProject && (
          <div className="card">
            <h3>Create Project</h3>
            <form onSubmit={create}>
              <label>Name</label>
              <input value={name} onChange={(e) => setName(e.target.value)} required />
              <label>Key</label>
              <input value={key} onChange={(e) => setKey(e.target.value)} required />
              <label>Description</label>
              <textarea value={description} onChange={(e) => setDescription(e.target.value)} />
              {error && <div className="error">{error}</div>}
              <button className="btn">Create</button>
            </form>
          </div>
        )}

        <div className="card">
          <h3>Projects</h3>
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
                  <Link className="btn secondary" to={`/projects/${p.id}`}>Issues</Link>
                </li>
              ))}
              {projects.length === 0 && <li className="muted">No projects yet</li>}
              {!canCreateProject && <li className="muted">Project creation is restricted to maintainers.</li>}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
