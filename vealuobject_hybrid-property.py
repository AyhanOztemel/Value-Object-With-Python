from sqlalchemy import TypeDecorator, String, create_engine, Column, Integer, func, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.hybrid import hybrid_property
import json

Base = declarative_base()

from sqlalchemy import TypeDecorator, String
import json
from sqlalchemy.sql import column

class ValueType(TypeDecorator):
    """
    SQLAlchemy TypeDecorator sınıfı: Python nesnelerini veritabanında JSON string olarak saklamak,
    ve gerektiğinde tekrar Python nesnesine dönüştürmek için kullanılır.
    Örnek: Money, Coordinates gibi Value Object'leri SQLite TEXT sütununda saklamak.
    """

    # 1. Temel SQL Tipi: Bu TypeDecorator hangi temel SQL tipine karşılık geliyor?
    impl = String  # SQLite'da TEXT sütunu demektir.

    # 2. Önbellek Uyumluluğu: SQLAlchemy 2.0+ sürümünde SQL ifadeleri önbelleğe alınır.
    #    Bu tipin durumu (state) sabit ve güvenli olduğu için önbelleğe alınabilir.
    cache_ok = True  # ✅ Bu tipin önbellek anahtarı üretmesi güvenlidir.

    # 3. Yapıcı Metot (Constructor): Bu tip hangi Python sınıfını temsil edecek?
    def __init__(self, cls, *args, **kwargs):
        """
        ValueType'ı bir Python sınıfı (örneğin Money, Coordinates) ile başlatır.
        :param cls: JSON'dan geri yüklenecek Python sınıfı (örneğin Money)
        """
        super().__init__(*args, **kwargs)  # Üst sınıfın (TypeDecorator) __init__ metodunu çağır.
        self.cls = cls  # Saklanacak/geri yüklenecek sınıfı kaydet.

    # 4. Python → Veritabanı Dönüşümü: Python nesnesini veritabanına yazmadan önce hazırlar.
    def process_bind_param(self, value, dialect):
        """
        Python nesnesini → JSON string'e dönüştürür (veritabanına yazılırken).
        Örnek: Money(15000, "TRY") → '{"amount": 15000, "currency": "TRY"}'
        :param value: Python nesnesi (örneğin Money instance)
        :param dialect: Kullanılan veritabanı diyalekti (örneğin sqlite, postgresql)
        :return: JSON string veya None
        """
        if value is not None:
            # Nesnenin __dict__'ini al ve JSON string'e dönüştür.
            # __dict__: Nesnenin tüm attribute'larını içeren sözlük (örneğin {'amount': 15000, 'currency': 'TRY'})
            return json.dumps(value.__dict__)
        return None  # Eğer değer None ise, None döndür.

    # 5. Veritabanı → Python Dönüşümü: Veritabanından okunan değeri Python nesnesine çevirir.
    def process_result_value(self, value, dialect):
        """
        Veritabanından gelen JSON string'i → Python nesnesine dönüştürür (okuma sırasında).
        Örnek: '{"amount": 15000, "currency": "TRY"}' → Money(amount=15000, currency="TRY")
        :param value: Veritabanından gelen JSON string
        :param dialect: Kullanılan veritabanı diyalekti
        :return: Python nesnesi (self.cls tipinde) veya None
        """
        if value is not None:
            # JSON string'i Python sözlüğüne dönüştür.
            data = json.loads(value)
            # Sözlüğü, self.cls sınıfının yapıcısına (**kwargs olarak) vererek yeni bir nesne oluştur.
            # Örnek: Money(**{'amount': 15000, 'currency': 'TRY'}) → Money(15000, "TRY")
            return self.cls(**data)
        return None  # Eğer değer None ise, None döndür.

    # 6. SQL İfade Temsili: Bu sütun SQL ifadelerinde nasıl temsil edilmeli?
    def column_expression(self, col):
        """
        SQLAlchemy, bir sütunu SQL ifadesi içinde (WHERE, ORDER BY vs.) kullanırken
        bu metodu çağırır. Biz burada sütunu olduğu gibi bırakıyoruz — yani ham JSON string.
        Neden? Çünkü SQL seviyesinde nesneye dönüştürme YAPILMAZ — sadece Python seviyesinde yapılır.
        Filtreleme gibi işlemler için hybrid_property kullanılır (json_extract ile).
        :param col: SQLAlchemy Column nesnesi (örneğin Product.price sütunu)
        :return: Değişmeden aynı sütun nesnesi
        """
        return col  # SQL'de sütun hala TEXT (JSON string) olarak kalır.
