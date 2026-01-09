import requests
import sys
import os
def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


BASE_URL = "http://localhost:5000"

def print_header(text):
    print("\n" + "=" * 50)
    print(text.center(50))
    print("=" * 50)

def print_error(text):
    print(f"\nERROR: {text}")

def fetch_instruments():
    try:
        response = requests.get(f"{BASE_URL}/api/v1/instruments")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to fetch instruments: {e}")
        return None

def fetch_portfolio():
    try:
        response = requests.get(f"{BASE_URL}/api/v1/portfolio")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to fetch portfolio: {e}")
        return None

def fetch_trades():
    try:
        response = requests.get(f"{BASE_URL}/api/v1/trades")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to fetch trades: {e}")
        return None

def fetch_order(order_id: str):
    try:
        response = requests.get(f"{BASE_URL}/api/v1/orders/{order_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to fetch order: {e}")
        return None

def display_instruments(instruments):
    print_header("AVAILABLE INSTRUMENTS")
    print(f"\n{'No.':<5} {'Symbol':<15} {'Exchange':<10} {'Type':<12} {'LTP':>12}")
    print("-" * 60)
    for idx, instrument in enumerate(instruments, 1):
        print(f"{idx:<5} {instrument['symbol']:<15} {instrument['exchange']:<10} "
              f"{instrument['instrumentType']:<12} {"₹"+f'{instrument['lastTradedPrice']:.2f}':>12}")

def display_portfolio(portfolio):
    print_header("YOUR PORTFOLIO")
    if not portfolio:
        print("\nYour portfolio is empty.")
        return
    
    print(f"\n{'Symbol':<15} {'Quantity':<12} {'Avg Price':>12} {'Current Value':>15}")
    print("-" * 70)
    total_value = 0
    for holding in portfolio:
        total_value += holding['currentValue']
        print(f"{holding['symbol']:<15} {holding['quantity']:<12.2f} "
              f"{"₹"+f'{holding['averagePrice']:.2f}' :>12} {"₹"+f'{holding['currentValue']:.2f}':>15}")
    print("-" * 70)
    print(f"{'Total Portfolio Value:':<42} {"₹"+f'{total_value:.2f}':>14}")

def display_trades(trades):
    print_header("YOUR TRADES")
    if not trades:
        print("\nNo trades found.")
        return
    
    print(f"\n{'Order ID':<38} {'Symbol':<12} {'Type':<6} {'Style':<8} {'Qty':<8} {'Price':>10} {'Status':<10}")
    print("-" * 100)
    for trade in trades:
        print(f"{trade['orderId']:<38} {trade['symbol']:<12} {trade['type']:<6} "
              f"{trade['style']:<8} {trade['quantity']:<8.2f} {"₹"+f'{trade['price']:.2f}':>12} {trade['status']:<10}")

