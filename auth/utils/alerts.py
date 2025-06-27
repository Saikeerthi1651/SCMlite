from fastapi.responses import JSONResponse

def alert_response(message: str, alert_type: str = "info", status_code: int = 200, **kwargs):
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success" if status_code < 400 else "error",
            "message": message,
            "alert": {
                "type": alert_type,
                "message": message
            },
            **kwargs
        }
    )