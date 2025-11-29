# Library Desk Agent

An AI-powered library management system that uses a RAG 
(Retrieval-Augmented Generation) agent to handle book inventory, orders, 
pricing, and customer queries.

## 🏗️ Project Structure

```
library-desk-agent/
├── app/                    # Frontend (React/Next.js)
├── server/                 # Backend (Agent, Tools, REST API)
│   ├── agent.py           # Main agent logic
│   ├── db_tools.py        # Database tool functions
│   ├── api.py             # REST API endpoints (optional)
│   └── requirements.txt   # Python dependencies
├── db/                     # Database files
│   ├── schema.sql         # Database schema
│   ├── seed.sql           # Sample data
│   └── library.db         # SQLite database (generated)
├── prompts/               # System prompts
│   └── system_prompt.txt  # Agent instructions
├── .env.example           # Environment variables template
└── README.md              # This file
```

## ✨ Features

- **Book Search**: Find books by title or author
- **Order Management**: Create and track orders
- **Inventory Control**: Restock books and check inventory levels
- **Price Updates**: Update book prices dynamically
- **Order Status**: Check order details and history
- **Low Stock Alerts**: Get notified of books with low inventory

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+ (for frontend)
- Google Gemini API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd library-desk-agent
   ```

2. **Set up the database**
   ```bash
   cd db
   sqlite3 library.db < schema.sql
   sqlite3 library.db < seed.sql
   cd ..
   ```

3. **Set up the backend**
   ```bash
   cd server
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

5. **Run the agent (CLI mode)**
   ```bash
   python agent.py
   ```

6. **Set up the frontend** (optional)
   ```bash
   cd ../app
   npm install
   npm run dev
   ```

## 🔧 Configuration

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-2.0-flash-exp
```

## 📚 Database Setup

### Schema

The database includes the following tables:
- `books` - Book inventory (ISBN, title, author, price, stock)
- `customers` - Customer information
- `orders` - Order records
- `order_items` - Items in each order

### Seeding the Database

```bash
cd db
sqlite3 library.db < schema.sql
sqlite3 library.db < seed.sql
```

This will create sample books, customers, and orders for testing.

## 🤖 Using the Agent

### CLI Mode

```bash
cd server
source venv/bin/activate
python agent.py
```

Example queries:
- "What books do you have by George Orwell?"
- "Show me the current inventory summary"
- "Create an order for customer 1 with ISBN 978-0141439518, quantity 2"
- "Restock 978-0061120084 with 10 copies"
- "What's the status of order 1?"

### As a REST API

```bash
cd server
python api.py
```

Then make requests to `http://localhost:5000/api/chat`

## 🛠️ Available Tools

The agent has access to these tools:

1. **find_books_tool**: Search books by title or author
2. **create_order_tool**: Create new orders and reduce stock
3. **restock_book_tool**: Add inventory to existing books
4. **update_price_tool**: Change book prices
5. **order_status_tool**: Check order details
6. **inventory_summary_tool**: Get inventory overview and low stock alerts

## 📝 System Prompt

The agent's behavior is controlled by `prompts/system_prompt.txt`. You can 
customize how the agent responds by editing this file.

## 🔍 Troubleshooting

### Import Errors
Make sure you're using Python 3.12+ and have activated your virtual 
environment:
```bash
python --version
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Database Errors
Ensure the database exists and is properly seeded:
```bash
cd db
rm library.db  # Remove old database
sqlite3 library.db < schema.sql
sqlite3 library.db < seed.sql
```

### API Key Issues
Make sure your `.env` file is in the root directory and contains:
```env
GOOGLE_API_KEY=your_actual_key_here
```

## 📦 Dependencies

### Backend
- `langchain-core` - LangChain framework
- `langchain-google-genai` - Google Gemini integration
- `python-dotenv` - Environment variable management
- `sqlite3` - Database (included in Python)

### Frontend (optional)
- React/Next.js
- Tailwind CSS
- Axios for API calls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License - feel free to use this project for learning and development.

## 🙋 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Open an issue on GitHub

---

Built with ❤️ using LangChain and Google Gemini
