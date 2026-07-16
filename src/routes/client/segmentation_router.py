from fastapi import APIRouter, Depends, status
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import UnitOfWork, make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.segmentation.create import SegmentationCreateSchema
from src.schemas.segmentation.response import SegmentationResponseSchema
from src.services.client.segmentation_service import SegmentationService

router = APIRouter()

get_segmentation_service = make_service_dependency(SegmentationService)

@router.post(
    "",
    response_model=SegmentationResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new service",
    dependencies=[Depends(require_permission([PermissionCode.SEGMENTATION_CREATE]))]
)
async def create(data: SegmentationCreateSchema,
                 segmenatationService: SegmentationService = Depends(get_segmentation_service)):
    return await segmenatationService.create(data)