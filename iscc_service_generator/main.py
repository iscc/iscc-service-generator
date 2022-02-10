import uvicorn


def run_server():
    uvicorn.run(
        "iscc_service_generator.asgi:application",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    uvicorn.run(
        "iscc_service_generator.asgi:application",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
