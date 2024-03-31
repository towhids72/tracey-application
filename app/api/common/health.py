from fastapi import APIRouter

router = APIRouter(
    prefix='/health',
    tags=['Health']
)


@router.get(path='', response_model=dict[str, str])
async def health_check():
    return {"status": "ok"}
