from dataclasses import dataclass

@dataclass(frozen=True)
class ValueObject:
    value: object

    def __str__(self):
        return str(self.value)

# Kullanım örnekleri:
date = ValueObject("15/06/2024")
file_path = ValueObject("/home/user/file.txt")
email_address = ValueObject("user@example.com")
measurement_unit = ValueObject("10 m")
color = ValueObject("(255, 0, 0)")
file_size = ValueObject("1024 KB")
currency_converter = ValueObject("100 USD = 110.0 EUR")
conference_room = ValueObject("Meeting Room A (Capacity: 20)")

print(date)
print(file_path)
print(email_address)
print(measurement_unit)
print(color)
print(file_size)
print(currency_converter)
print(conference_room)
#measurement_unit.value="ayhamn" #hata verir

@dataclass(frozen=True)
class ValueObject2:
    value: object

    def __str__(self):
        return str(self.value)

# Kullanım örneği:
vo = ValueObject2("değişmez")
print(vo)  # Output: değişmez

# Değişmezlik kontrolü
# Aşağıdaki satır hata verir, çünkü değişmez bir nesne üzerinde değişiklik yapılmaya çalışılıyor.
vo.value = "yenideğişmez"
