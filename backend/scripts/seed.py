"""Populate local development database with demo users, projects, issues, and comments."""

import argparse
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

# Allow running as: `python scripts/seed.py` from backend directory.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import base as _base  # noqa: F401
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.comment import Comment
from app.models.issue import Issue
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User


def ensure_user(db: Session, name: str, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    user = User(name=name, email=email, password_hash=get_password_hash(password))
    db.add(user)
    db.flush()
    return user


def ensure_project(db: Session, name: str, key: str, description: str) -> Project:
    project = db.query(Project).filter(Project.key == key).first()
    if project:
        return project
    project = Project(name=name, key=key, description=description)
    db.add(project)
    db.flush()
    return project


def ensure_membership(db: Session, project_id: int, user_id: int, role: str) -> None:
    member = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        .first()
    )
    if member:
        member.role = role
        return
    db.add(ProjectMember(project_id=project_id, user_id=user_id, role=role))


def reset_data(db: Session) -> None:
    db.query(Comment).delete()
    db.query(Issue).delete()
    db.query(ProjectMember).delete()
    db.query(Project).delete()
    db.query(User).delete()
    db.commit()


def seed_data(db: Session, seed: int = 42) -> None:
    random.seed(seed)

    users = [
        ensure_user(db, "Alice Maintainer", "alice@example.com", "pass123"),
        ensure_user(db, "Bob Member", "bob@example.com", "pass123"),
        ensure_user(db, "Carol Member", "carol@example.com", "pass123"),
        ensure_user(db, "Dave Maintainer", "dave@example.com", "pass123"),
    ]

    project_a = ensure_project(db, "IssueHub Platform", "IHUB", "Core platform work")
    project_b = ensure_project(db, "Website Revamp", "WEB", "Frontend refresh")

    ensure_membership(db, project_a.id, users[0].id, "maintainer")
    ensure_membership(db, project_a.id, users[1].id, "member")
    ensure_membership(db, project_a.id, users[2].id, "member")
    ensure_membership(db, project_b.id, users[3].id, "maintainer")
    ensure_membership(db, project_b.id, users[2].id, "member")

    db.flush()

    existing_issues = db.query(Issue).count()
    if existing_issues >= 10:
        db.commit()
        return

    statuses = ["open", "in_progress", "resolved", "closed"]
    priorities = ["low", "medium", "high", "critical"]
    titles = [
        "Login returns 500 on invalid token",
        "Filters reset after page refresh",
        "Comment editor trims first character",
        "Issue assignment fails for valid member",
        "Pagination skips records",
        "Project key allows lowercase unexpectedly",
        "Status badge color mismatch",
        "Search query is case sensitive",
        "Issue update timestamp not visible",
        "Assignee dropdown not sorted",
        "Slow load on project list",
        "Duplicate invite not handled cleanly",
    ]

    reporter_pool_a = [users[0], users[1], users[2]]
    assignee_pool_a = [None, users[0], users[1], users[2]]
    reporter_pool_b = [users[3], users[2]]
    assignee_pool_b = [None, users[3], users[2]]
    now = datetime.utcnow()

    def create_issue(project: Project, idx: int, reporter_pool: list[User], assignee_pool: list[User | None]) -> Issue:
        reporter = random.choice(reporter_pool)
        assignee = random.choice(assignee_pool)
        created = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        issue = Issue(
            project_id=project.id,
            title=titles[idx % len(titles)],
            description=f"Seeded issue #{idx + 1} for project {project.key}.",
            status=random.choice(statuses),
            priority=random.choice(priorities),
            reporter_id=reporter.id,
            assignee_id=assignee.id if assignee else None,
            created_at=created,
            updated_at=created + timedelta(hours=random.randint(1, 72)),
        )
        db.add(issue)
        db.flush()
        return issue

    issues: list[Issue] = []
    for i in range(7):
        issues.append(create_issue(project_a, i, reporter_pool_a, assignee_pool_a))
    for i in range(7, 12):
        issues.append(create_issue(project_b, i, reporter_pool_b, assignee_pool_b))

    comment_templates = [
        "I can reproduce this locally.",
        "Working on a fix branch now.",
        "Needs maintainer review before merge.",
        "Added more details and logs.",
    ]

    for issue in issues:
        commenters = reporter_pool_a if issue.project_id == project_a.id else reporter_pool_b
        for _ in range(2):
            author = random.choice(commenters)
            db.add(
                Comment(
                    issue_id=issue.id,
                    author_id=author.id,
                    body=random.choice(comment_templates),
                )
            )

    db.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed IssueHub demo data")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete current users/projects/issues/comments before seeding",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.reset:
            reset_data(db)
        seed_data(db)
        print("Seed complete.")
        print("Demo users: alice@example.com, bob@example.com, carol@example.com, dave@example.com")
        print("Demo password: pass123")
    finally:
        db.close()


if __name__ == "__main__":
    main()
