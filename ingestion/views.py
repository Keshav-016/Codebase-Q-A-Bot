from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response


# A "view" is just a function that receives a request and returns a response.
# @api_view is a DRF decorator: it restricts the allowed HTTP methods and
# lets us return a DRF Response, which DRF turns into JSON for us.
@api_view(["GET"])
def health_check(request):
    """Report whether the API is up and whether it can reach the database."""
    try:
        # Run the cheapest possible query to prove Postgres is reachable.
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "ok"
    except Exception as exc:
        db_status = f"error: {exc.__class__.__name__}"

    healthy = db_status == "ok"
    return Response(
        {"status": "ok" if healthy else "degraded", "database": db_status},
        status=200 if healthy else 503,  # 503 = "Service Unavailable"
    )
@api_view(["GET"])
def ping_req(request):
    return Response(
            {"status": "ok" , "message":"pong"},
            status=200
        )