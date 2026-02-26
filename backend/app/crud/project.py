from sqlalchemy.orm import Session
from app.models.project import Project
from app.models.project_member import ProjectMember


def create_project(db: Session, name: str, key: str, description: str | None, owner_id: int) -> Project:
    project = Project(name=name, key=key, description=description)
    db.add(project)
    db.commit()
    db.refresh(project)
    member = ProjectMember(project_id=project.id, user_id=owner_id, role="maintainer")
    db.add(member)
    db.commit()
    return project


def list_user_projects(db: Session, user_id: int):
    return (
        db.query(Project)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .filter(ProjectMember.user_id == user_id)
        .all()
    )


def list_maintained_projects(db: Session, user_id: int):
    return (
        db.query(Project)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .filter(ProjectMember.user_id == user_id, ProjectMember.role == "maintainer")
        .all()
    )
