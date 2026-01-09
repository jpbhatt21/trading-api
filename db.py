instruments = {
  "RELIANCE": {
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "instrumentType": "Equity",
    "lastTradedPrice": 1507.60
  },
  "TCS": {
    "symbol": "TCS",
    "exchange": "NSE",
    "instrumentType": "Equity",
    "lastTradedPrice": 3204.00
  },
  "HDFCBANK": {
    "symbol": "HDFCBANK",
    "exchange": "NSE",
    "instrumentType": "Equity",
    "lastTradedPrice": 947.00
  },
  "INFY": {
    "symbol": "INFY",
    "exchange": "NSE",
    "instrumentType": "Equity",
    "lastTradedPrice": 1613.00
  },
  "ICICIBANK": {
    "symbol": "ICICIBANK",
    "exchange": "NSE",
    "instrumentType": "Equity",
    "lastTradedPrice": 1435.00
  }
}

def get_all_instruments():
    return instruments.values()

def get_instrument_by_symbol(symbol):
    return instruments.get(symbol, None)

orders = {}

def get_order_by_id(order_id):
    return orders.get(order_id, None)

def get_orders_by_user(user_id):
    return [order for order in orders.values() if order['userId'] == user_id]

def save_order(order):
    orders[order['orderId']] = order

def get_portfolio_by_user(user_id):
    user_orders = get_orders_by_user(user_id)
    portfolio = {}
    for order in user_orders:
        symbol = order['symbol']
        if symbol not in portfolio:
            portfolio[symbol] = {
                "symbol": symbol,
                "quantity": 0,
                "averagePrice": 0.0
            }
        if order['type'] == 'BUY':
            total_cost = portfolio[symbol]['averagePrice'] * portfolio[symbol]['quantity']
            total_cost += order['price'] * order['quantity']
            portfolio[symbol]['quantity'] += order['quantity']
            portfolio[symbol]['averagePrice'] = total_cost / portfolio[symbol]['quantity']
        elif order['type'] == 'SELL':
            portfolio[symbol]['quantity'] -= order['quantity']
            if portfolio[symbol]['quantity'] < 0:
                portfolio[symbol]['quantity'] = 0
    for symbol in list(portfolio.keys()):
        if portfolio[symbol]['quantity'] == 0:
            del portfolio[symbol]
            continue
        portfolio[symbol]['averagePrice'] = round(portfolio[symbol]['averagePrice'], 2)
        portfolio[symbol]["currentValue"] = round(portfolio[symbol]['quantity'] * instruments[symbol]['lastTradedPrice'], 2)
    return portfolio