import time
import bisect

class Order:
    def __init__(self, id, side, price, qty, type='limit'):
        self.id = id
        self.side = side.lower()
        self.price = price
        self.qty = qty
        self.type = type
        self.t = time.perf_counter_ns()

    def __str__(self):
        return str(self.side) + " " + str(self.id)

class OrderBook:
    def __init__(self):
        self.buy_list = [] 
        self.sell_list = [] 
        self.history = []

    def add_order(self, order):
        if order.qty <= 0:
            return
        
        if order.side == 'buy':
            self.match(order, self.sell_list)
        else:
            self.match(order, self.buy_list)

        if order.qty > 0:
            if order.type == 'market':
                print("Cancelled remaining market order " + str(order.id))
                return

            if order.side == 'buy':
                bisect.insort(self.buy_list, (-order.price, order.t, order))
            else:
                bisect.insort(self.sell_list, (order.price, order.t, order))

    def match(self, new_order, orders_list):
        while len(orders_list) > 0 and new_order.qty > 0:
            top_order_tuple = orders_list[0]
            existing_order = top_order_tuple[2]
            
            can_trade = False
            if new_order.type == 'market':
                can_trade = True
            elif new_order.side == 'buy' and new_order.price >= existing_order.price:
                can_trade = True
            elif new_order.side == 'sell' and new_order.price <= existing_order.price:
                can_trade = True
            
            if can_trade:
                amount = min(new_order.qty, existing_order.qty)
                price = existing_order.price
                
                self.history.append({
                    'time': time.time(),
                    'price': price,
                    'qty': amount
                })
                print(f">>> TRADE: {amount} @ {price} (Taker: {new_order.id}, Maker: {existing_order.id})")

                new_order.qty = new_order.qty - amount
                existing_order.qty = existing_order.qty - amount

                if existing_order.qty == 0:
                    orders_list.pop(0)
            else:
                break

    def print_book(self):
        print("\n" + "="*50)
        print("--- ORDER BOOK SNAPSHOT ---")
        print("BID QTY    |  BID PRC   |  ASK PRC   |   ASK QTY")
        print("-" * 50)
        
        limit = 5
        buys = self.buy_list[:limit]
        sells = self.sell_list[:limit]
        
        count = max(len(buys), len(sells))
        
        for i in range(count):
            b_q = ""
            b_p = ""
            a_p = ""
            a_q = ""

            if i < len(buys):
                b_q = str(buys[i][2].qty)
                b_p = str(buys[i][2].price)
            
            if i < len(sells):
                a_p = str(sells[i][2].price)
                a_q = str(sells[i][2].qty)
            
            print(f"{b_q:<10} | {b_p:^10} | {a_p:^10} | {a_q:>10}")
        print("="*50 + "\n")

if __name__ == "__main__":
    lob = OrderBook()
    
    print("1. Submitting 15 Passive Limit Orders...")
    for i in range(15):
        if i % 2 == 0:
            s = 'buy'
        else:
            s = 'sell'
        
        step = i // 2
        if s == 'sell':
            p = 101 + step
        else:
            p = 99 - step
            
        q = 10 + i
        
        o = Order("ORD_" + str(i), s, p, q)
        lob.add_order(o)
    
    lob.print_book()

    print("2. Submitting 10 Aggressive Market Orders...")
    for j in range(10):
        if j % 2 != 0:
            s = 'buy'
        else:
            s = 'sell'
            
        q = 5
        
        m = Order("MKT_" + str(j), s, 0, q, type='market')
        
        print(f"[Incoming {s.upper()} Market Order {j} for {q} units]")
        lob.add_order(m)
        time.sleep(0.01)

    lob.print_book()