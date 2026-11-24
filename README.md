# Autonomous WhatsApp AI Agent for E-Commerce

An AI-powered e-commerce assistant that communicates with customers through WhatsApp, understands Arabic and English, and performs real store operations using Gemini function calling and a FastAPI backend.

## 1. Project Overview

This project implements an autonomous WhatsApp shopping assistant that can:

- Display available product categories.
- Search for products and check stock availability.
- Retrieve product details.
- Manage customer shopping carts.
- Complete checkout using a shipping address.
- Track existing orders.
- Cancel orders.
- Handle multiple relevant tool calls within one customer request.
- Maintain separate conversation histories for different customers.
- Communicate in Arabic or English according to the customer's language.

All product, price, stock, and order information is retrieved from the backend to prevent fabricated store information.

## 2. Technologies Used

- Python
- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- Google Gemini API (`google-genai`)
- Neonize (WhatsApp integration)
- Requests
- Python-dotenv

**Gemini model note:** The project currently uses `gemini-3.5-flash-lite` with API version `v1beta`. Gemini 2.5 Flash was the model specified in the original project requirements, but it was unavailable to the new Google project used during development. The current model is therefore a documented replacement.

## 3. Project Structure

```text
ecommerce-whatsapp-agent/
│
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── schemas.py
│   ├── seed_data.py
│   └── ecommerce.db
│
├── tools.py
├── agent.py
├── bot.py
├── simulate_chat.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

The SQLite database and WhatsApp session files are generated locally and are excluded from Git.

## 4. Installation and Setup

### Step 1: Clone the repository

```bash
git clone  https://github.com/mohamed232002/ecommerce-whatsapp-agent.git
cd ecommerce-whatsapp-agent
```

### Step 2: Create a virtual environment

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Configure environment variables

Create a `.env` file in the project root using `.env.example` as a template.

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
BACKEND_URL=http://127.0.0.1:8000
```

## 5. Database Initialization

Initialize the local SQLite database and insert the sample store data:

```powershell
python backend\seed_data.py
```

This initializes the store data, including product categories and products.

## 6. Running the Backend

Open a terminal in the project root, activate the virtual environment, and run:

```powershell
cd backend
python -m uvicorn main:app --reload
```

The backend API will be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

Keep the backend running while using the simulator or WhatsApp bot.

## 7. Running the Terminal Chat Simulator

Open a second terminal in the project root and activate the virtual environment.

Run:

```powershell
python simulate_chat.py
```

The simulator asks for:

- Customer name
- Customer phone number

You can then interact with the AI assistant.

Available commands:

- `reset` — Reset the current customer's conversation history.
- `exit` — End the simulation.

## 8. Running the WhatsApp Bot

Open another terminal in the project root and activate the virtual environment.

Run:

```powershell
python bot.py
```

On the first connection:

1. A QR code will appear in the terminal.
2. Open WhatsApp on your phone.
3. Navigate to **Linked Devices**.
4. Select **Link a Device**.
5. Scan the QR code.

After successful pairing, the bot can receive and respond to private customer messages.

The bot ignores:
- WhatsApp Status updates.
- Group messages.
- Messages sent by the connected account itself.

The WhatsApp session is stored locally in `whatsapp_session.db`, so the device does not normally need to be paired again after every restart.

## 9. Available Backend Tools

The AI agent uses ten Python functions to interact with the backend.

| Tool | Operation |
|---|---|
| `list_categories` | Retrieve product categories |
| `search_products` | Search products by keyword, category, and stock |
| `get_product_details` | Retrieve product information |
| `get_customer_cart` | Retrieve a customer's cart |
| `add_item_to_cart` | Add a product to the cart |
| `remove_cart_item` | Remove a cart item |
| `clear_customer_cart` | Clear the customer's cart |
| `checkout_cart` | Complete checkout with a shipping address |
| `track_order` | Retrieve order details and status |
| `cancel_order` | Cancel an order |

## 10. Main API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/categories` | List categories |
| GET | `/products` | Search and list products |
| GET | `/products/{product_id}` | Get product details |
| GET | `/cart/{customer_name}` | Get customer cart |
| POST | `/cart/items` | Add item to cart |
| DELETE | `/cart/items/{item_id}` | Remove cart item |
| DELETE | `/cart/{customer_name}` | Clear customer cart |
| POST | `/orders/checkout` | Complete checkout |
| GET | `/orders/{order_id}` | Track order |
| PUT | `/orders/{order_id}/cancel` | Cancel order |

## 11. Important Project Features

### Multi-Tool Calling

The agent can execute multiple relevant backend operations during one customer turn instead of asking the customer to split a request into separate messages.

### Zero Hallucination

The agent retrieves product prices, stock availability, and order information from backend functions. It does not claim that an operation succeeded unless the backend confirms it.

### Customer Session Isolation

Conversation histories are stored separately using customer phone identifiers.

### Database Integrity

The backend manages shopping carts, orders, and product inventory through SQLite and SQLAlchemy. Checkout validates the cart and stock before completing the order.

## 12. Security and Git

The `.gitignore` file excludes sensitive and generated files, including:

- `.env`
- Virtual environments
- Python cache files
- SQLite database files
- Database backup files

Never upload API keys, WhatsApp session databases, or private credentials to GitHub.

## 13. Requirements

Install the dependencies using:

```powershell
pip install -r requirements.txt
```

The dependency list is maintained in `requirements.txt`.

## 14. Demo

The project demonstration should show:

1. Backend startup and API documentation.
2. WhatsApp QR pairing.
3. A customer sending a multi-action shopping request.
4. The AI agent calling the required backend tools.
5. The resulting cart or order information.
6. The corresponding database changes.

## Project Demo Video

Watch the project demonstration video:

[Download Project Demo Video](https://github.com/mohamed232002/ecommerce-whatsapp-agent/releases/download/v1.0.0/demo_project.mkv)
