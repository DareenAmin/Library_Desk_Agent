# /server/db_tools.py

import sqlite3
import json
from typing import List, Dict, Union

# '../db/library_desk.db' should correctly point up one directory and into 'db'.
DB_PATH = '../db/library_desk.db'

def connect_db():
    """Returns a connection object to the database."""
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

# --- TOOL IMPLEMENTATIONS ---

def find_books(q: str, by: str = "title") -> Dict:
    """
    Finds books by title or author based on the search query.

    :param q: The search query (title or author keywords).
    :param by: The field to search by ('title' or 'author').
    :return: Dictionary containing status and a list of matching books.
    """
    conn = connect_db()
    cursor = conn.cursor()
    
    # Input validation and sanitation for the column name
    column = "title" if by.lower() == "title" else "author"
    
    try:
        query = f"SELECT isbn, title, author, stock, price FROM books WHERE {column} LIKE ?"
        results = cursor.execute(query, (f'%{q}%',)).fetchall()
        
        # Convert list of Row objects to list of dicts
        book_list = [dict(row) for row in results]
        
        if not book_list:
            return {"status": "Found", "message": f"No books found matching '{q}' by {column}.", "books": []}

        return {"status": "Success", "message": f"Found {len(book_list)} book(s).", "books": book_list}
        
    except sqlite3.Error as e:
        return {"status": "Error", "message": f"Database error during find_books: {e}"}
        
    finally:
        conn.close()


def create_order(customer_id: int, items: List[Dict[str, Union[str, int]]]) -> Dict:
    """
    Creates a new order, adds items, and crucially, reduces book stock.
    This function uses a transaction to ensure all steps complete successfully.

    :param customer_id: ID of the customer.
    :param items: List of items: [{'isbn': str, 'qty': int}].
    :return: Dictionary with new order_id, status, and updated stock details.
    """
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # 1. Check Customer Exists
        cursor.execute("SELECT id FROM customers WHERE id = ?", (customer_id,))
        if cursor.fetchone() is None:
            raise Exception(f"Customer ID {customer_id} not found.")

        # 2. Create the main Order record
        cursor.execute("INSERT INTO orders (customer_id) VALUES (?)", (customer_id,))
        order_id = cursor.lastrowid
        
        updated_stock = []
        
        # 3. Process each item (Check stock, reduce stock, record order_item)
        for item in items:
            isbn = item['isbn']
            qty = item['qty']
            
            cursor.execute("SELECT stock, price, title FROM books WHERE isbn = ?", (isbn,))
            book_info = cursor.fetchone()
            
            if book_info is None:
                raise Exception(f"Book with ISBN {isbn} not found.")
            
            current_stock, price, title = book_info
            
            if current_stock < qty:
                raise Exception(f"Insufficient stock for {title} (ISBN {isbn}). Requested: {qty}, Available: {current_stock}.")
                
            # Insert into order_items
            cursor.execute(
                "INSERT INTO order_items (order_id, isbn, qty, price_at_order) VALUES (?, ?, ?, ?)",
                (order_id, isbn, qty, price)
            )
            
            # Update stock in the books table
            new_stock = current_stock - qty
            cursor.execute("UPDATE books SET stock = ? WHERE isbn = ?", (new_stock, isbn))
            updated_stock.append({"isbn": isbn, "title": title, "new_stock": new_stock})
            
        # 4. Commit Transaction (save all changes)
        conn.commit()
        return {
            "status": "Success", 
            "order_id": order_id, 
            "summary": f"Order {order_id} created for customer {customer_id}.",
            "updated_stock": updated_stock
        }

    except Exception as e:
        conn.rollback() # If any error occurs, undo everything
        return {"status": "Error", "message": str(e)}
        
    finally:
        conn.close()


