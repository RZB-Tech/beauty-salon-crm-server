from dataclasses import dataclass

@dataclass
class Receipt:
    amount: int

receipts = [
    Receipt(100), Receipt(200), Receipt(300)
]
total = sum([receipt.amount for receipt in receipts])
print(total)