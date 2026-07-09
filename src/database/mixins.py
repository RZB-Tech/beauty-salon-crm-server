from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class TenantMixin:
    @declared_attr
    def tenant_id(cls) -> Mapped[int]:
        return mapped_column(ForeignKey("tenants.id", ondelete = "cascade"), nullable = False, index = True)