from fastapi import APIRouter

router: APIRouter = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post(path="/github")
async def github_webhook_handler(event) -> None:
    print(event)
