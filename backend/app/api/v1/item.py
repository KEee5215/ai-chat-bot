from typing import Dict, Annotated
from fastapi import APIRouter
from fastapi.params import Depends
from app.utils.response import success_response

router = APIRouter(prefix="/item", tags=["物品"])

def page_common(page: int = 1, page_size: int = 10):
    return {"page": page, "pageSize": page_size}

@router.get("/list")
async def get_item_page(page_params: Annotated[dict,Depends(page_common)]):
    """分页查询物品"""
    page = page_params.get("page")
    size = page_params.get("pageSize")
    return success_response(data={"页码": page, "每页尺寸": size})
