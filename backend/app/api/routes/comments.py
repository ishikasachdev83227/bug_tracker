from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.comment import CommentCreate, CommentOut
from app.crud import comment as comment_crud
from app.models.issue import Issue
from app.models.project_member import ProjectMember
from app.models.user import User

router = APIRouter()

@router.get("/issues/{issue_id}/comments", response_model=list[CommentOut])
def list_comments(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"code": "not_found", "message": "Issue not found"}})
    member = db.query(ProjectMember).filter(ProjectMember.project_id == issue.project_id, ProjectMember.user_id == current_user.id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"error": {"code": "forbidden", "message": "Project membership required"}})
    return issue.comments

@router.post("/issues/{issue_id}/comments", response_model=CommentOut)
def add_comment(issue_id: int, data: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"code": "not_found", "message": "Issue not found"}})
    member = db.query(ProjectMember).filter(ProjectMember.project_id == issue.project_id, ProjectMember.user_id == current_user.id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"error": {"code": "forbidden", "message": "Project membership required"}})
    return comment_crud.create_comment(db, issue_id, current_user.id, data.body)
