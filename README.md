# Trading API

A Flask-based REST API Trading – Bajaj Broking

## Setup and Run Instructions

### Prerequisites
- Python 
- pip 

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd trading-api
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

Start the Flask server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

To verify the server is running:
```bash
curl http://localhost:5000/health
```

### Optional: Using the CLI Tool

A command-line interface is provided for interactive trading:
```bash
python cli.py
```

The CLI provides options to:
- Place orders interactively
- View available instruments
- View portfolio and P&L
- View trades history
- Look up specific orders

## API Details

### Base URL
```
http://localhost:5000
```

### Endpoints

#### 1. Health Check
**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

---

#### 2. Get Instruments
**GET** `/api/v1/instruments`

Retrieve list of all available trading instruments.

**Response:**
```json
[
  {
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "instrumentType": "Equity",
    "lastTradedPrice": 1507.60
  },
  {
    "symbol": "TCS",
    "exchange": "NSE",
    "instrumentType": "Equity",
    "lastTradedPrice": 3204.00
  }
]
```

---

#### 3. Place Order
**POST** `/api/v1/orders/`

Place a BUY or SELL order for a specific instrument.

**Request Body:**
```json
{
  "symbol": "RELIANCE",
  "orderType": "BUY",
  "orderStyle": "MARKET",
  "quantity": 10,
  "price": 1510.00
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading symbol (e.g., "RELIANCE", "TCS") |
| orderType | string | Yes | Order type: "BUY" or "SELL" |
| orderStyle | string | Yes | Order style: "MARKET" or "LIMIT" |
| quantity | number | Yes | Number of shares (must be > 0) |
| price | number | Conditional | Required for LIMIT orders, ignored for MARKET orders |

**Response (Success - 201):**
```json
{
  "orderId": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
  "userId": 123,
  "symbol": "RELIANCE",
  "type": "BUY",
  "style": "MARKET",
  "quantity": 10,
  "price": 1507.60,
  "status": "placed"
}
```

**Error Responses:**
- `400 Bad Request`: Missing required fields, invalid parameters, or insufficient holdings
- `404 Not Found`: Invalid instrument symbol

**Validations:**
- Symbol must exist in the instruments list
- Order type must be "BUY" or "SELL"
- Order style must be "MARKET" or "LIMIT"
- Quantity must be a positive number
- For LIMIT orders, price is mandatory and must be > 0
- For SELL orders, user must have sufficient holdings in portfolio

---

#### 4. Get Order by ID
**GET** `/api/v1/orders/<orderId>`

Retrieve details of a specific order.

**Path Parameters:**
- `orderId`: UUID of the order

**Response (Success - 200):**
```json
{
  "orderId": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
  "userId": 123,
  "symbol": "RELIANCE",
  "type": "BUY",
  "style": "MARKET",
  "quantity": 10,
  "price": 1507.60,
  "status": "placed"
}
```

**Error Response:**
- `404 Not Found`: Order does not exist

---

#### 5. Get Trades
**GET** `/api/v1/trades`

Retrieve all orders/trades for the current user.

**Response:**
```json
[
  {
    "orderId": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
    "userId": 123,
    "symbol": "RELIANCE",
    "type": "BUY",
    "style": "MARKET",
    "quantity": 10,
    "price": 1507.60,
    "status": "placed"
  },
  {
    "orderId": "b2c3d4e5-f6g7-8h9i-0j1k-l2m3n4o5p6q7",
    "userId": 123,
    "symbol": "TCS",
    "type": "BUY",
    "style": "LIMIT",
    "quantity": 5,
    "price": 3200.00,
    "status": "placed"
  }
]
```

---

#### 6. Get Portfolio
**GET** `/api/v1/portfolio`

Retrieve the user's current portfolio with holdings.

**Response:**
```json
[
  {
    "symbol": "RELIANCE",
    "quantity": 10,
    "averagePrice": 1507.60,
    "currentValue": 15076.00
  },
  {
    "symbol": "TCS",
    "quantity": 5,
    "averagePrice": 3200.00,
    "currentValue": 16020.00
  }
]
```

**Portfolio Calculation Logic:**
- BUY orders increase quantity and update average price
- SELL orders decrease quantity
- Positions with zero quantity are removed from portfolio
- Current value is calculated using live instrument prices

---

## Assumptions Made During Implementation

### 1. User Management
- **Single User System**: The application uses a hardcoded user ID (`USER = 123`) for all operations
- **No Authentication**: No login/logout or authentication mechanism is implemented
- **No User Registration**: Users are not created or managed

### 2. Order Management
- **Order Status**: All placed orders have a status of "placed" - no order execution, filling, or rejection logic
- **Instant Execution**: Orders are considered placed immediately.
- **UUID Generation**: Order IDs are generated using UUID4, with collision detection
- **No Order Cancellation**: Once placed, orders cannot be cancelled or modified

### 3. Portfolio Management
- **Calculated Portfolio**: Portfolio is computed from order history, not stored separately
- **Average Price Calculation**: Uses weighted average for BUY orders
- **Current Value**: Portfolio value uses the latest traded price from instruments
- **No Negative Positions**: System prevents selling more than what's held
- **No Short Selling**: SELL orders require existing holdings

### 4. Data Persistence
- **In-Memory Storage**: All data (instruments, orders, portfolio) is stored in memory
- **No Database**: Data is lost when the application restarts

### 5. Instruments
- **Static Instrument List**: Five hardcoded NSE equity instruments (RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK)
- **Fixed Prices**: Last traded prices are static and don't update

### 6. Validation and Error Handling
- **Basic Validation**: Input validation for required fields and data types
- **Insufficient Holdings Check**: SELL orders validate against portfolio holdings
- **Price Validation**: LIMIT orders require valid price input
- **Quantity Validation**: Ensures quantity is a positive number

### 7. API Design
- **RESTful Conventions**: Follows REST principles with appropriate HTTP methods
- **JSON Only**: All requests and responses use JSON format
- **CORS Enabled**: Cross-Origin Resource Sharing is enabled for all origins
- **No Pagination**: All list endpoints return complete results without pagination

---