<h1 align="center">Sales / Business Management System</h1>

<p align="center">
A business management application built using Python, SQLite, and Streamlit
</p>

---

## Overview

This project is a business management system that allows users to manage products, customers, and sales efficiently using a simple interface.

---

## Features

* Product Management (Add, View, Update, Delete)
* Customer Management (Add, View, Update, Delete)
* Sales Management (Record sales, update stock automatically)
* Dashboard with business insights
* PDF bill generation for each sale

---

## Product Management

Manage products with the following fields:

* ID
* Name
* Category
* Price
* Stock

Supports full CRUD operations.

---

## Customer Management

Store customer details including:

* ID
* Name
* Phone
* Email
* Address

Includes validation for email and phone.

---

## Sales Management

* Select product and customer
* Enter quantity
* Automatically calculate total price
* Update stock after each sale
* View sales history

---

## Dashboard

Displays:

* Total sales amount
* Total number of products
* Total number of customers

---

## PDF Bill

Each sale generates a downloadable bill containing:

* Sale ID
* Product name
* Customer name
* Quantity
* Total amount
* Date

---

## Technologies Used

* Python
* SQLite
* Streamlit
* Pandas
* ReportLab

---

## How to Run

```bash
pip install streamlit pandas reportlab
streamlit run app.py
```

---

## Learning Outcomes

* Understanding CRUD operations
* Working with SQLite database
* Building user interfaces using Streamlit
* Implementing real-world business logic
* Generating PDF files

---

## Author

Aayusha Karki
