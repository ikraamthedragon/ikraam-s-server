shopping_cart = [{"name": "oranges", "price":6, "amount":2}, {"name": "apples", "price":4, "amount":3}]

def total_price(shopping_cart, tax=0):
    total = 0
    for item in shopping_cart:
        total = total + (item['price'] * item['amount'])
    total = tax + total
    return total


class ShoppingManager:
    def __init__(self, name, shopping_list, tax):
        self.name = name
        self.shopping_list = shopping_list
        self.tax = tax

        def total(self):
            total = 0
            for item in self.shopping_list:
                total += item['price'] * item['amount']
            total = self.tax + total
            return total

        def print_total_price(self):
            print("total price is: ", self.total_price())