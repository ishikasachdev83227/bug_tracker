import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";

// IssueDetailPage handles single-issue metadata, status/assignee controls, and the comment thread with timestamps.
export default function IssueDetailPage({ me, notify }) {
  const { issueId } = useParams();
  const [issue, setIssue] = useState(null);
  const [comments, setComments] = useState([]);
  const [members, setMembers] = useState([]);
  const [body, setBody] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const i = await api(`/issues/${issueId}`);
      setIssue(i);
      const c = await api(`/issues/${issueId}/comments`);
      setComments(c);
      const mems = await api(`/projects/${i.project_id}/members`);
      setMembers(mems);
    } catch (err) {
      setError(err.message);
      notify(err.message, "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [issueId]);

  const addComment = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api(`/issues/${issueId}/comments`, {
        method: "POST",
        body: JSON.stringify({ body }),
      });
      setBody("");
      notify("Comment added", "success");
      load();
    } catch (err) {
      setError(err.message);
      notify(err.message, "error");
    }
  };

  const updateIssue = async (patch) => {
    setError("");
    try {
      await api(`/issues/${issueId}`, {
        method: "PATCH",
        body: JSON.stringify(patch),
      });
      notify("Issue updated", "success");
      load();
    } catch (err) {
      setError(err.message);
      notify(err.message, "error");
    }
  };

  const meRole = members.find((m) => m.user_id === me?.id)?.role;
  const isMaintainer = meRole === "maintainer";
  const memberNameById = Object.fromEntries(members.map((m) => [m.user_id, m.name]));
  const formatTs = (value) => {
    if (!value) return "Unknown time";
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return "Unknown time";
    return d.toLocaleString();
  };

  if (loading) return <div className="page">Loading...</div>;
  if (!issue) return <div className="page">Issue not found</div>;

  return (
    <div className="page">
      <h1>{issue.title}</h1>
      {error && <div className="error">{error}</div>}

      <div className="card">
        <div className="meta">
          <div><strong>Status:</strong> {issue.status}</div>
          <div><strong>Priority:</strong> {issue.priority}</div>
          <div><strong>Reporter:</strong> {memberNameById[issue.reporter_id] || `User ${issue.reporter_id}`}</div>
          <div><strong>Assignee:</strong> {issue.assignee_id ? (memberNameById[issue.assignee_id] || `User ${issue.assignee_id}`) : "Unassigned"}</div>
        </div>

        {isMaintainer && (
          <div className="controls">
            <label>Status</label>
            <select value={issue.status} onChange={(e) => updateIssue({ status: e.target.value })}>
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
            <label>Assignee</label>
            <select value={issue.assignee_id || ""} onChange={(e) => updateIssue({ assignee_id: e.target.value ? Number(e.target.value) : null })}>
              <option value="">Unassigned</option>
              {members.map((m) => <option key={m.user_id} value={m.user_id}>{m.name}</option>)}
            </select>
          </div>
        )}
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h3>Comments</h3>
        <ul className="list">
          {comments.map((c) => (
            <li key={c.id}>
              <div>{c.body}</div>
              <div className="muted">Author: {memberNameById[c.author_id] || `User ${c.author_id}`}</div>
              <div className="muted">Posted: {formatTs(c.created_at)}</div>
            </li>
          ))}
          {comments.length === 0 && <li className="muted">No comments yet</li>}
        </ul>

        <form onSubmit={addComment}>
          <label>Add Comment</label>
          <textarea value={body} onChange={(e) => setBody(e.target.value)} required />
          <button className="btn">Post Comment</button>
        </form>
      </div>
    </div>
  );
}
