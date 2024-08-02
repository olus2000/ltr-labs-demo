from dataclasses import dataclass
from typing import Optional
from fractions import Fraction
import pytest

'''
Mamy dane dwie encje: Order i OrderItem.
+-------------+               +--------------+
|    ORDER    |               |  ORDER ITEM  |
+-------------+ 1           * +--------------+
|  net_total  +---------------+  net_price   |
|  tax        |               |  quantity    |
|  total      |               |  net_total   |
|             |               |  total       |
+-------------+               |              |
                              +--------------+

gdzie:

  Order
  -----
  net_total - wartość netto zamówienia
  tax - całkowita kwota podatku
  total - wartość brutto zamówienia

  Order Item
  ----------
  net_price - cena netto 1 sztuki towaru (podane)
  quantity - ilość sztuk (podane)
  net_total - wartość netto pozycji
  total - wartość brutto pozycji

1. Jakiego typu danych użyjesz do przechowywania poszczególnych wartości
   w bazie danych?
2. Napisz kod(+testy), który wypełni brakujące wartości dla obu encji mając
   dany Order z OrderItemami (podane net_price i quantity) oraz wysokość
   podatku w %.
   Podatek dla pojedynczego OrderItema powinien być liczony od wartości
   net_total.
'''


'''
Do większości wartości użyję typu wymiernego Fraction żeby nie stracić precyzji
w obliczeniach. Mianownik nie będzie rósł za wysoko, do 10000 przy obliczaniu
podatków. Zakładam że podatek jest zaokrąglany do 1, 100 dla każdego OrderItema,
a wartość brutto Orderu to suma wartości brutto jego Itemów.

Do ilości sztuk użyję typu całkowitego int, zakładając że towary którymy
handlujemy są niepodzielne. W przeciwnym wypadku należałoby rozważyć typ
Fraction. Do wysokości podatku użyję typu całkowitego int, zakładając że
wszystkie możliwe wartości podatku są wielokrotnością 1%, a zadanie wymaga
podawania tych wartości w %.
'''


# Rozwiązanie

@dataclass
class OrderItem:
    net_price : Fraction
    quantity : int
    net_total : Optional[Fraction] = None
    total : Optional[Fraction] = None

    def fill_tax_fields(self, tax_rate: int) -> 'OrderItem':
        '''
        tax_rate : int
            Wysokość podatku wyrażona w procentach
        '''

        self.net_total = self.net_price * self.quantity
        self.total = round(self.net_total * (Fraction(tax_rate, 100) + 1), 2)

        return self


@dataclass
class Order:
    items : list[OrderItem]
    net_total : Optional[Fraction] = None
    tax : Optional[Fraction] = None
    total : Optional[Fraction] = None

    def fill_tax_fields(self, tax_rate: int) -> 'Order':
        '''
        tax_rate : int
            Wysokość podatku wyrażona w procentach
        '''

        for i in self.items:
            i.fill_tax_fields(tax_rate)

        self.net_total = sum(i.net_total for i in self.items)
        self.total = sum(i.total for i in self.items)
        self.tax = self.total - self.net_total

        return self


# Testy

'''
pytest tax_calculator.py
'''


@pytest.mark.parametrize("item,tax_rate,target", [
    (
        OrderItem(Fraction(), 0),
        0,
        OrderItem(Fraction(), 0, Fraction(), Fraction()),
    ),
    (
        OrderItem(Fraction(), 0),
        100,
        OrderItem(Fraction(), 0, Fraction(), Fraction()),
    ),
    (
        OrderItem(Fraction(2137, 100), 0),
        0,
        OrderItem(Fraction(2137, 100), 0, Fraction(), Fraction()),
    ),
    (
        OrderItem(Fraction(2137, 100), 1),
        0,
        OrderItem(Fraction(2137, 100), 1, Fraction(2137, 100), Fraction(2137, 100)),
    ),
    (
        OrderItem(Fraction(2137, 100), 5),
        0,
        OrderItem(Fraction(2137, 100), 5, Fraction(2137, 20), Fraction(2137, 20)),
    ),
    (
        OrderItem(Fraction(2137, 100), 5),
        10,
        OrderItem(Fraction(2137, 100), 5, Fraction(2137, 20), Fraction(23508, 200)),
    ),
])
def test_tax_filling_of_order_items(item, tax_rate, target):
    processed = item.fill_tax_fields(tax_rate)
    assert processed is item
    assert processed == target


@pytest.mark.parametrize("order,tax_rate,target", [
    (
        Order([]),
        0,
        Order([], Fraction(), Fraction(), Fraction()),
    ),
    (
        Order([]),
        100,
        Order([], Fraction(), Fraction(), Fraction()),
    ),
    (
        Order([
            OrderItem(Fraction(2137, 100), 0),
        ]),
        0,
        Order(
            [
                OrderItem(Fraction(2137, 100), 0, Fraction(), Fraction())
            ],
            Fraction(),
            Fraction(),
            Fraction(),
        ),
    ),
    (
        Order([
            OrderItem(Fraction(2137, 100), 5),
        ]),
        0,
        Order(
            [
                OrderItem(
                    Fraction(2137, 100),
                    5,
                    Fraction(2137, 20),
                    Fraction(2137, 20),
                )
            ],
            Fraction(2137, 20),
            Fraction(),
            Fraction(2137, 20),
        ),
    ),
    (
        Order([
            OrderItem(Fraction(2137, 100), 5),
        ]),
        10,
        Order(
            [
                OrderItem(
                    Fraction(2137, 100),
                    5,
                    Fraction(2137, 20),
                    Fraction(23508, 200),
                )
            ],
            Fraction(2137, 20),
            Fraction(2138, 200),
            Fraction(23508, 200),
        ),
    ),
    (
        Order([
            OrderItem(Fraction(2137, 100), 5),
            OrderItem(Fraction(131, 100), 3),
        ]),
        10,
        Order(
            [
                OrderItem(
                    Fraction(2137, 100),
                    5,
                    Fraction(2137, 20),
                    Fraction(23508, 200),
                ),
                OrderItem(
                    Fraction(131, 100),
                    3,
                    Fraction(393, 100),
                    Fraction(432, 100),
                ),
            ],
            Fraction(11078, 100),
            Fraction(2216, 200),
            Fraction(24372, 200),
        ),
    ),
])
def test_tax_filling_of_orders(order, tax_rate, target):
    processed = order.fill_tax_fields(tax_rate)
    assert processed is order
    assert processed == target
