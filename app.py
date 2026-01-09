from flask import Flask, jsonify,request
from flask_cors import CORS
import uuid
import db
app = Flask(__name__)
CORS(app)
USER = 123
@app.route('/health', methods=['GET'])
def health():
    return jsonify(status='healthy')

@app.route('/api/v1/instruments', methods=['GET'])
def get_instruments():
    return jsonify(list(db.get_all_instruments()))

@app.route('/api/v1/orders/',methods=['POST'])
def place_order():
    data = request.get_json()
    
    symbol = data.get('symbol')
    order_type = data.get('orderType') 
    order_style = data.get('orderStyle')
    quantity = data.get('quantity')
    price = data.get('price')

    if not symbol or not order_type or not order_style:
        return jsonify({"error": f"Missing required fields: {"symbol" if not symbol else ""} {"orderType" if not order_type else ""} {"orderStyle" if not order_style else ""}"}), 400
    cur = db.get_instrument_by_symbol(symbol)
    if not cur:
        return jsonify({"error": "Invalid instrument symbol"}), 400
    
    if order_type not in ['BUY', 'SELL']:
        return jsonify({"error": "Invalid orderType. Must be BUY or SELL"}), 400

    if order_style not in ['MARKET', 'LIMIT']:
        return jsonify({"error": "Invalid orderStyle. Must be MARKET or LIMIT"}), 400

    try:
        quantity = float(quantity)
        if quantity <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "Quantity must be a number greater than 0"}), 400

    if order_type == 'SELL':
        portfolio = db.get_portfolio_by_user(USER)
        holding = portfolio.get(symbol)
        if not holding or holding['quantity'] < quantity:
            return jsonify({"error": "Insufficient holdings to place SELL order"}), 400

    if order_style == 'LIMIT':
        try:
            if price is None or float(price) <= 0:
                return jsonify({"error": "Price is mandatory and must be > 0 for LIMIT orders"}), 400
        except (TypeError, ValueError):
             return jsonify({"error": "Invalid price format"}), 400

    order_response = {
            "orderId": str(uuid.uuid4()),
            "userId": USER,
            "symbol": symbol,
            "type": order_type,
            "style": order_style,
            "quantity": quantity,
            "price": price if order_style == 'LIMIT' else cur['lastTradedPrice'],
            "status": "placed"
    }
    while db.get_order_by_id(order_response['orderId']):
        order_response['orderId'] = str(uuid.uuid4())
    db.save_order(order_response)
    return jsonify(order_response), 201

@app.route('/api/v1/orders/<orderId>',methods=['GET'])
def get_order(orderId):
    order = db.get_order_by_id(orderId)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order)

@app.route('/api/v1/trades',methods=['GET'])
def get_trades():
    return jsonify(db.get_orders_by_user(USER))

@app.route('/api/v1/portfolio',methods=['GET'])
def get_portfolio():
    portfolio = db.get_portfolio_by_user(USER)
    return jsonify(list(portfolio.values()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)