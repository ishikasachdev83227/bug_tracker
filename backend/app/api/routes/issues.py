from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.issue import IssueCreate, IssueOut, IssueUpdate
from app.crud import issue as issue_crud
from app.models.project_member import ProjectMember
from app.models.issue import Issue
from app.models.user import User
from app.api.errors import api_error

router = APIRouter()


def require_membership(db: Session, project_id: int, user_id: int):
    member = db.query(ProjectMember).filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"error": {"code": "forbidden", "message": "Project membership required"}})
    return member

@router.get("/projects/{project_id}/issues", response_model=list[IssueOut])
def list_issues(
    project_id: int,
    q: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    assignee: int | None = None,
    sort: str | None = Query(default=None),
    limit: int | None = Query(default=20, ge=1, le=100),
    offset: int | None = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_membership(db, project_id, current_user.id)
    return issue_crud.list_project_issues(db, project_id, q, status, priority, assignee, sort, limit, offset)

@router.post("/projects/{project_id}/issues", response_model=IssueOut)
def create_issue(project_id: int, data: IssueCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    member = require_membership(db, project_id, current_user.id)
    if member.role != "maintainer":
        raise api_error(status.HTTP_403_FORBIDDEN, "forbidden", "Only maintainers can create issues")
    if data.assignee_id is not None:
        assignee_member = db.query(ProjectMember).filter(ProjectMember.project_id == project_id, ProjectMember.user_id == data.assignee_id).first()
        if not assignee_member:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": {"code": "invalid_assignee", "message": "Assignee must be a project member"}})
    return issue_crud.create_issue(db, project_id, data.title, data.description, data.priority, current_user.id, data.assignee_id)

@router.get("/issues/{issue_id}", response_model=IssueOut)
def get_issue(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"code": "not_found", "message": "Issue not found"}})
    require_membership(db, issue.project_id, current_user.id)
    return issue

@router.patch("/issues/{issue_id}", response_model=IssueOut)
def update_issue(issue_id: int, data: IssueUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"code": "not_found", "message": "Issue not found"}})
    member = require_membership(db, issue.project_id, current_user.id)
    is_reporter = issue.reporter_id == current_user.id
    is_maintainer = member.role == "maintainer"

    if (data.status is not None or data.assignee_id is not None) and not is_maintainer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"error": {"code": "forbidden", "message": "Maintainer role required to change status or assignee"}})

    if not is_reporter and not is_maintainer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"error": {"code": "forbidden", "message": "Only reporter or maintainer can update"}})

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(issue, field, value)
    if data.model_dump(exclude_unset=True):
        from datetime import datetime
        issue.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(issue)
    return issue

@router.delete("/issues/{issue_id}")
def delete_issue(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"code": "not_found", "message": "Issue not found"}})
    member = require_membership(db, issue.project_id, current_user.id)
    is_reporter = issue.reporter_id == current_user.id
    is_maintainer = member.role == "maintainer"
    if not is_reporter and not is_maintainer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"error": {"code": "forbidden", "message": "Only reporter or maintainer can delete"}})
    db.delete(issue)
    db.commit()
    return {"ok": True}
