from fastapi import APIRouter, Depends, status
from src.core.dependencies.uow import UnitOfWork
from src.schemas.segmentation.create import SegmentationCreateSchema
from src.schemas.segmentation.response import SegmentationResponseSchema
from src.services.segmentation_service import SegmentationService

router = APIRouter()

def get_segmentation_service(uow: UnitOfWork = Depends(get_uow_with_context)) -> SegmentationService:
    return SegmentationService(uow=uow)

@router.post(
    "/", 
    response_model=SegmentationResponseSchema, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new service"
)
async def create(data: SegmentationCreateSchema,
                 segmenatationService: SegmentationService = Depends(get_segmentation_service)):
    return await segmenatationService.create(data)