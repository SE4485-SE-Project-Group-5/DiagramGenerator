import os
import shutil
import tempfile

import wget
from invoke import task

TEMP = tempfile.gettempdir()


def remove(path: str):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


def copy(from_path: str, to_path: str):
    if os.path.isdir(from_path):
        shutil.copytree(from_path, to_path)
    elif os.path.isfile(from_path):
        shutil.copy(from_path, to_path)


def mkdir(path: str):
    os.makedirs(path)


@task
def clean(c, bytecode=False, build=False, lib=False, assets=False, all=False):
    if all or bytecode or not any((build, lib, assets)):
        c.run("pyclean .")

    if all or assets:
        remove("templates")
        remove("static")

    if all or build:
        remove("build")
        remove("main.spec")
        remove("dist")

    if all or lib:
        remove("lib")


@task
def start(c):
    c.run("python main.py")


@task
def build_ui(c):
    # Remove assets
    clean(c, assets=True)

    # Build React app
    with c.cd("react-ui"):
        c.run("yarn build")

    # Transfer assets
    mkdir("templates")
    copy("react-ui/build/index.html", "templates/index.html")
    copy("react-ui/build/static", "static")


@task
def build(c):  # TODO: Fix build issues
    # Build UI
    build_ui(c)

    # Clean previous build
    clean(c, build=True)

    # Build exe with Pyinstaller
    c.run("pyi-makespec main.py")
    c.run("python -O -m PyInstaller --clean --debug=all --add-data \"templates;templates\" --add-data \"static;static\" --distpath \"lib\" -y main.py")


@task
def package(c):
    # Build
    if not os.path.exists("lib/main"):
        build(c)

    if not os.path.exists("lib/graphviz-2.38.msi"):
        wget.download(
            "https://graphviz.gitlab.io/_pages/Download/windows/graphviz-2.38.msi",
            out="lib/graphviz-2.38.msi"
        )

    # Get version number
    version = c.run("poetry version -s").stdout.rstrip()

    # Package with Inno Setup
    c.run(f'iscc /DMyAppVersion="{version}" package.iss')


@task
def release(c):
    # Get version number
    version = c.run("poetry version -s").stdout.rstrip()

    # Upload release with GitHub CLI tool
    c.run(
        f'gh release create v{version} dist/DiagramGenerator-{version}-setup.exe -t "Diagram Generator v{version}" -n "" -p'
    )