def place_order():
    print_header("PLACE ORDER")

    instruments = fetch_instruments()
    if not instruments:
        return

    display_instruments(instruments)
    
    while True:
        try:
            choice = input("\nEnter instrument number (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                return
            
            choice = int(choice)
            if 1 <= choice <= len(instruments):
                selected_instrument = instruments[choice - 1]
                break
            else:
                print_error(f"Please enter a number between 1 and {len(instruments)}")
        except ValueError:
            print_error("Invalid input. Please enter a number.")
    
    print(f"\n-> Selected: {selected_instrument['symbol']} (LTP: ₹{selected_instrument['lastTradedPrice']})")
    
    while True:
        order_type = input("\nOrder Type - [B]uy or [S]ell: ").strip().upper()
        if order_type in ['B', 'S']:
            order_type = 'BUY' if order_type == 'B' else 'SELL'
            break
        print_error("Invalid input. Enter 'B' for Buy or 'S' for Sell.")

    while True:
        order_style = input("\nOrder Style - [M]arket or [L]imit: ").strip().upper()
        if order_style in ['M', 'L']:
            order_style = 'MARKET' if order_style == 'M' else 'LIMIT'
            break
        print_error("Invalid input. Enter 'M' for Market or 'L' for Limit.")

    while True:
        try:
            quantity = float(input("\nEnter quantity: ").strip())
            if quantity > 0:
                break
            print_error("Quantity must be greater than 0.")
        except ValueError:
            print_error("Invalid input. Please enter a valid number.")
    
    price = None
    if order_style == 'LIMIT':
        while True:
            try:
                price = float(input("\nEnter limit price: ").strip())
                if price > 0:
                    break
                print_error("Price must be greater than 0.")
            except ValueError:
                print_error("Invalid input. Please enter a valid number.")
    
    print("\n" + "-" * 50)
    print("ORDER SUMMARY")
    print("-" * 50)
    print(f"Symbol:       {selected_instrument['symbol']}")
    print(f"Type:         {order_type}")
    print(f"Style:        {order_style}")
    print(f"Quantity:     {quantity}")
    if price:
        print(f"Price:        ₹{price:.2f}")
    else:
        print(f"Price:        Market Price (₹{selected_instrument['lastTradedPrice']:.2f})")
    print("-" * 50)
    
    confirm = input("\nConfirm order? [Y/n]: ").strip().upper()
    if confirm and confirm != 'Y':
        print("\n--Order cancelled.--")
        return

    order_data = {
        "symbol": selected_instrument['symbol'],
        "orderType": order_type,
        "orderStyle": order_style,
        "quantity": quantity,
        "price": price
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/orders/", json=order_data)
        response.raise_for_status()
        order_response = response.json()
        print("-> Order placed successfully! <-")
        print(f"\nOrder ID: {order_response['orderId']}")
        print(f"Status: {order_response['status']}")
    except requests.exceptions.RequestException as e:
        if hasattr(e.response, 'json'):
            error_msg = e.response.json().get('error', str(e))
            print_error(f"Failed to place order: {error_msg}")
        else:
            print_error(f"Failed to place order: {e}")

def view_order():
    print_header("VIEW ORDER")
    order_id = input("\nEnter Order ID: ").strip()
    
    if not order_id:
        print_error("Order ID cannot be empty.")
        return
    
    order = fetch_order(order_id)
    if order:
        print("\n" + "-" * 50)
        print("ORDER DETAILS")
        print("-" * 50)
        print(f"Order ID:     {order['orderId']}")
        print(f"User ID:      {order['userId']}")
        print(f"Symbol:       {order['symbol']}")
        print(f"Type:         {order['type']}")
        print(f"Style:        {order['style']}")
        print(f"Quantity:     {order['quantity']}")
        print(f"Price:        ₹{order['price']:.2f}")
        print(f"Status:       {order['status']}")
        print("-" * 50)

def main_menu():
    while True:
        cls()
        print_header("TRADING CLI")
        print("\nWhat would you like to do?")
        print("\n1. [PO] Place Order")
        print("2. [VI] View Instruments")
        print("3. [VP] View Portfolio")
        print("4. [VT] View Trades")
        print("5. [VO] View Order (by ID)")
        print("6. [Q]  Quit")
        
        choice = input("\nEnter your choice: ").strip().upper()
        cls()
        print("Fetching data, please wait...\n")
        if choice in ['1', 'PO']:
            place_order()
        elif choice in ['2', 'VI']:
            instruments = fetch_instruments()
            if instruments:
                display_instruments(instruments)
        elif choice in ['3', 'VP']:
            portfolio = fetch_portfolio()
            if portfolio is not None:
                display_portfolio(portfolio)
        elif choice in ['4', 'VT']:
            trades = fetch_trades()
            if trades is not None:
                display_trades(trades)
        elif choice in ['5', 'VO']:
            view_order()
        elif choice in ['6', 'Q']:
            print("\nGoodbye!")
            sys.exit(0)
        else:
            print_error("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        response.raise_for_status()
        main_menu()
    except requests.exceptions.RequestException:
        print_error(f"Cannot connect to API at {BASE_URL}")
        print("Please make sure the Flask server is running.")
        sys.exit(1)
