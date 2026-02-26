import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";

// ProjectIssuesPage handles issue browsing/filtering and maintainer-only issue creation inside a project.
export default function ProjectIssuesPage({ me, notify }) {
  const { projectId } = useParams();
  const [issues, setIssues] = useState([]);
  const [members, setMembers] = useState([]);
  const [filters, setFilters] = useState({ q: "", status: "", priority: "", assignee: "", sort: "created_at" });
  const [form, setForm] = useState({ title: "", description: "", priority: "medium", assignee_id: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const pageSize = 5;

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams();
      if (filters.q) params.set("q", filters.q);
      if (filters.status) params.set("status", filters.status);
      if (filters.priority) params.set("priority", filters.priority);
      if (filters.assignee) params.set("assignee", filters.assignee);
      if (filters.sort) params.set("sort", filters.sort);
      params.set("limit", String(pageSize));
      params.set("offset", String(page * pageSize));
      const data = await api(`/projects/${projectId}/issues?${params.toString()}`);
      setIssues(data);
      const mems = await api(`/projects/${projectId}/members`);
      setMembers(mems);
    } catch (err) {
      setError(err.message);
      notify(err.message, "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [projectId, page]);

  const createIssue = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api(`/projects/${projectId}/issues`, {
        method: "POST",
        body: JSON.stringify({
          title: form.title,
          description: form.description,
          priority: form.priority,
          assignee_id: form.assignee_id ? Number(form.assignee_id) : null,
        }),
      });
      setForm({ title: "", description: "", priority: "medium", assignee_id: "" });
      notify("Issue created", "success");
      load();
    } catch (err) {
      setError(err.message);
      notify(err.message, "error");
    }
  };

  const hasNextPage = issues.length === pageSize;
  const myRole = members.find((m) => m.user_id === me?.id)?.role;
  const isMaintainer = myRole === "maintainer";

  return (
    <div className="page">
      <h1>Project Issues</h1>
      <div className="grid">
        <div className="card">
          <h3>Filters</h3>
          <label>Search</label>
          <input value={filters.q} onChange={(e) => setFilters({ ...filters, q: e.target.value })} />
          <label>Status</label>
          <select value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
            <option value="">All</option>
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
          <label>Priority</label>
          <select value={filters.priority} onChange={(e) => setFilters({ ...filters, priority: e.target.value })}>
            <option value="">All</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
          <label>Assignee</label>
          <select value={filters.assignee} onChange={(e) => setFilters({ ...filters, assignee: e.target.value })}>
            <option value="">All</option>
            {members.map((m) => <option key={m.user_id} value={m.user_id}>{m.name}</option>)}
          </select>
          <label>Sort</label>
          <select value={filters.sort} onChange={(e) => setFilters({ ...filters, sort: e.target.value })}>
            <option value="created_at">Created</option>
            <option value="priority">Priority</option>
            <option value="status">Status</option>
          </select>
          <button className="btn" onClick={() => { setPage(0); load(); }}>Apply</button>
        </div>

        {isMaintainer && (
          <div className="card">
            <h3>New Issue</h3>
            <form onSubmit={createIssue}>
              <label>Title</label>
              <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
              <label>Description</label>
              <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              <label>Priority</label>
              <select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
              <label>Assignee</label>
              <select value={form.assignee_id} onChange={(e) => setForm({ ...form, assignee_id: e.target.value })}>
                <option value="">Unassigned</option>
                {members.map((m) => <option key={m.user_id} value={m.user_id}>{m.name}</option>)}
              </select>
              {error && <div className="error">{error}</div>}
              <button className="btn">Create Issue</button>
            </form>
          </div>
        )}
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h3>Issues</h3>
        {loading ? (
          <div>Loading...</div>
        ) : (
          <ul className="list">
            {issues.map((i) => (
              <li key={i.id}>
                <div>
                  <strong>{i.title}</strong>
                  <div className="muted">{i.status} | {i.priority}</div>
                </div>
                <Link className="btn secondary" to={`/issues/${i.id}`}>View</Link>
              </li>
            ))}
            {issues.length === 0 && <li className="muted">No issues found</li>}
          </ul>
        )}
        <div className="pager">
          <button className="btn secondary" disabled={page === 0} onClick={() => setPage((p) => Math.max(0, p - 1))}>Previous</button>
          <span className="muted">Page {page + 1}</span>
          <button className="btn secondary" disabled={!hasNextPage} onClick={() => setPage((p) => p + 1)}>Next</button>
        </div>
      </div>
    </div>
  );
}
