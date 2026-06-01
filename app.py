import streamlit as st
import sqlite3
import pandas as pd
import re
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas

# ---------- DATABASE ----------
conn = sqlite3.connect("business.db", check_same_thread=False)
cursor = conn.cursor()

# CREATE TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    price REAL,
    stock INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    email TEXT,
    address TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    customer_id INTEGER,
    quantity INTEGER,
    total REAL,
    date TEXT
)
""")

conn.commit()

#---------HELPING FUNCTIONM FOR REGEX---------
def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)

def is_valid_phone(phone):
    pattern = r"^\+?[0-9]{7,15}$"
    return re.match(pattern, phone)

def is_valid_price(price):
    pattern = r"^\d+(\.\d{1,2})?$"
    return re.match(pattern, str(price))

def is_valid_stock(stock):
    pattern = r"^\d+$"
    return re.match(pattern, str(stock))


# ---------- MENU ----------
menu = st.sidebar.selectbox("Menu", ["Dashboard", "Products", "Customers", "Sales"])

# ---------- DASHBOARD ----------
if menu == "Dashboard":
    st.title("📊 Dashboard")

    total_sales = cursor.execute("SELECT SUM(total) FROM sales").fetchone()[0]
    product_count = cursor.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    customer_count = cursor.execute("SELECT COUNT(*) FROM customers").fetchone()[0]

    st.metric("Total Sales", total_sales if total_sales else 0)
    st.metric("Products", product_count)
    st.metric("Customers", customer_count)

# ---------- PRODUCTS ----------
elif menu == "Products":
    st.title("📦 Product Management")

    # ADD
    with st.form("add_product"):
        st.subheader("Add Product")
        name = st.text_input("Name")
        category = st.text_input("Category")
        price = st.number_input("Price")
        stock = st.number_input("Stock", step=1)

        if st.form_submit_button("Add Product"):
                if not is_valid_price(price):
                 st.error("Invalid price!")

                elif not is_valid_stock(stock):
                    st.error("Invalid stock value!")

                else:    
                    cursor.execute(
                        "INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
                        (name, category, price, stock)
                    )
                    conn.commit()
                    st.success("Product added!")

    # VIEW
    st.subheader("Product List")
    products = cursor.execute("SELECT * FROM products").fetchall()
    product_df = pd.DataFrame(
        products,
        columns=["ID", "Product Name", "Category", "Price", "Stock"]
    )

    st.table(product_df)

    product_ids = [p[0] for p in products]

    # UPDATE
    st.subheader("Update Product")
    if product_ids:
        selected_id = st.selectbox("Select Product ID", product_ids)

        new_name = st.text_input("New Name")
        new_category = st.text_input("New Category")
        new_price = st.number_input("New Price")
        new_stock = st.number_input("New Stock", step=1)

        if st.button("Update Product"):
            cursor.execute("""
                UPDATE products 
                SET name=?, category=?, price=?, stock=? 
                WHERE id=?
            """, (new_name, new_category, new_price, new_stock, selected_id))
            conn.commit()
            st.success("Product updated!")

    # DELETE
    st.subheader("Delete Product")
    if product_ids:
        delete_id = st.selectbox("Select ID to Delete", product_ids, key="delete_p")

        if st.button("Delete Product"):
            cursor.execute("DELETE FROM products WHERE id=?", (delete_id,))
            conn.commit()
            st.warning("Product deleted!")

# ---------- CUSTOMERS ----------
elif menu == "Customers":
    st.title("👤 Customer Management")

    # ADD
    with st.form("add_customer"):
        st.subheader("Add Customer")
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        email = st.text_input("Email")
        address = st.text_input("Address")

        if st.form_submit_button("Add Customer"):
            if not is_valid_phone(phone):
                st.error("Invalid phone number!")

            elif not is_valid_email(email):
                st.error("Invalid email format!")
            else:
                cursor.execute(
                    "INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?)",
                    (name, phone, email, address)
                )
                conn.commit()
                st.success("Customer added!")

    # VIEW
    st.subheader("Customer List")
    customers = cursor.execute("SELECT * FROM customers").fetchall()
    customer_df = pd.DataFrame(
        customers,
        columns=["ID", "Name", "Phone", "Email", "Address"]
    )

    st.table(customer_df)

    customer_ids = [c[0] for c in customers]

    # UPDATE
    st.subheader("Update Customer")
    if customer_ids:
        selected_id = st.selectbox("Select Customer ID", customer_ids)

        new_name = st.text_input("New Name")
        new_phone = st.text_input("New Phone")
        new_email = st.text_input("New Email")
        new_address = st.text_input("New Address")

        if st.button("Update Customer"):
            cursor.execute("""
                UPDATE customers 
                SET name=?, phone=?, email=?, address=? 
                WHERE id=?
            """, (new_name, new_phone, new_email, new_address, selected_id))
            conn.commit()
            st.success("Customer updated!")

    # DELETE
    st.subheader("Delete Customer")
    if customer_ids:
        delete_id = st.selectbox("Select ID to Delete", customer_ids, key="delete_c")

        if st.button("Delete Customer"):
            cursor.execute("DELETE FROM customers WHERE id=?", (delete_id,))
            conn.commit()
            st.warning("Customer deleted!")

# ---------- SALES ----------
elif menu == "Sales":
    st.title("🧾 Sales Management")

    products = cursor.execute("SELECT * FROM products").fetchall()
    customers = cursor.execute("SELECT * FROM customers").fetchall()

    if not products or not customers:
        st.warning("Add products and customers first!")
    else:
        product_dict = {p[1]: p for p in products}
        customer_dict = {c[1]: c for c in customers}

        product_name = st.selectbox("Select Product", list(product_dict.keys()))
        customer_name = st.selectbox("Select Customer", list(customer_dict.keys()))
        quantity = st.number_input("Quantity", min_value=1)

        if st.button("Record Sale"):
            product = product_dict[product_name]
            customer = customer_dict[customer_name]

            total = product[3] * quantity
            new_stock = product[4] - quantity

            if new_stock < 0:
                st.error("Not enough stock!")
            else:
                cursor.execute("""
                    INSERT INTO sales (product_id, customer_id, quantity, total, date)
                    VALUES (?, ?, ?, ?, ?)
                """, (product[0], customer[0], quantity, total, datetime.now()))

                cursor.execute("UPDATE products SET stock=? WHERE id=?",
                               (new_stock, product[0]))

                conn.commit()
                st.success(f"Sale recorded! Total = {total}")
        # ---------- PDF BILL GENERATOR ----------
    def generate_bill(sale, product_name, customer_name):

        buffer = BytesIO()

        p = canvas.Canvas(buffer)

        p.setFont("Helvetica-Bold", 18)
        p.drawString(200, 800, "SALES BILL")

        p.setFont("Helvetica", 12)

        p.drawString(50, 740, f"Sale ID: {sale[0]}")
        p.drawString(50, 720, f"Product: {product_name}")
        p.drawString(50, 700, f"Customer: {customer_name}")
        p.drawString(50, 680, f"Quantity: {sale[3]}")
        p.drawString(50, 660, f"Total Amount: ${sale[4]}")
        p.drawString(50, 640, f"Date: {sale[5]}")

        p.line(50, 620, 550, 620)

        p.drawString(50, 590, "Thank you for your purchase!")

        p.save()

        buffer.seek(0)

        return buffer
    # VIEW SALES
    # st.markdown("""
    #     <style>

    #     .sales-row {
    #         border: 1px solid #888;
    #         border-radius: 7px;
    #         padding: 0.5px;
    #         margin-bottom: 10px;
    #         background-color: #111;
    #     }

    #     </style>
    #     """, unsafe_allow_html=True)
    st.subheader("Sales History")
    sales = cursor.execute("SELECT * FROM sales").fetchall()
    # sales_df = pd.DataFrame(
    #     sales,
    #     columns=[
    #         "Sale ID",
    #         "Product ID",
    #         "Customer ID",
    #         "Quantity",
    #         "Total",
    #         "Date"
    #     ]
    # )
    if sales:

            # HEADER
        h1, h2, h3, h4, h5, h6, h7 = st.columns([1,2,2,1,1,2,1])

        h1.markdown("**Sale ID**")
        h2.markdown("**Product**")
        h3.markdown("**Customer**")
        h4.markdown("**Qty**")
        h5.markdown("**Total**")
        h6.markdown("**Date**")
        h7.markdown("**Bill**")

        st.divider()

        for sale in sales:
            # st.markdown('<div class="sales-row">', unsafe_allow_html=True)

            sale_id = sale[0]
            product_id = sale[1]
            customer_id = sale[2]
            quantity = sale[3]
            total = sale[4]
            date = sale[5]

            # Product name
            product = cursor.execute(
                "SELECT name FROM products WHERE id=?",
                (product_id,)
            ).fetchone()

            product_name = product[0] if product else "Unknown"

            # Customer name
            customer = cursor.execute(
                "SELECT name FROM customers WHERE id=?",
                (customer_id,)
            ).fetchone()

            customer_name = customer[0] if customer else "Unknown"

            # Generate PDF
            pdf = generate_bill(sale, product_name, customer_name)

            # ROW
            c1, c2, c3, c4, c5, c6, c7 = st.columns([1,2,2,1,1,2,1])

            c1.write(sale_id)
            c2.write(product_name)
            c3.write(customer_name)
            c4.write(quantity)
            c5.write(f"${total}")
            c6.write(date)

            c7.download_button(
                label="🧾 Bill",
                data=pdf,
                file_name=f"bill_{sale_id}.pdf",
                mime="application/pdf",
                key=f"bill_{sale_id}"
            )
            # st.markdown('</div>', unsafe_allow_html=True)
            st.divider()