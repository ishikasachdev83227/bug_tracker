from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db, get_current_user
from app.schemas.project import (
    ProjectCreate,
    ProjectOut,
    ProjectMemberAdd,
    ProjectMemberOut,
    ProjectMemberOnboard,
    ProjectMemberUpdate,
)
from app.crud import project as project_crud
from app.models.project_member import ProjectMember
from app.models.user import User
from app.api.errors import api_error
from app.core.security import get_password_hash

router = APIRouter()


def get_membership_or_403(db: Session, project_id: int, user_id: int) -> ProjectMember:
    member = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        .first()
    )
    if not member:
        raise api_error(status.HTTP_403_FORBIDDEN, "forbidden", "Project membership required")
    return member


def require_maintainer(db: Session, project_id: int, user_id: int) -> ProjectMember:
    member = get_membership_or_403(db, project_id, user_id)
    if member.role != "maintainer":
        raise api_error(status.HTTP_403_FORBIDDEN, "forbidden", "Maintainer role required")
    return member

@router.post("", response_model=ProjectOut)
def create_project(data: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    memberships = db.query(ProjectMember).filter(ProjectMember.user_id == current_user.id).all()
    if memberships and all(m.role != "maintainer" for m in memberships):
        raise api_error(
            status.HTTP_403_FORBIDDEN,
            "forbidden",
            "Only maintainers can create projects",
        )
    try:
        project = project_crud.create_project(db, data.name, data.key, data.description, current_user.id)
        return project
    except IntegrityError:
        db.rollback()
        raise api_error(status.HTTP_400_BAD_REQUEST, "project_key_taken", "Project key already exists")

@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return project_crud.list_user_projects(db, current_user.id)

@router.get("/maintained", response_model=list[ProjectOut])
def list_maintained_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return project_crud.list_maintained_projects(db, current_user.id)

@router.post("/{project_id}/members")
def add_member(project_id: int, data: ProjectMemberAdd, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_maintainer(db, project_id, current_user.id)
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise api_error(status.HTTP_404_NOT_FOUND, "user_not_found", "User not found")
    existing = db.query(ProjectMember).filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user.id).first()
    if existing:
        existing.role = data.role
        db.commit()
        return {"ok": True}
    new_member = ProjectMember(project_id=project_id, user_id=user.id, role=data.role)
    db.add(new_member)
    db.commit()
    return {"ok": True}


@router.post("/{project_id}/members/onboard")
def onboard_member(
    project_id: int,
    data: ProjectMemberOnboard,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_maintainer(db, project_id, current_user.id)
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise api_error(
            status.HTTP_400_BAD_REQUEST,
            "email_taken",
            "User already exists. Use invite by email for existing users.",
        )

    user = User(name=data.name, email=data.email, password_hash=get_password_hash(data.password))
    db.add(user)
    db.flush()
    db.add(ProjectMember(project_id=project_id, user_id=user.id, role=data.role))
    db.commit()
    return {"ok": True, "user_id": user.id}

@router.get("/{project_id}/members", response_model=list[ProjectMemberOut])
def list_members(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_membership_or_403(db, project_id, current_user.id)
    rows = (
        db.query(ProjectMember, User)
        .join(User, User.id == ProjectMember.user_id)
        .filter(ProjectMember.project_id == project_id)
        .all()
    )
    return [
        ProjectMemberOut(user_id=u.id, name=u.name, email=u.email, role=pm.role)
        for pm, u in rows
    ]


@router.patch("/{project_id}/members/{user_id}")
def update_member_role(
    project_id: int,
    user_id: int,
    data: ProjectMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_maintainer(db, project_id, current_user.id)
    member = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        .first()
    )
    if not member:
        raise api_error(status.HTTP_404_NOT_FOUND, "member_not_found", "Project member not found")
    member.role = data.role
    db.commit()
    return {"ok": True}


@router.delete("/{project_id}/members/{user_id}")
def remove_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_maintainer(db, project_id, current_user.id)
    member = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        .first()
    )
    if not member:
        raise api_error(status.HTTP_404_NOT_FOUND, "member_not_found", "Project member not found")

    if member.role == "maintainer":
        maintainers_count = (
            db.query(ProjectMember)
            .filter(ProjectMember.project_id == project_id, ProjectMember.role == "maintainer")
            .count()
        )
        if maintainers_count <= 1:
            raise api_error(
                status.HTTP_400_BAD_REQUEST,
                "last_maintainer",
                "Cannot remove the last maintainer from a project",
            )

    db.delete(member)
    db.commit()
    return {"ok": True}
