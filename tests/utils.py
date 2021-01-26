import os

from opencoverage.reporter import CoverageReporter

DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


def read_data(name):
    with open(os.path.join(DATA_DIR, name), "rb") as fi:
        return fi.read()


async def add_coverage(
    settings, db, scm, organization, repo, branch, commit, coverage_filename
):
    reporter = CoverageReporter(
        settings=settings,
        db=db,
        scm=scm,
        organization=organization,
        repo=repo,
        branch=branch,
        commit=commit,
    )
    await reporter(coverage_data=read_data(coverage_filename))
