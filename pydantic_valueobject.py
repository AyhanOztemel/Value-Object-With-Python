# pip install "sqlalchemy>=2" "pydantic>=2"
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List

from sqlalchemy import Float, String, Integer, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


# ================== DOMAIN ==================
@dataclass(frozen=True)
class PriceDC:
    amount: float
    currency: str


@dataclass
class ProductDC:
    id: Optional[int]
    name: str
    price: PriceDC


# ================== ORM =====================
class Base(DeclarativeBase):
    pass


class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    # DB tarafında iki ayrı kolon; domain tarafında PriceDC olarak expose edeceğiz
    _price_amount: Mapped[float] = mapped_column(Float, index=True, nullable=False)
    _price_currency: Mapped[str] = mapped_column(String(8), index=True, nullable=False)

    # --- Hybrid property benzeri düz property ---
    @property
    def price(self) -> PriceDC:
        return PriceDC(self._price_amount, self._price_currency)

    @price.setter
    def price(self, val: PriceDC):
        self._price_amount = val.amount
        self._price_currency = val.currency


# ================== SETUP ===================
engine = create_engine("sqlite:///hybrid_price_demo.db", echo=False)
Base.metadata.create_all(engine)


# ================== HELPERS =================
def _to_dc(orm: ProductModel) -> ProductDC:
    return ProductDC(
        id=orm.id,
        name=orm.name,
        price=PriceDC(orm._price_amount, orm._price_currency),
    )


# ================== REPO-LIKE API ===========
def add_product(p: ProductDC) -> ProductDC:
    """ProductDC -> DB insert -> ProductDC (id ile döndür)."""
    with Session(engine) as s:
        orm = ProductModel(
            name=p.name,
            _price_amount=p.price.amount,
            _price_currency=p.price.currency,
        )
        # İstersen şu da eşdeğer (setter devrede):
        # orm = ProductModel(name=p.name, _price_amount=0, _price_currency="")
        # orm.price = p.price

        s.add(orm)
        s.commit()
        s.refresh(orm)
        return _to_dc(orm)


def add_products_bulk(items: List[ProductDC]) -> List[ProductDC]:
    with Session(engine) as s:
        orms = [
            ProductModel(
                name=p.name,
                _price_amount=p.price.amount,
                _price_currency=p.price.currency,
            )
            for p in items
        ]
        s.add_all(orms)
        s.commit()
        # id’ler yazıldı; tekrar select yerine direkt map’liyoruz
        return [_to_dc(o) for o in orms]


def get_all_products() -> List[ProductDC]:
    with Session(engine) as s:
        rows = s.execute(select(ProductModel).order_by(ProductModel.id.asc())).scalars().all()
        return [_to_dc(r) for r in rows]


def get_product_by_id(pid: int) -> Optional[ProductDC]:
    with Session(engine) as s:
        row = s.get(ProductModel, pid)
        return _to_dc(row) if row else None


# ================== DEMO ====================
if __name__ == "__main__":
    # 1) Tek tek ekleme
    add_product(ProductDC(id=None, name="Coffee Mug", price=PriceDC(129.9, "TRY")))
    add_product(ProductDC(id=None, name="Tea Cup",    price=PriceDC(89.5,  "TRY")))

    # 2) Toplu ekleme (3 ürün)
    bulk_inserted = add_products_bulk([
        ProductDC(id=None, name="Glass",     price=PriceDC(49.0,   "TRY")),
        ProductDC(id=None, name="Thermos",   price=PriceDC(399.0,  "TRY")),
        ProductDC(id=None, name="Kettle",    price=PriceDC(799.99, "TRY")),
    ])

    # === get_all ===
    all_products = get_all_products()
    print("All products:")
    for p in all_products:
        print(f"- #{p.id}: {p.name} | {p.price.amount} {p.price.currency}")

    # === get_by_id === (örnek: 1 ve 5)
    p1 = get_product_by_id(1)
    p5 = get_product_by_id(5)
    print("\nget_by_id(1):", p1)
