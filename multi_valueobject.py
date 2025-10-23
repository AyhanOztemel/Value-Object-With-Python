from sqlalchemy import TypeDecorator, String
import json
from sqlalchemy import text
class ValueType(TypeDecorator):
    """
    Herhangi bir sınıfı JSON olarak SQLite'de saklamak için genel TypeDecorator.
    Kullanım: Column(ValueType(Money))
    """
    impl = String  # SQLite TEXT sütunu

    def __init__(self, cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cls = cls  # Hangi value object sınıfı?

    def process_bind_param(self, value, dialect):
        # Python nesnesini -> JSON string
        if value is not None:
            return json.dumps(value.__dict__)
        return None

    def process_result_value(self, value, dialect):
        # JSON string -> Python nesnesi
        if value is not None:
            data = json.loads(value)
            return self.cls(**data)
        return None
    
class Money:
    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency

class Coordinates:
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

class FullName:
    def __init__(self, first, last):
        self.first = first
        self.last = last


from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(ValueType(Money))  # Value object

class Place(Base):
    __tablename__ = 'places'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    location = Column(ValueType(Coordinates))
    owner_name = Column(ValueType(FullName))

engine = create_engine('sqlite:///multi_ValueObject.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Ürün ekle
laptop = Product(
    name="Laptop",
    price=Money(amount=15000, currency="TRY")
)

# Mekan ekle
cafe = Place(
    name="Kahve Dükkanı",
    location=Coordinates(lat=41.0151, lng=28.9793),
    owner_name=FullName(first="Ayşe", last="Yılmaz")
)

session.add_all([laptop, cafe])
session.commit()


# Ürünü oku
p = session.query(Product).filter_by(name="Laptop").first()
print(p.price.amount)     # 15000
print(p.price.currency)   # TRY

# Mekanı oku
pl = session.query(Place).first()
print(pl.location.lat)    # 41.0151
print(pl.owner_name.first) # Ayşe


# Fiyatı 10.000'den yüksek olan ürünler
expensive = session.query(Product).filter(
    text("json_extract(price, '$.amount') > 10000")
).all()

for p in expensive:
    print(f"{p.name}: {p.price.amount} {p.price.currency}")

# Sahibi "Ayşe" olan mekanlar
ayse_places = session.query(Place).filter(
    text("json_extract(owner_name, '$.first') = 'Ayşe'")
).all()

for pl in ayse_places:
    print(pl.name)  # Kahve Dükkanı
print("----------------------------------------------------------------------")
"""✅ Alternatifler (değişiklik yapmadan değil ama)
Eğer hiçbir değişiklik yapmadan istiyorsanız, tek seçeneğiniz tüm kayıtları
Python tarafında filtrelemek:"""
products = session.query(Product).all()
expensive = [p for p in products if p.price and p.price.amount > 10000]
for p in expensive:
    print(f"{p.name}: {p.price.amount} {p.price.currency}")

#Bu, verimsizdir (özellikle büyük veri setlerinde) ama çalışır — ve json_extract kullanmaz.

print("----------------------------------------------------------------------")
p = session.query(Product).first()
print(p.price.amount)  # ✅ Bu çalışır — çünkü ORM bu nesneyi Python nesnesi olarak döndürdü.






        
