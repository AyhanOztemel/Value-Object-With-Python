from dataclasses import dataclass

@dataclass(frozen=True)
class Time:
    hours: int
    minutes: int
    seconds: int

    def __str__(self):
        return f"{self.hours:02}:{self.minutes:02}:{self.seconds:02}"

# Kullanım örneği:
start_time = Time(hours=9, minutes=30, seconds=0)
end_time = Time(hours=17, minutes=45, seconds=0)

print(start_time)  # Output: 09:30:00
print(end_time)    # Output: 17:45:00

#*********************************************************************
@dataclass(frozen=True)
class Location:
    latitude: float
    longitude: float

    def __str__(self):
        return f"({self.latitude}, {self.longitude})"

# Kullanım örneği:
home_location = Location(latitude=40.7128, longitude=-74.0060)
print(home_location)  # Output: (40.7128, -74.0060)

#*********************************************************************
@dataclass(frozen=True)
class Quantity:
    amount: int
    unit: str

    def __str__(self):
        return f"{self.amount} {self.unit}"

# Kullanım örneği:
product_quantity = Quantity(amount=100, unit="pieces")
print(product_quantity)  # Output: 100 pieces

#*********************************************************************
@dataclass(frozen=True)
class Money:
    amount: float
    currency: str

    def __str__(self):
        return f"{self.amount} {self.currency}"

# Kullanım örneği:
salary = Money(amount=5000.0, currency="USD")
print(salary)  # Output: 5000.0 USD

#*********************************************************************
@dataclass(frozen=True)
class Date:
    day: int
    month: int
    year: int

    def __str__(self):
        return f"{self.day:02}/{self.month:02}/{self.year}"

# Kullanım örneği:
meeting_date = Date(day=15, month=6, year=2024)
print(meeting_date)  # Output: 15/06/2024

#*********************************************************************
@dataclass(frozen=True)
class FilePath:
    path: str

    def __str__(self):
        return self.path

# Kullanım örneği:
file_path = FilePath(path="/home/user/file.txt")
print(file_path)  # Output: /home/user/file.txt

#*********************************************************************
@dataclass(frozen=True)
class EmailAddress:
    address: str

    def __str__(self):
        return self.address

# Kullanım örneği:
email = EmailAddress(address="user@example.com")
print(email)  # Output: user@example.com

#*********************************************************************
@dataclass(frozen=True)
class MeasurementUnit:
    value: float
    unit: str

    def __str__(self):
        return f"{self.value} {self.unit}"

# Kullanım örneği:
length = MeasurementUnit(value=10, unit="m")
print(length)  # Output: 10 m

#*********************************************************************
@dataclass(frozen=True)
class Color:
    red: int
    green: int
    blue: int

    def __str__(self):
        return f"({self.red}, {self.green}, {self.blue})"

# Kullanım örneği:
color = Color(red=255, green=0, blue=0)
print(color)  # Output: (255, 0, 0)

#*********************************************************************
@dataclass(frozen=True)
class FileSize:
    size: int
    unit: str

    def __str__(self):
        return f"{self.size} {self.unit}"

# Kullanım örneği:
file_size = FileSize(size=1024, unit="KB")
print(file_size)  # Output: 1024 KB

#*********************************************************************
@dataclass(frozen=True)
class CurrencyConverter:
    from_currency: str
    to_currency: str

    def convert(self, amount):
        # Burada gerçek bir dönüşüm yapılabilir, ancak örnek olarak basit bir çarpma işlemi yapalım
        return f"{amount} {self.from_currency} = {amount * 1.1} {self.to_currency}"

# Kullanım örneği:
converter = CurrencyConverter(from_currency="USD", to_currency="EUR")
print(converter.convert(100))  # Örnek çıktı: 100 USD = 110.0 EUR

#*********************************************************************
@dataclass(frozen=True)
class ConferenceRoom:
    name: str
    capacity: int

    def __str__(self):
        return f"{self.name} (Capacity: {self.capacity})"

# Kullanım örneği:
room = ConferenceRoom(name="Meeting Room A", capacity=20)
print(room)  # Output: Meeting Room A (Capacity: 20)








































































