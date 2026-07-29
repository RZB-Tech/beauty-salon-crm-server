from src.core.dependencies.uow import UnitOfWork
from src.repository.employee.segments_model import Segmentation
from src.schemas.segmentation.create import SegmentationCreateSchema

class SegmentationService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create(self, payload: SegmentationCreateSchema) -> Segmentation:
        new_segment = Segmentation(
            name=payload.name,
            description=payload.description,
            criteria=payload.criteria,
            client_ids=payload.client_ids
        )

        self.uow.db.add(new_segment)
        
        await self.uow.db.commit()
        
        await self.uow.db.refresh(new_segment)
        
        return new_segment