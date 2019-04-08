from invoke import task
from fabric2 import Connection

@task
def deploy(c, restart=False, sync=False):
    c.run("git push --all")
    conn = Connection("trotsky")
    with conn.cd("src/pyborg-1up"):
        conn.run("git fetch")
        conn.run("git stash")
        conn.run("git pull")
        conn.run("git stash pop")
        if sync:
            conn.run("~/.local/bin/pipenv sync") # they all use the same pipenv managed virtualenv
        if restart:
            for unit in ["pyborg_discord", "pyborg_http", "pyborg_twitter", "pyborg_mastodon"]:
                conn.sudo("systemctl restart {}".format(unit), pty=True)
        print("Deploy Completed.")

@task
def release(c, clean=True):
    "cut a release of pyborg"
    with c.cd("pyborg"):
        if clean:
            c.run("rm -rf build")
        c.run("pipenv run python --version", echo=True)
        c.run("pipenv run python setup.py bdist_wheel sdist")
        print("now run `gpg -ba` on the files in dist/ and upload with `twine`")

@task
def bandit(c):
    c.run("pipenv run bandit --exclude=build,test -s B311 -r pyborg", pty=True)

@task
def test(c):
    c.run("tox")

@task
def outdated(c):
    c.run("pipenv run pip list -o --format=columns")

@task
def lint(c, mypy=True):
    if mypy:
        c.run("pipenv run mypy pyborg/pyborg", warn=True)
    c.run("flake8 --config=tox.ini --count pyborg", warn=True)