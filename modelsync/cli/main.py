import typer
from modelsync.core.versioning import init_repo, commit_changes

app = typer.Typer()

@app.command()
def init():
    init_repo()

@app.command()
def commit(message: str):
    commit_changes(message)

if __name__ == "__main__":
    app()