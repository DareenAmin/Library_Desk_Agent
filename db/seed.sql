-- Seed Customers (6 total)
INSERT INTO customers (id, name, email) VALUES
(1, 'Dareen Mahboobeh', 'dareen@example.com'),
(2, 'Moh''d Mattar', 'mohd@example.com'),
(3, 'Faisal Al-Rashed', 'faisal@example.com'),
(4, 'Lina Hadid', 'lina@example.com'),
(5, 'Omar Qasem', 'omar@example.com'),
(6, 'Rania Youssef', 'rania@example.com');


-- Seed Books (10 total)
INSERT INTO books (isbn, title, author, stock, price) VALUES
('978-0134494166', 'The Pragmatic Programmer', 'Andrew Hunt', 15, 45.99),
('978-0132350884', 'Clean Code', 'Robert C. Martin', 5, 39.50),
('978-0321765723', 'The Mythical Man-Month', 'Frederick Brooks', 8, 
29.95),
('978-0321773025', 'Refactoring', 'Martin Fowler', 12, 55.00),
('978-0596517748', 'Head First Design Patterns', 'Eric Freeman', 7, 
49.99),
('978-0201485677', 'Design Patterns', 'Erich Gamma', 20, 65.50),
('978-1934356073', 'Code Complete', 'Steve McConnell', 10, 35.00),
('978-1449331009', 'The Phoenix Project', 'Gene Kim', 18, 25.75),
('978-0133742911', 'Data Science for Business', 'Foster Provost', 9, 
70.00),
('978-0321721514', 'Structure and Interpretation of Computer Programs', 
'Harold Abelson', 11, 40.00);


-- Seed Orders (4 total)
-- Order 101: Dareen Mahboobeh (2 items)
INSERT INTO orders (id, customer_id) VALUES (101, 1);
INSERT INTO order_items (order_id, isbn, qty, price_at_order) VALUES
(101, '978-0134494166', 1, 45.99), -- The Pragmatic Programmer
(101, '978-0321765723', 3, 29.95); -- The Mythical Man-Month

-- Order 102: Moh'd Mattar (1 item)
INSERT INTO orders (id, customer_id) VALUES (102, 2);
INSERT INTO order_items (order_id, isbn, qty, price_at_order) VALUES
(102, '978-0132350884', 2, 39.50); -- Clean Code

-- Order 103: Faisal Al-Rashed (1 item)
INSERT INTO orders (id, customer_id) VALUES (103, 3);
INSERT INTO order_items (order_id, isbn, qty, price_at_order) VALUES
(103, '978-0596517748', 1, 49.99); -- Head First Design Patterns

-- Order 104: Lina Hadid (2 items)
INSERT INTO orders (id, customer_id) VALUES (104, 4);
INSERT INTO order_items (order_id, isbn, qty, price_at_order) VALUES
(104, '978-0321773025', 1, 55.00), -- Refactoring
(104, '978-0201485677', 1, 65.50); -- Design Patterns
