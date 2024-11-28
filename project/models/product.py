class Product:
    def __init__(self, name: str, category: str, price: float):
        self.name: str = name
        self.category: str = category
        self.price: float = price
        self.sale: float = 0

    def edit_category(self, new_category: str):
        self.category = new_category

    def edit_price(self, new_price: float):
        self.price = new_price

    def set_sale(self, sale: float):
        self.sale = sale

    def cancel_sale(self):
        self.sale = 0

    def get_price(self) -> float:
        return self.price * (1 - self.sale / 100)

    def __repr__(self) -> str:
        return f"<Product {self.name}>"
