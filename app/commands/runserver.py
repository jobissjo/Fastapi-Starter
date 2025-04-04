import typer
import uvicorn

def run(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(8000, help="Port to run the server on"),
    reload: bool = typer.Option(True, "--reload/--no-reload", help="Enable auto-reload")
):
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)
