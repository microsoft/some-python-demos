def main() -> None:
    import uvicorn

    uvicorn.run("maf.app:app", host="127.0.0.1", port=8001, reload=True)
