import math
import secrets
from sqlalchemy.exc import IntegrityError
from src.core.dependencies.uow import UnitOfWork
from src.exceptions.client_exceptions import ClientNotFound
from src.exceptions.general_exceptions import ObjectIsArchived
from src.repository.giftCard.giftCard_model import GiftCard
from src.repository.receipt.receipt_model import Receipt, ReceiptItem, ReceiptStatus, ReceiptType
from src.repository.transaction.transaction_model import Transaction, TransactionCategory, TransactionMethod, TransactionType
from src.schemas.base import RequestAllObject
from src.schemas.giftCard.create import GiftCardCreateSchema

ALLOWED_CHARS = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
MAX_CODE_GENERATION_ATTEMPTS = 5

class GiftCardService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    @staticmethod
    def _generate_gift_card_code() -> str:
        """
        Generates a human-readable code like: XK-8X4N-92KP
        Excludes ambiguous characters (0, O, 1, I, L).
        """
        prefix = "".join(secrets.choice(ALLOWED_CHARS) for _ in range(2))
        chunk1 = "".join(secrets.choice(ALLOWED_CHARS) for _ in range(4))
        chunk2 = "".join(secrets.choice(ALLOWED_CHARS) for _ in range(4))
        return f"{prefix}-{chunk1}-{chunk2}"

    async def _create_gift_card_with_unique_code(self, newObject: GiftCard) -> GiftCard:
        """
        Inserts newObject inside a SAVEPOINT, retrying with a freshly generated
        code if it collides with an existing one (uq_gift_card_code), without
        aborting the rest of the request's transaction (receipt/transaction creation).
        """
        self.uow.db.add(newObject)

        for attempt in range(1, MAX_CODE_GENERATION_ATTEMPTS + 1):
            newObject.code = self._generate_gift_card_code()
            try:
                async with self.uow.db.begin_nested():
                    await self.uow.db.flush()
                break
            except IntegrityError as exc:
                constraint_name = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
                if constraint_name != "uq_gift_card_code" or attempt == MAX_CODE_GENERATION_ATTEMPTS:
                    raise

        await self.uow.db.refresh(newObject)
        return newObject

    async def create(self, data: GiftCardCreateSchema) -> GiftCard:
        if data.client_id is not None:
            checkClient = await self.uow.clients.get(data.client_id)
            if checkClient is None: raise ClientNotFound(data.client_id)
            if checkClient.archived: raise ObjectIsArchived(data.client_id, "clients")

        giftCardData = data.model_dump(exclude = {"payment_method"}, exclude_unset = True)
        newObject = GiftCard(**giftCardData)
        newObject.remain_amount = data.initial_amount

        receiptData = Receipt(
            receipt_type = ReceiptType.DIRECT_SALE,
            client_id = data.client_id if data.client_id is not None else None,
            subtotal_amount = data.initial_amount,
            total_amount = data.initial_amount,
            status = ReceiptStatus.PAID
        )
        receipt = await self.uow.receipts.create(receiptData)

        newObject.receipt_id = receipt.id
        giftCard = await self._create_gift_card_with_unique_code(newObject)

        receiptItem = ReceiptItem(
            receipt_id = receipt.id,
            giftCard_id = giftCard.id,
            base_price = data.initial_amount,
            final_price = data.initial_amount,
            quantity = 1
        )
        receipt.items.append(receiptItem)

        await self.uow.transactions.create(Transaction(
            receipt_id = receipt.id,
            amount = data.initial_amount,
            type = TransactionType.INCOME,
            method = TransactionMethod(data.payment_method),
            category = TransactionCategory.GIFT_CARD,
            auto_generated = True
        ))

        return giftCard

    # async def update(self, data: PromotionUpdateSchema) -> Promotion:
    #     promotion = await self.uow.promotions.get(data.id)
    #     if promotion is None: raise PromotionNotFound(data.id)
    #     if promotion.archived: raise ObjectIsArchived(data.id, "promotions")

    #     effective_promo_type = data.promo_type if data.promo_type is not None else promotion.promo_type

    #     if effective_promo_type == PromotionType.PERCENTAGE and data.discount_value is None:
    #         if promotion.discount_value > 100 or promotion.discount_value < 0:
    #             raise PromotionDiscountPercentageExceed(promotion.discount_value)
    #     if effective_promo_type == PromotionType.PERCENTAGE and data.discount_value is not None and (
    #         data.discount_value > 100 or data.discount_value < 0
    #     ):
    #         raise PromotionDiscountPercentageExceed(data.discount_value)

    #     if data.service_id:
    #         checkIfUsing = await self.uow.promotions.get_by_object(data.service_id, "service")
    #         if checkIfUsing is not None and checkIfUsing.is_active:
    #             raise PromotionTargetConflict("service", data.service_id, checkIfUsing.id, checkIfUsing.name)
            
    #         await self._unusable_object(data.service_id, "services")

    #     if data.material_id:
    #         checkIfUsing = await self.uow.promotions.get_by_object(data.material_id, "material")
    #         if checkIfUsing is not None and checkIfUsing.is_active:
    #             raise PromotionTargetConflict("material", data.material_id, checkIfUsing.id, checkIfUsing.name)
            
    #         await self._unusable_object(data.material_id, "materials")

    #     data.promo_type = effective_promo_type
    #     dataDict = data.model_dump(exclude = {"id"}, exclude_unset = True)
    #     result = await self.uow.promotions.update(data.id, **dataDict)
    #     if result is None: raise CannotUpdate(data.id, "promotions")
    #     return result

    # async def get(self, id: int) -> Promotion:
    #     promotion = await self.uow.promotions.get(id)
    #     if promotion is None: raise PromotionNotFound(id)
    #     return promotion

    # async def get_all(self, data: RequestAllObject) -> dict:
    #     items, total_items = await self.uow.promotions.get_all(data)

    #     total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
    #     return {
    #         "items": items,
    #         "page": data.page,
    #         "pageSize": data.pageSize,
    #         "totalItems": total_items,
    #         "totalPages": total_pages
    #     }