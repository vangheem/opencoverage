import psycopg2.errors
import sqlalchemy as sa
import sqlalchemy.exc
import sqlalchemy.orm.exc
from asyncom.om import OMBase
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base(cls=OMBase)


class Organization(Base):  # type: ignore
    __tablename__ = "organizations"

    name = sa.Column(sa.String, primary_key=True)

    creation_date = sa.Column(sa.DateTime)
    modification_date = sa.Column(sa.DateTime)
    installation_id = sa.Column(sa.String)


class Repo(Base):  # type: ignore
    __tablename__ = "repos"

    organization = sa.Column(sa.String, primary_key=True)
    name = sa.Column(sa.String, primary_key=True)

    creation_date = sa.Column(sa.DateTime)
    modification_date = sa.Column(sa.DateTime)


class Branch(Base):  # type: ignore
    __tablename__ = "branches"

    organization = sa.Column(sa.String, primary_key=True, index=True)
    repo = sa.Column(sa.String, primary_key=True, index=True)
    name = sa.Column(sa.String, primary_key=True)

    creation_date = sa.Column(sa.DateTime)
    modification_date = sa.Column(sa.DateTime)

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["organization", "repo"], [Repo.organization, Repo.name], ondelete="SET NULL"
        ),
        sa.Index(
            "index_branches_repo_name",
            repo,
            name,
        ),
    )


class PullRequest(Base):  # type: ignore
    __tablename__ = "pullrequests"

    organization = sa.Column(sa.String, primary_key=True, index=True)
    repo = sa.Column(
        sa.String,
        primary_key=True,
        index=True,
    )
    id = sa.Column(sa.Integer, primary_key=True)
    base = sa.Column(sa.String)
    head = sa.Column(sa.String)

    creation_date = sa.Column(sa.DateTime)
    modification_date = sa.Column(sa.DateTime)

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["organization", "repo", "base"],
            [Branch.organization, Branch.repo, Branch.name],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["organization", "repo", "head"],
            [Branch.organization, Branch.repo, Branch.name],
            ondelete="SET NULL",
        ),
    )


class Commit(Base):  # type: ignore
    __tablename__ = "commits"

    organization = sa.Column(sa.String, primary_key=True, index=True)
    repo = sa.Column(sa.String, primary_key=True, index=True)
    branch = sa.Column(sa.String, primary_key=True, index=True)
    hash = sa.Column(sa.String, primary_key=True, index=True)

    creation_date = sa.Column(sa.DateTime)
    modification_date = sa.Column(sa.DateTime)

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["organization", "repo", "branch"],
            [Branch.organization, Branch.repo, Branch.name],
            ondelete="SET NULL",
        ),
    )


ROOT_PROJECT = "/"


class CoverageReport(Base):  # type: ignore
    __tablename__ = "coveragereports"

    organization = sa.Column(sa.String, index=True, primary_key=True)
    repo = sa.Column(sa.String, index=True, primary_key=True)
    branch = sa.Column(sa.String, index=True, primary_key=True)
    commit_hash = sa.Column(sa.String, index=True, primary_key=True)

    # projects are a way of handling mono-repo setups where
    # you want to track coverage of multiple sub-folders seperately
    project = sa.Column(sa.String, index=True, primary_key=True, default=ROOT_PROJECT)

    lines_valid = sa.Column(sa.Integer)
    lines_covered = sa.Column(sa.Integer)
    line_rate = sa.Column(sa.Float)
    branches_valid = sa.Column(sa.Integer)
    branches_covered = sa.Column(sa.Integer)
    branch_rate = sa.Column(sa.Integer)
    complexity = sa.Column(sa.Integer)

    creation_date = sa.Column(sa.DateTime)
    modification_date = sa.Column(sa.DateTime)

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["organization", "repo", "branch", "commit_hash"],
            [Commit.organization, Commit.repo, Commit.branch, Commit.hash],
            ondelete="SET NULL",
        ),
    )


class CoverageRecord(Base):  # type: ignore
    __tablename__ = "coveragerecords"

    filename = sa.Column(sa.String, primary_key=True)
    organization = sa.Column(sa.String, index=True, primary_key=True)
    repo = sa.Column(sa.String, index=True, primary_key=True)
    branch = sa.Column(sa.String, index=True, primary_key=True)
    commit_hash = sa.Column(sa.String, index=True, primary_key=True)
    project = sa.Column(sa.String, index=True, primary_key=True, default=ROOT_PROJECT)

    lines = sa.Column(JSONB)

    line_rate = sa.Column(sa.Float)
    branch_rate = sa.Column(sa.Integer)
    complexity = sa.Column(sa.Integer)

    creation_date = sa.Column(sa.DateTime)
    modification_date = sa.Column(sa.DateTime)

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["organization", "repo", "branch", "commit_hash", "project"],
            [
                CoverageReport.organization,
                CoverageReport.repo,
                CoverageReport.branch,
                CoverageReport.commit_hash,
                CoverageReport.project,
            ],
            ondelete="SET NULL",
        ),
    )


class CoverageReportPullRequest(Base):  # type: ignore
    __tablename__ = "coveragereportpullrequests"

    organization = sa.Column(sa.String, index=True, primary_key=True)
    repo = sa.Column(sa.String, index=True, primary_key=True)
    branch = sa.Column(sa.String, index=True, primary_key=True)
    commit_hash = sa.Column(sa.String, index=True, primary_key=True)
    project = sa.Column(sa.String, index=True, primary_key=True, default=ROOT_PROJECT)

    pull = sa.Column(sa.Integer, primary_key=True)
    pull_diff = sa.Column(JSONB)

    check_id = sa.Column(sa.String)
    comment_id = sa.Column(sa.String)

    line_rate = sa.Column(sa.Float)

    creation_date = sa.Column(sa.DateTime)
    modification_date = sa.Column(sa.DateTime)

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["organization", "repo", "branch", "commit_hash", "project"],
            [
                CoverageReport.organization,
                CoverageReport.repo,
                CoverageReport.branch,
                CoverageReport.commit_hash,
                CoverageReport.project,
            ],
            ondelete="SET NULL",
        ),
    )


class Task(Base):  # type: ignore
    __tablename__ = "tasks"

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    name = sa.Column(sa.String)
    data = sa.Column(sa.LargeBinary)
    status = sa.Column(sa.String, index=True)
    info = sa.Column(sa.String)

    creation_date = sa.Column(sa.DateTime, index=True)
    modification_date = sa.Column(sa.DateTime, index=True)


MODELS = (
    Organization,
    Repo,
    Branch,
    PullRequest,
    Commit,
    CoverageReport,
    CoverageRecord,
    CoverageReportPullRequest,
    Task,
)


def init(url: str) -> Engine:
    engine = sa.create_engine(url)
    for model in MODELS:
        try:
            model.__table__.create(engine)  # type: ignore
        except (
            psycopg2.errors.DuplicateTable,
            sqlalchemy.exc.OperationalError,
            sqlalchemy.exc.ProgrammingError,
        ):
            ...
    return engine
