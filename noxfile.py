#! /usr/bin/env nox

import nox

@nox.session
def fmt(session):
    session.install("black")
    session.install("isort")
    session.run("black", "src")
    session.run("isort", "src")

# @nox.session
# def tests(session):
#     session.install('pytest')
#     session.run('pytest')