# Value Object sınıfları
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

# Modeller
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(ValueType(Money))  # ValueType ile JSON olarak saklanan value object

    # -------------------------------------------------------------------
    # ✅ HYBRID_PROPERTY: NEDEN KULLANILIR?
    # -------------------------------------------------------------------
    # SQLAlchemy'de, bir sütunun hem Python nesnesi attribute'u gibi 
    # hem de SQL sorgusu içinde (WHERE, ORDER BY vs.) kullanılabilmesini sağlar.
    # 
    # 🎯 AMAÇ: 
    #   - Python tarafında: p.price_amount → p.price.amount gibi doğal erişim
    #   - SQL tarafında:  .filter(Product.price_amount > 10000) → 
    #                    SQL'de: json_extract(price, '$.amount') > 10000
    #
    # ❗ NEDEN GEREKLİ?
    #   ValueType sadece Python tarafında nesneye çevirir. SQL tarafında sütun hala JSON string.
    #   Dolayısıyla doğrudan "Product.price.amount" şeklinde filtreleme YAPILAMAZ.
    #   hybrid_property, bu iki dünyayı birleştirir: hem Python'da attribute gibi davranır,
    #   hem de SQL'de fonksiyon çağrısına (json_extract) dönüştürülür.
    #
    # 🔄 ValueType İLİŞKİSİ:
    #   ValueType, veriyi JSON string olarak saklar ve Python'da geri nesneye çevirir.
    #   Ama SQL filtrelemesi için bu yetmez → hybrid_property ile SQL tarafında
    #   nasıl sorgulanacağını MANUEL olarak tanımlıyoruz.
    # -------------------------------------------------------------------

    @hybrid_property
    def price_amount(self):
        """
        🐍 PYTHON TARAFINDA KULLANIM:
        Bu metod, Python nesnesi üzerinden erişildiğinde çalışır.
        Örnek: product.price_amount → product.price.amount döner.
        ValueType sayesinde 'price' zaten Money nesnesi → .amount attribute'u var.
        """
        return self.price.amount if self.price else None

    @price_amount.expression
    def price_amount(cls):
        """
        🗃️ SQL TARAFINDA KULLANIM:
        Bu metod, SQLAlchemy sorgu ifadesi içinde (örneğin .filter() içinde) 
        bu property kullanıldığında çağrılır.
        ValueType ile saklanan JSON string içinden 'amount' alanını çıkarmak için
        SQLite'ın json_extract fonksiyonunu kullanır.
        Örnek SQL: json_extract(price, '$.amount')
        """
        return func.json_extract(cls.price, '$.amount')

    # Aynı mantık currency için de uygulanabilir:
    @hybrid_property
    def price_currency(self):
        """Python tarafında erişim: product.price_currency"""
        return self.price.currency if self.price else None

    @price_currency.expression
    def price_currency(cls):
        """SQL tarafında: json_extract(price, '$.currency')"""
        return func.json_extract(cls.price, '$.currency')

class Place(Base):
    __tablename__ = 'places'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    location = Column(ValueType(Coordinates))
    owner_name = Column(ValueType(FullName))

    @hybrid_property
    def location_lat(self):
        return self.location.lat if self.location else None

    @location_lat.expression
    def location_lat(cls):
        return func.json_extract(cls.location, '$.lat')

    @hybrid_property
    def owner_first_name(self):
        return self.owner_name.first if self.owner_name else None

    @owner_first_name.expression
    def owner_first_name(cls):
        return func.json_extract(cls.owner_name, '$.first')

# DB ve session
engine = create_engine('sqlite:///multi_ValueObject.db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Test verileri
laptop = Product(name="Laptop", price=Money(15000, "TRY"))
cafe = Place(
    name="Kahve Dükkanı",
    location=Coordinates(41.0151, 28.9793),
    owner_name=FullName("Ayşe", "Yılmaz")
)

session.add_all([laptop, cafe])
session.commit()

# ✅ Python tarafında erişim
p = session.query(Product).first()
print(f"Python: {p.price_amount} {p.price_currency}")  # 15000 TRY

# ✅ SQL filtreleme
expensive = session.query(Product).filter(Product.price_amount > 10000).all()
for p in expensive:
    print(f"SQL Filter: {p.name} - {p.price_amount} {p.price_currency}")

# ✅ Owner name filter
ayse_places = session.query(Place).filter(Place.owner_first_name == 'Ayşe').all()
for pl in ayse_places:
    print(f"Ayşe'nin yeri: {pl.name}")
