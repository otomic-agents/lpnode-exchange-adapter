class Order:
    def __init__(self, order_id, product_info, amount):
        self.order_id = order_id
        self.product_info = product_info
        self.amount = amount

    def __str__(self):
        return f"Order ID: {self.order_id}, Product Info: {self.product_info}, Amount: {self.amount}"

    # 假设这里是向系统提交新订单的方法
    def create(self):
        # 实际应用中这里会包含与数据库交互或调用API来创建订单的实际逻辑
        print(f"Order created: {self.__str__()}")
