from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: float
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

    def __str__(self):
        return f"{self.amount} {self.currency}"

# Kullanım örneği:
money1 = Money(amount=100, currency="USD")
money2 = Money(amount=100.0, currency="USD")
money3 = Money(amount=200.0, currency="EUR")

# Eşitlik kontrolü
print(money1 == money2)  # True
print(money1 == money3)  # False

# Değişmezlik kontrolü
money1.amount = 200.0  # Hata: frozen=True nedeniyle değişiklik yapılamaz
