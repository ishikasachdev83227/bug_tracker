from sqlalchemy.orm import Session
from sqlalchemy import or_, case
from app.models.issue import Issue

PRIORITY_ORDER = {"low": 1, "medium": 2, "high": 3, "critical": 4}
STATUS_ORDER = {"open": 1, "in_progress": 2, "resolved": 3, "closed": 4}


def list_project_issues(db: Session, project_id: int, q: str | None, status: str | None, priority: str | None, assignee: int | None, sort: str | None, limit: int | None, offset: int | None):
    query = db.query(Issue).filter(Issue.project_id == project_id)
    if q:
        query = query.filter(Issue.title.ilike(f"%{q}%"))
    if status:
        query = query.filter(Issue.status == status)
    if priority:
        query = query.filter(Issue.priority == priority)
    if assignee is not None:
        query = query.filter(Issue.assignee_id == assignee)

    if sort == "created_at":
        query = query.order_by(Issue.created_at.desc())
    elif sort == "priority":
        query = query.order_by(case(PRIORITY_ORDER, value=Issue.priority))
    elif sort == "status":
        query = query.order_by(case(STATUS_ORDER, value=Issue.status))
    else:
        query = query.order_by(Issue.created_at.desc())

    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)

    return query.all()


def create_issue(db: Session, project_id: int, title: str, description: str | None, priority: str, reporter_id: int, assignee_id: int | None):
    issue = Issue(project_id=project_id, title=title, description=description, priority=priority, reporter_id=reporter_id, assignee_id=assignee_id)
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue
