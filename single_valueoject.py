from sqlalchemy import create_engine, Column, Integer, String, TypeDecorator
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import json

# --- Temel ORM kurulumu ---
Base = declarative_base()
"""
✅ Hedef:
User sınıfı olsun.
profile sütunu, bir JSON içinde age ve country tutacak.
profile bir value object gibi davranacak.
age > 18 olan kullanıcıları sorgula"""
# --- Value Object: Profile (sadece veri taşıyor) ---
class Profile:
    def __init__(self, age, country):
        self.age = age
        self.country = country
"""🧠 Sonuç
❌ SQLite’da gerçek composite yok.
✅ Ama TypeDecorator ile aynı amacı (value object saklamak) çok basit şekilde
sağlayabilirsin.
Bu yapı, DDD’deki value object kavramına tam uyar"""
#------------------------------------------------------------------ 
# --- JSON tipi için özel sütun ---
#ProfileType → Profile nesnesini JSON’a çevirir.
class ProfileType(TypeDecorator):
    impl = String  # SQLite TEXT sütunu

    def process_bind_param(self, value, dialect):
        # Python nesnesini JSON string'e çevir
        if value is not None:
            return json.dumps({'age': value.age, 'country': value.country})
        return None
        #------------------------------------------------------------------    
          #🔄 Örnek Akış:       
            #user = User(profile=Profile(age=25, country="TR"))
            #session.add(user)  # 1. Kaydetme
           """
            SQLAlchemy user.profile'i görür.
            profile sütunu ProfileType tipinde → process_bind_param çağrılır.
            Profile(25, "TR") → '{"age": 25, "country": "TR"}' (string)
            Bu string, SQLite’ın TEXT sütununa yazılır"""
             #------------------------------------------------------------------
    def process_result_value(self, value, dialect):
        # JSON string'den Python nesnesine çevir
        if value is not None:
            data = json.loads(value)
            return Profile(data['age'], data['country'])
        return None
        #------------------------------------------------------------------    
            #user = session.query(User).first()  # 2. Okuma
            """
                ***1-SQLite’dan '{"age": 25, "country": "TR"}' gelir.
                ***2-ProfileType.process_result_value çağrılır.
                ***3-JSON string → Profile(age=25, country="TR")
                ***4-Sen user.profile.age yazdığında, doğal erişim olur"""   

# --- Sade User tablosu ---
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    profile = Column(ProfileType)  # JSON olarak saklanır

# --- Veritabanı bağlantısı ---
engine = create_engine('sqlite:///example.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

session.add(User(name="Ali", profile=Profile(age=25, country="TR")))
session.add(User(name="Zeynep", profile=Profile(age=17, country="TR")))
session.add(User(name="Mehmet", profile=Profile(age=30, country="DE")))
session.add(User(name="Veli", profile=Profile(age=24, country="TR")))
session.add(User(name="Züleyha", profile=Profile(age=18, country="TR")))
session.add(User(name="Muhittin", profile=Profile(age=20, country="DE")))
session.add(User(name="Şükrü", profile=Profile(age=23, country="TR")))
session.add(User(name="leyla", profile=Profile(age=16, country="TR")))
session.add(User(name="Kemal", profile=Profile(age=32, country="DE")))
session.commit()

from sqlalchemy import text
#------------------------------------------------------------------
"""
Ama dikkat:
"SQLAlchemy profile.age" gibi doğrudan sorgulamayı otomatik desteklemez,
çünkü profile bir TEXT sütunu içinde JSON olarak saklanıyor.

Ancak SQLite, json_extract fonksiyonunu destekler. Bunu kullanarak sorgu
yapabiliriz."""
#------------------------------------------------------------------
# JSON içinden age'ye göre sorgu
results = session.query(User).filter(
    text("json_extract(profile, '$.age') > 18")
).all()
for user in results:
    print(f"{user.name} - {user.profile.age} yaşında")

#------------------------------------------------------------------   
turks = session.query(User).filter(
    text("json_extract(profile, '$.country') = 'DE'")
).all()
for user in turks:
    print(user.name)
#------------------------------------------------------------------    
"""✅ Özet
ProfileType → Profile nesnesini JSON’a çevirir.
json_extract → SQLite’ın JSON sorgulama fonksiyonu.
text() → SQLAlchemy’de ham SQL fonksiyonlarını kullanmamızı sağlar."""