def restock_book(isbn: str, qty: int) -> Dict:
    """Restocks a book by adding the given quantity and returns the new stock level."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE books SET stock = stock + ? WHERE isbn = ?", (qty, isbn))
        
        if cursor.rowcount == 0:
            conn.close()
            return {"status": "Error", "message": f"Book with ISBN {isbn} not found."}
        
        cursor.execute("SELECT title, stock FROM books WHERE isbn = ?", (isbn,))
        result = cursor.fetchone()
        
        conn.commit()
        return {"status": "Success", "isbn": isbn, "title": result['title'], "new_stock": result['stock']}
    except sqlite3.Error as e:
        conn.rollback()
        return {"status": "Error", "message": f"Database error during restock_book: {e}"}
    finally:
        conn.close()


def update_price(isbn: str, price: float) -> Dict:
    """Updates the price of a book."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE books SET price = ? WHERE isbn = ?", (price, isbn))
        
        if cursor.rowcount == 0:
            conn.close()
            return {"status": "Error", "message": f"Book with ISBN {isbn} not found."}

        cursor.execute("SELECT title, price FROM books WHERE isbn = ?", (isbn,))
        result = cursor.fetchone()
        
        conn.commit()
        return {"status": "Success", "isbn": isbn, "title": result['title'], "new_price": round(result['price'], 2)}
    except sqlite3.Error as e:
        conn.rollback()
        return {"status": "Error", "message": f"Database error during update_price: {e}"}
    finally:
        conn.close()


def order_status(order_id: int) -> Dict:
    """Retrieves the status and details of an order."""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        order_query = """
        SELECT o.id, c.name, o.order_date
        FROM orders o JOIN customers c ON o.customer_id = c.id
        WHERE o.id = ?
        """
        cursor.execute(order_query, (order_id,))
        order_info = cursor.fetchone()
        
        if order_info is None:
            return {"status": "Error", "message": f"Order ID {order_id} not found."}
            
        # Use row access by key (name)
        customer_name = order_info['name']
        order_date = order_info['order_date']

        items_query = """
        SELECT oi.isbn, b.title, oi.qty, oi.price_at_order, (oi.qty * oi.price_at_order) as subtotal
        FROM order_items oi JOIN books b ON oi.isbn = b.isbn
        WHERE oi.order_id = ?
        """
        items_results = cursor.execute(items_query, (order_id,)).fetchall()
        
        total_price = sum(item['subtotal'] for item in items_results)
        
        items_list = [dict(row) for row in items_results]
        
        return {
            "status": "Found",
            "order_id": order_id,
            "customer_name": customer_name,
            "order_date": order_date,
            "items": items_list,
            "total_price": round(total_price, 2)
        }
    except sqlite3.Error as e:
        return {"status": "Error", "message": f"Database error during order_status: {e}"}
    finally:
        conn.close()


def inventory_summary() -> Dict:
    """Provides a summary of inventory and lists low-stock titles."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(isbn) as unique_books, SUM(stock) as total_stock FROM books")
        summary_result = cursor.fetchone()
        unique_books = summary_result['unique_books']
        total_stock = summary_result['total_stock']
        
        LOW_STOCK_THRESHOLD = 5
        cursor.execute("SELECT title, stock FROM books WHERE stock <= ?", (LOW_STOCK_THRESHOLD,))
        low_stock_results = cursor.fetchall()
        
        low_stock_titles = [dict(row) for row in low_stock_results]
        
        return {
            "status": "Success",
            "total_unique_books": unique_books if unique_books is not None else 0,
            "total_inventory_quantity": total_stock if total_stock is not None else 0,
            "low_stock_threshold": LOW_STOCK_THRESHOLD,
            "low_stock_titles": low_stock_titles
        }
    except sqlite3.Error as e:
        return {"status": "Error", "message": f"Database error during inventory_summary: {e}"}
    finally:
        conn.close()
        
# --- HISTORY PERSISTENCE FUNCTIONS (New) ---

def load_history(session_id: str) -> Dict:
    """
    Loads all messages for a given session ID.

    :param session_id: The unique identifier for the chat session.
    :return: Dictionary containing status and a list of message dicts ({'role': str, 'content': str}).
    """
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = "SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at ASC"
        results = cursor.execute(query, (session_id,)).fetchall()

        history_list = [dict(row) for row in results]

        return {"status": "Success", "history": history_list}
    except sqlite3.Error as e:
        return {"status": "Error", "message": f"Database error during load_history: {e}"}
    finally:
        conn.close()

def save_message(session_id: str, role: str, content: str) -> Dict:
    """
    Saves a single message (user or assistant) to the database.
    """
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)"
        cursor.execute(query, (session_id, role, content))
        conn.commit()
        return {"status": "Success"}
    except sqlite3.Error as e:
        conn.rollback()
        return {"status": "Error", "message": f"Database error during save_message: {e}"}
    finally:
        conn.close()
