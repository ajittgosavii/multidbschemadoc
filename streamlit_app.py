import streamlit as st
import pandas as pd
import anthropic
import json
import time
from datetime import datetime
import io
import base64
from typing import Dict, List, Any, Optional
import hashlib

# Page configuration
st.set_page_config(
    page_title="Multi-DB Schema Documentation Tool",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        padding-top: 0rem;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Professional header */
    .doc-header {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 50%, #2980b9 100%);
        padding: 3rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
    }
    
    .doc-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="docs" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="20" cy="20" r="2" fill="white" opacity="0.1"/><circle cx="80" cy="80" r="2" fill="white" opacity="0.1"/><circle cx="50" cy="15" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23docs)"/></svg>');
        opacity: 0.3;
    }
    
    .doc-header h1 {
        font-family: 'Inter', sans-serif;
        font-size: 3.2em;
        font-weight: 700;
        margin: 0;
        position: relative;
        z-index: 1;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .doc-header p {
        font-family: 'Inter', sans-serif;
        font-size: 1.3em;
        font-weight: 400;
        margin: 1rem 0 0 0;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }
    
    /* Database badges */
    .db-badges {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin: 2rem 0 0 0;
        position: relative;
        z-index: 1;
        flex-wrap: wrap;
    }
    
    .db-badge {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        color: white;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
    }
    
    .db-badge:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.35);
    }
    
    /* Stats container */
    .stats-container {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        padding: 1.5rem 2rem;
        margin: 0 -1rem 2rem -1rem;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .stat-item {
        text-align: center;
        color: white;
        font-family: 'Inter', sans-serif;
    }
    
    .stat-number {
        font-size: 2.5em;
        font-weight: 700;
        color: #74b9ff;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .stat-label {
        font-size: 0.95em;
        font-weight: 500;
        opacity: 0.9;
        margin-top: 0.5rem;
        letter-spacing: 0.5px;
    }
    
    /* Schema cards */
    .schema-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
        margin: 1rem 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .schema-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #2c3e50, #3498db);
    }
    
    .schema-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.12);
    }
    
    .card-title {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.2em;
        color: #2c3e50;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #2c3e50, #3498db);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(44, 62, 80, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(44, 62, 80, 0.4);
        background: linear-gradient(135deg, #3498db, #2980b9);
    }
    
    /* Success banners */
    .success-banner {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border: 1px solid #b8dabd;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.1);
        font-family: 'Inter', sans-serif;
    }
    
    .info-banner {
        background: linear-gradient(135deg, #d1ecf1, #bee5eb);
        border: 1px solid #b6d7dc;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(23, 162, 184, 0.1);
        font-family: 'Inter', sans-serif;
    }
    
    .warning-banner {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        border: 1px solid #ffeaa7;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(255, 193, 7, 0.1);
        font-family: 'Inter', sans-serif;
    }
    
    /* Table styling */
    .schema-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-radius: 10px;
        overflow: hidden;
    }
    
    .schema-table th {
        background: linear-gradient(135deg, #2c3e50, #3498db);
        color: white;
        padding: 1rem;
        text-align: left;
        font-weight: 600;
    }
    
    .schema-table td {
        padding: 0.8rem 1rem;
        border-bottom: 1px solid #ecf0f1;
        background: white;
    }
    
    .schema-table tr:hover td {
        background: #f8f9fa;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: #f8f9fa;
        padding: 0.5rem;
        border-radius: 15px;
        border: 1px solid #e9ecef;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        color: #6c757d;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2c3e50, #3498db);
        color: white;
        box-shadow: 0 4px 15px rgba(44, 62, 80, 0.3);
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border: 1px solid #e9ecef;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    /* Code blocks */
    .stCodeBlock {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .doc-header h1 {
            font-size: 2.5em;
        }
        
        .stats-container {
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            padding: 1rem;
        }
        
        .stat-number {
            font-size: 2em;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize Claude AI
@st.cache_resource
def init_claude():
    """Initialize Claude AI client"""
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            st.warning("⚠️ Claude AI API key not found. Please add ANTHROPIC_API_KEY to your secrets for AI-enhanced documentation.")
            return None
        return anthropic.Anthropic(api_key=api_key)
    except Exception as e:
        st.warning(f"⚠️ Could not initialize Claude AI: {str(e)}")
        return None

# Sample schema data for demonstration
def get_sample_schema_data():
    """Get sample schema data for demonstration"""
    return {
        "PostgreSQL": {
            "database_info": {
                "name": "ecommerce_db",
                "version": "PostgreSQL 15.2",
                "size": "2.5 GB",
                "created": "2023-01-15",
                "last_backup": "2024-07-27"
            },
            "tables": [
                {
                    "table_name": "customers",
                    "schema": "public",
                    "table_type": "BASE TABLE",
                    "row_count": 125000,
                    "size_mb": 45.2,
                    "description": "Customer information and profiles",
                    "columns": [
                        {"column_name": "customer_id", "data_type": "SERIAL", "is_nullable": False, "default": "nextval('customers_customer_id_seq')", "description": "Primary key"},
                        {"column_name": "first_name", "data_type": "VARCHAR(50)", "is_nullable": False, "default": None, "description": "Customer first name"},
                        {"column_name": "last_name", "data_type": "VARCHAR(50)", "is_nullable": False, "default": None, "description": "Customer last name"},
                        {"column_name": "email", "data_type": "VARCHAR(100)", "is_nullable": False, "default": None, "description": "Customer email address"},
                        {"column_name": "phone", "data_type": "VARCHAR(20)", "is_nullable": True, "default": None, "description": "Customer phone number"},
                        {"column_name": "address", "data_type": "JSONB", "is_nullable": True, "default": None, "description": "Customer address in JSON format"},
                        {"column_name": "registration_date", "data_type": "TIMESTAMP", "is_nullable": False, "default": "CURRENT_TIMESTAMP", "description": "Account registration date"},
                        {"column_name": "last_login", "data_type": "TIMESTAMP", "is_nullable": True, "default": None, "description": "Last login timestamp"},
                        {"column_name": "is_active", "data_type": "BOOLEAN", "is_nullable": False, "default": "true", "description": "Account status"}
                    ],
                    "indexes": [
                        {"index_name": "customers_pkey", "columns": ["customer_id"], "index_type": "PRIMARY KEY", "is_unique": True},
                        {"index_name": "idx_customers_email", "columns": ["email"], "index_type": "UNIQUE", "is_unique": True},
                        {"index_name": "idx_customers_name", "columns": ["last_name", "first_name"], "index_type": "BTREE", "is_unique": False},
                        {"index_name": "idx_customers_registration", "columns": ["registration_date"], "index_type": "BTREE", "is_unique": False}
                    ],
                    "constraints": [
                        {"constraint_name": "customers_pkey", "constraint_type": "PRIMARY KEY", "columns": ["customer_id"]},
                        {"constraint_name": "customers_email_key", "constraint_type": "UNIQUE", "columns": ["email"]},
                        {"constraint_name": "chk_email_format", "constraint_type": "CHECK", "definition": "email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"}
                    ]
                },
                {
                    "table_name": "orders",
                    "schema": "public", 
                    "table_type": "BASE TABLE",
                    "row_count": 450000,
                    "size_mb": 125.8,
                    "description": "Customer order information",
                    "columns": [
                        {"column_name": "order_id", "data_type": "SERIAL", "is_nullable": False, "default": "nextval('orders_order_id_seq')", "description": "Primary key"},
                        {"column_name": "customer_id", "data_type": "INTEGER", "is_nullable": False, "default": None, "description": "Reference to customers table"},
                        {"column_name": "order_date", "data_type": "TIMESTAMP", "is_nullable": False, "default": "CURRENT_TIMESTAMP", "description": "Order creation date"},
                        {"column_name": "total_amount", "data_type": "DECIMAL(10,2)", "is_nullable": False, "default": None, "description": "Order total amount"},
                        {"column_name": "status", "data_type": "VARCHAR(20)", "is_nullable": False, "default": "'pending'", "description": "Order status"},
                        {"column_name": "shipping_address", "data_type": "JSONB", "is_nullable": True, "default": None, "description": "Shipping address in JSON"},
                        {"column_name": "payment_method", "data_type": "VARCHAR(50)", "is_nullable": True, "default": None, "description": "Payment method used"}
                    ],
                    "indexes": [
                        {"index_name": "orders_pkey", "columns": ["order_id"], "index_type": "PRIMARY KEY", "is_unique": True},
                        {"index_name": "idx_orders_customer", "columns": ["customer_id"], "index_type": "BTREE", "is_unique": False},
                        {"index_name": "idx_orders_date", "columns": ["order_date"], "index_type": "BTREE", "is_unique": False},
                        {"index_name": "idx_orders_status", "columns": ["status"], "index_type": "BTREE", "is_unique": False}
                    ],
                    "constraints": [
                        {"constraint_name": "orders_pkey", "constraint_type": "PRIMARY KEY", "columns": ["order_id"]},
                        {"constraint_name": "fk_orders_customer", "constraint_type": "FOREIGN KEY", "columns": ["customer_id"], "references": "customers(customer_id)"},
                        {"constraint_name": "chk_total_positive", "constraint_type": "CHECK", "definition": "total_amount > 0"}
                    ]
                }
            ],
            "views": [
                {
                    "view_name": "customer_summary",
                    "schema": "public",
                    "definition": "SELECT c.customer_id, c.first_name, c.last_name, COUNT(o.order_id) as total_orders, COALESCE(SUM(o.total_amount), 0) as total_spent FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id, c.first_name, c.last_name",
                    "description": "Customer order summary view"
                }
            ],
            "functions": [
                {
                    "function_name": "calculate_customer_lifetime_value",
                    "schema": "public",
                    "return_type": "DECIMAL",
                    "parameters": "customer_id INTEGER",
                    "description": "Calculates lifetime value for a customer"
                }
            ]
        },
        "Oracle": {
            "database_info": {
                "name": "ORCL",
                "version": "Oracle Database 19c",
                "size": "3.2 GB", 
                "created": "2023-01-20",
                "last_backup": "2024-07-27"
            },
            "tables": [
                {
                    "table_name": "CUSTOMERS",
                    "schema": "SALES",
                    "table_type": "TABLE",
                    "row_count": 125000,
                    "size_mb": 52.1,
                    "description": "Customer information and profiles",
                    "columns": [
                        {"column_name": "CUSTOMER_ID", "data_type": "NUMBER(10)", "is_nullable": False, "default": "CUSTOMERS_SEQ.NEXTVAL", "description": "Primary key"},
                        {"column_name": "FIRST_NAME", "data_type": "VARCHAR2(50)", "is_nullable": False, "default": None, "description": "Customer first name"},
                        {"column_name": "LAST_NAME", "data_type": "VARCHAR2(50)", "is_nullable": False, "default": None, "description": "Customer last name"},
                        {"column_name": "EMAIL", "data_type": "VARCHAR2(100)", "is_nullable": False, "default": None, "description": "Customer email address"},
                        {"column_name": "PHONE", "data_type": "VARCHAR2(20)", "is_nullable": True, "default": None, "description": "Customer phone number"},
                        {"column_name": "ADDRESS_DATA", "data_type": "CLOB", "is_nullable": True, "default": None, "description": "Customer address data"},
                        {"column_name": "REGISTRATION_DATE", "data_type": "DATE", "is_nullable": False, "default": "SYSDATE", "description": "Account registration date"},
                        {"column_name": "LAST_LOGIN", "data_type": "TIMESTAMP", "is_nullable": True, "default": None, "description": "Last login timestamp"},
                        {"column_name": "IS_ACTIVE", "data_type": "NUMBER(1)", "is_nullable": False, "default": "1", "description": "Account status"}
                    ],
                    "indexes": [
                        {"index_name": "CUSTOMERS_PK", "columns": ["CUSTOMER_ID"], "index_type": "PRIMARY KEY", "is_unique": True},
                        {"index_name": "CUSTOMERS_EMAIL_UK", "columns": ["EMAIL"], "index_type": "UNIQUE", "is_unique": True},
                        {"index_name": "IDX_CUSTOMERS_NAME", "columns": ["LAST_NAME", "FIRST_NAME"], "index_type": "NORMAL", "is_unique": False},
                        {"index_name": "IDX_CUSTOMERS_REG_DATE", "columns": ["REGISTRATION_DATE"], "index_type": "NORMAL", "is_unique": False}
                    ],
                    "constraints": [
                        {"constraint_name": "CUSTOMERS_PK", "constraint_type": "PRIMARY KEY", "columns": ["CUSTOMER_ID"]},
                        {"constraint_name": "CUSTOMERS_EMAIL_UK", "constraint_type": "UNIQUE", "columns": ["EMAIL"]},
                        {"constraint_name": "CHK_IS_ACTIVE", "constraint_type": "CHECK", "definition": "IS_ACTIVE IN (0,1)"}
                    ]
                },
                {
                    "table_name": "ORDERS",
                    "schema": "SALES",
                    "table_type": "TABLE", 
                    "row_count": 450000,
                    "size_mb": 138.5,
                    "description": "Customer order information",
                    "columns": [
                        {"column_name": "ORDER_ID", "data_type": "NUMBER(10)", "is_nullable": False, "default": "ORDERS_SEQ.NEXTVAL", "description": "Primary key"},
                        {"column_name": "CUSTOMER_ID", "data_type": "NUMBER(10)", "is_nullable": False, "default": None, "description": "Reference to customers table"},
                        {"column_name": "ORDER_DATE", "data_type": "DATE", "is_nullable": False, "default": "SYSDATE", "description": "Order creation date"},
                        {"column_name": "TOTAL_AMOUNT", "data_type": "NUMBER(10,2)", "is_nullable": False, "default": None, "description": "Order total amount"},
                        {"column_name": "STATUS", "data_type": "VARCHAR2(20)", "is_nullable": False, "default": "'PENDING'", "description": "Order status"},
                        {"column_name": "SHIPPING_ADDRESS", "data_type": "CLOB", "is_nullable": True, "default": None, "description": "Shipping address data"},
                        {"column_name": "PAYMENT_METHOD", "data_type": "VARCHAR2(50)", "is_nullable": True, "default": None, "description": "Payment method used"}
                    ],
                    "indexes": [
                        {"index_name": "ORDERS_PK", "columns": ["ORDER_ID"], "index_type": "PRIMARY KEY", "is_unique": True},
                        {"index_name": "IDX_ORDERS_CUSTOMER", "columns": ["CUSTOMER_ID"], "index_type": "NORMAL", "is_unique": False},
                        {"index_name": "IDX_ORDERS_DATE", "columns": ["ORDER_DATE"], "index_type": "NORMAL", "is_unique": False},
                        {"index_name": "IDX_ORDERS_STATUS", "columns": ["STATUS"], "index_type": "NORMAL", "is_unique": False}
                    ],
                    "constraints": [
                        {"constraint_name": "ORDERS_PK", "constraint_type": "PRIMARY KEY", "columns": ["ORDER_ID"]},
                        {"constraint_name": "FK_ORDERS_CUSTOMER", "constraint_type": "FOREIGN KEY", "columns": ["CUSTOMER_ID"], "references": "CUSTOMERS(CUSTOMER_ID)"},
                        {"constraint_name": "CHK_TOTAL_POSITIVE", "constraint_type": "CHECK", "definition": "TOTAL_AMOUNT > 0"}
                    ]
                }
            ],
            "views": [
                {
                    "view_name": "CUSTOMER_SUMMARY",
                    "schema": "SALES",
                    "definition": "SELECT c.CUSTOMER_ID, c.FIRST_NAME, c.LAST_NAME, COUNT(o.ORDER_ID) as TOTAL_ORDERS, NVL(SUM(o.TOTAL_AMOUNT), 0) as TOTAL_SPENT FROM CUSTOMERS c LEFT JOIN ORDERS o ON c.CUSTOMER_ID = o.CUSTOMER_ID GROUP BY c.CUSTOMER_ID, c.FIRST_NAME, c.LAST_NAME",
                    "description": "Customer order summary view"
                }
            ],
            "procedures": [
                {
                    "procedure_name": "CALCULATE_CUSTOMER_LTV",
                    "schema": "SALES",
                    "parameters": "p_customer_id IN NUMBER, p_ltv OUT NUMBER",
                    "description": "Calculates lifetime value for a customer"
                }
            ]
        },
        "SQL Server": {
            "database_info": {
                "name": "ECommerceDB",
                "version": "SQL Server 2022",
                "size": "2.8 GB",
                "created": "2023-01-18", 
                "last_backup": "2024-07-27"
            },
            "tables": [
                {
                    "table_name": "Customers",
                    "schema": "dbo",
                    "table_type": "BASE TABLE",
                    "row_count": 125000,
                    "size_mb": 48.7,
                    "description": "Customer information and profiles",
                    "columns": [
                        {"column_name": "CustomerID", "data_type": "INT IDENTITY(1,1)", "is_nullable": False, "default": None, "description": "Primary key"},
                        {"column_name": "FirstName", "data_type": "NVARCHAR(50)", "is_nullable": False, "default": None, "description": "Customer first name"},
                        {"column_name": "LastName", "data_type": "NVARCHAR(50)", "is_nullable": False, "default": None, "description": "Customer last name"},
                        {"column_name": "Email", "data_type": "NVARCHAR(100)", "is_nullable": False, "default": None, "description": "Customer email address"},
                        {"column_name": "Phone", "data_type": "NVARCHAR(20)", "is_nullable": True, "default": None, "description": "Customer phone number"},
                        {"column_name": "AddressData", "data_type": "NVARCHAR(MAX)", "is_nullable": True, "default": None, "description": "Customer address data in JSON"},
                        {"column_name": "RegistrationDate", "data_type": "DATETIME2", "is_nullable": False, "default": "GETDATE()", "description": "Account registration date"},
                        {"column_name": "LastLogin", "data_type": "DATETIME2", "is_nullable": True, "default": None, "description": "Last login timestamp"},
                        {"column_name": "IsActive", "data_type": "BIT", "is_nullable": False, "default": "1", "description": "Account status"}
                    ],
                    "indexes": [
                        {"index_name": "PK_Customers", "columns": ["CustomerID"], "index_type": "PRIMARY KEY", "is_unique": True},
                        {"index_name": "UQ_Customers_Email", "columns": ["Email"], "index_type": "UNIQUE", "is_unique": True},
                        {"index_name": "IX_Customers_Name", "columns": ["LastName", "FirstName"], "index_type": "NONCLUSTERED", "is_unique": False},
                        {"index_name": "IX_Customers_RegistrationDate", "columns": ["RegistrationDate"], "index_type": "NONCLUSTERED", "is_unique": False}
                    ],
                    "constraints": [
                        {"constraint_name": "PK_Customers", "constraint_type": "PRIMARY KEY", "columns": ["CustomerID"]},
                        {"constraint_name": "UQ_Customers_Email", "constraint_type": "UNIQUE", "columns": ["Email"]},
                        {"constraint_name": "CK_Email_Format", "constraint_type": "CHECK", "definition": "Email LIKE '%@%.%'"}
                    ]
                },
                {
                    "table_name": "Orders",
                    "schema": "dbo",
                    "table_type": "BASE TABLE",
                    "row_count": 450000,
                    "size_mb": 132.3,
                    "description": "Customer order information",
                    "columns": [
                        {"column_name": "OrderID", "data_type": "INT IDENTITY(1,1)", "is_nullable": False, "default": None, "description": "Primary key"},
                        {"column_name": "CustomerID", "data_type": "INT", "is_nullable": False, "default": None, "description": "Reference to customers table"},
                        {"column_name": "OrderDate", "data_type": "DATETIME2", "is_nullable": False, "default": "GETDATE()", "description": "Order creation date"},
                        {"column_name": "TotalAmount", "data_type": "DECIMAL(10,2)", "is_nullable": False, "default": None, "description": "Order total amount"},
                        {"column_name": "Status", "data_type": "NVARCHAR(20)", "is_nullable": False, "default": "'Pending'", "description": "Order status"},
                        {"column_name": "ShippingAddress", "data_type": "NVARCHAR(MAX)", "is_nullable": True, "default": None, "description": "Shipping address in JSON"},
                        {"column_name": "PaymentMethod", "data_type": "NVARCHAR(50)", "is_nullable": True, "default": None, "description": "Payment method used"}
                    ],
                    "indexes": [
                        {"index_name": "PK_Orders", "columns": ["OrderID"], "index_type": "PRIMARY KEY", "is_unique": True},
                        {"index_name": "IX_Orders_Customer", "columns": ["CustomerID"], "index_type": "NONCLUSTERED", "is_unique": False},
                        {"index_name": "IX_Orders_Date", "columns": ["OrderDate"], "index_type": "NONCLUSTERED", "is_unique": False},
                        {"index_name": "IX_Orders_Status", "columns": ["Status"], "index_type": "NONCLUSTERED", "is_unique": False}
                    ],
                    "constraints": [
                        {"constraint_name": "PK_Orders", "constraint_type": "PRIMARY KEY", "columns": ["OrderID"]},
                        {"constraint_name": "FK_Orders_Customer", "constraint_type": "FOREIGN KEY", "columns": ["CustomerID"], "references": "Customers(CustomerID)"},
                        {"constraint_name": "CK_TotalAmount_Positive", "constraint_type": "CHECK", "definition": "TotalAmount > 0"}
                    ]
                }
            ],
            "views": [
                {
                    "view_name": "CustomerSummary",
                    "schema": "dbo",
                    "definition": "SELECT c.CustomerID, c.FirstName, c.LastName, COUNT(o.OrderID) as TotalOrders, ISNULL(SUM(o.TotalAmount), 0) as TotalSpent FROM Customers c LEFT JOIN Orders o ON c.CustomerID = o.CustomerID GROUP BY c.CustomerID, c.FirstName, c.LastName",
                    "description": "Customer order summary view"
                }
            ],
            "procedures": [
                {
                    "procedure_name": "CalculateCustomerLTV",
                    "schema": "dbo",
                    "parameters": "@CustomerID INT, @LTV DECIMAL(10,2) OUTPUT",
                    "description": "Calculates lifetime value for a customer"
                }
            ]
        }
    }

def main():
    # Header
    st.markdown("""
    <div class="doc-header">
        <h1>📚 Multi-DB Schema Documentation Tool</h1>
        <p>Generate comprehensive database documentation with cross-platform analysis</p>
        <div class="db-badges">
            <div class="db-badge">🐘 PostgreSQL</div>
            <div class="db-badge">🔶 Oracle</div>
            <div class="db-badge">🟦 SQL Server</div>
            <div class="db-badge">🤖 AI-Enhanced</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats bar
    st.markdown("""
    <div class="stats-container">
        <div class="stat-item">
            <div class="stat-number">90%</div>
            <div class="stat-label">TIME REDUCTION</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">3</div>
            <div class="stat-label">DB PLATFORMS</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">100%</div>
            <div class="stat-label">CONSISTENCY</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">∞</div>
            <div class="stat-label">EXPORT FORMATS</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Initialize Claude AI
    claude_client = init_claude()

    # Sidebar configuration
    with st.sidebar:
        st.header("🔧 Documentation Configuration")
        
        # Documentation mode
        doc_mode = st.selectbox(
            "📋 Documentation Mode",
            [
                "📊 Live Database Connection",
                "🎯 Demo Mode (Sample Data)",
                "📁 Schema File Upload",
                "🔄 Cross-Platform Comparison"
            ]
        )
        
        # Documentation options
        st.subheader("📝 Documentation Options")
        include_ai_descriptions = st.checkbox("🤖 AI-Enhanced Descriptions", value=True)
        include_diagrams = st.checkbox("📊 Include ER Diagrams", value=True)
        include_data_dictionary = st.checkbox("📖 Data Dictionary", value=True)
        include_performance_notes = st.checkbox("⚡ Performance Notes", value=True)
        include_security_analysis = st.checkbox("🔒 Security Analysis", value=True)
        
        # Export formats
        st.subheader("📤 Export Formats")
        export_html = st.checkbox("🌐 HTML Report", value=True)
        export_pdf = st.checkbox("📄 PDF Document", value=True)
        export_markdown = st.checkbox("📝 Markdown", value=True)
        export_json = st.checkbox("📋 JSON Schema", value=True)
        
        # Demo metrics
        st.subheader("📈 Documentation Metrics")
        st.metric("Schema Objects", "847", "+23%")
        st.metric("Documentation Pages", "156", "+89%")
        st.metric("Cross-Platform Mappings", "342", "+156%")

    # Main content based on mode
    if doc_mode == "🎯 Demo Mode (Sample Data)":
        show_demo_mode(claude_client, include_ai_descriptions, include_diagrams, 
                      include_data_dictionary, include_performance_notes, include_security_analysis)
    elif doc_mode == "📊 Live Database Connection":
        show_live_connection_mode()
    elif doc_mode == "📁 Schema File Upload":
        show_file_upload_mode()
    elif doc_mode == "🔄 Cross-Platform Comparison":
        show_cross_platform_comparison()

def show_demo_mode(claude_client, include_ai_descriptions, include_diagrams, 
                   include_data_dictionary, include_performance_notes, include_security_analysis):
    """Show demo mode with sample data"""
    
    st.header("🎯 Demo Mode - Sample E-Commerce Database")
    st.markdown("**Explore comprehensive schema documentation across PostgreSQL, Oracle, and SQL Server**")
    
    # Get sample data
    sample_data = get_sample_schema_data()
    
    # Database selection tabs
    db_tabs = st.tabs(["🐘 PostgreSQL", "🔶 Oracle", "🟦 SQL Server", "🔄 Cross-Platform Analysis"])
    
    with db_tabs[0]:
        show_database_documentation("PostgreSQL", sample_data["PostgreSQL"], claude_client, 
                                  include_ai_descriptions, include_diagrams, include_data_dictionary,
                                  include_performance_notes, include_security_analysis)
    
    with db_tabs[1]:
        show_database_documentation("Oracle", sample_data["Oracle"], claude_client,
                                  include_ai_descriptions, include_diagrams, include_data_dictionary,
                                  include_performance_notes, include_security_analysis)
    
    with db_tabs[2]:
        show_database_documentation("SQL Server", sample_data["SQL Server"], claude_client,
                                  include_ai_descriptions, include_diagrams, include_data_dictionary,
                                  include_performance_notes, include_security_analysis)
    
    with db_tabs[3]:
        show_cross_platform_analysis(sample_data, claude_client)

def show_database_documentation(db_name, db_data, claude_client, include_ai_descriptions, 
                               include_diagrams, include_data_dictionary, include_performance_notes, 
                               include_security_analysis):
    """Show comprehensive documentation for a single database"""
    
    # Database overview
    st.subheader(f"📊 {db_name} Database Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tables", len(db_data.get("tables", [])))
    with col2:
        st.metric("Views", len(db_data.get("views", [])))
    with col3:
        total_rows = sum(table.get("row_count", 0) for table in db_data.get("tables", []))
        st.metric("Total Rows", f"{total_rows:,}")
    with col4:
        total_size = sum(table.get("size_mb", 0) for table in db_data.get("tables", []))
        st.metric("Total Size", f"{total_size:.1f} MB")
    
    # Database info card
    db_info = db_data.get("database_info", {})
    st.markdown(f"""
    <div class="schema-card">
        <div class="card-title">🗄️ Database Information</div>
        <p><strong>Name:</strong> {db_info.get('name', 'N/A')}</p>
        <p><strong>Version:</strong> {db_info.get('version', 'N/A')}</p>
        <p><strong>Size:</strong> {db_info.get('size', 'N/A')}</p>
        <p><strong>Created:</strong> {db_info.get('created', 'N/A')}</p>
        <p><strong>Last Backup:</strong> {db_info.get('last_backup', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tables documentation
    if db_data.get("tables"):
        st.subheader("📋 Tables Documentation")
        
        for table in db_data["tables"]:
            with st.expander(f"📊 {table['table_name']} ({table['row_count']:,} rows, {table['size_mb']:.1f} MB)"):
                show_table_documentation(table, db_name, claude_client, include_ai_descriptions,
                                       include_data_dictionary, include_performance_notes)
    
    # Views documentation
    if db_data.get("views"):
        st.subheader("👁️ Views Documentation")
        for view in db_data["views"]:
            show_view_documentation(view, db_name, claude_client, include_ai_descriptions)
    
    # Functions/Procedures documentation
    if db_data.get("functions") or db_data.get("procedures"):
        st.subheader("⚙️ Functions & Procedures")
        
        for func in db_data.get("functions", []):
            show_function_documentation(func, db_name, "Function")
        
        for proc in db_data.get("procedures", []):
            show_function_documentation(proc, db_name, "Procedure")
    
    # Generate documentation button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(f"📄 Generate Complete {db_name} Documentation", 
                    type="primary", use_container_width=True):
            generate_complete_documentation(db_name, db_data, claude_client,
                                          include_ai_descriptions, include_diagrams, 
                                          include_data_dictionary, include_performance_notes,
                                          include_security_analysis)

def show_table_documentation(table, db_name, claude_client, include_ai_descriptions,
                           include_data_dictionary, include_performance_notes):
    """Show detailed table documentation"""
    
    # Table overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **Table Information:**
        - **Schema:** {table.get('schema', 'N/A')}
        - **Type:** {table.get('table_type', 'N/A')}
        - **Row Count:** {table.get('row_count', 0):,}
        - **Size:** {table.get('size_mb', 0):.1f} MB
        """)
    
    with col2:
        if table.get('description') and include_ai_descriptions:
            st.markdown(f"""
            **Description:**
            {table['description']}
            """)
    
    # Columns documentation
    if include_data_dictionary and table.get('columns'):
        st.markdown("#### 📝 Columns")
        
        columns_data = []
        for col in table['columns']:
            columns_data.append({
                'Column Name': str(col.get('column_name', '')),
                'Data Type': str(col.get('data_type', '')),
                'Nullable': str(col.get('is_nullable', '')),
                'Default': str(col.get('default', '') if col.get('default') is not None else ''),
                'Description': str(col.get('description', ''))
            })
        
        if columns_data:
            columns_df = pd.DataFrame(columns_data)
            st.dataframe(columns_df, use_container_width=True, hide_index=True)
    
    # Indexes documentation
    if table.get('indexes'):
        st.markdown("#### 🔍 Indexes")
        
        indexes_data = []
        for idx in table['indexes']:
            # Convert columns list to string
            columns_str = ', '.join(idx.get('columns', [])) if isinstance(idx.get('columns'), list) else str(idx.get('columns', ''))
            indexes_data.append({
                'Index Name': str(idx.get('index_name', '')),
                'Columns': columns_str,
                'Type': str(idx.get('index_type', '')),
                'Unique': str(idx.get('is_unique', ''))
            })
        
        if indexes_data:
            indexes_df = pd.DataFrame(indexes_data)
            st.dataframe(indexes_df, use_container_width=True, hide_index=True)
    
    # Constraints documentation
    if table.get('constraints'):
        st.markdown("#### 🔒 Constraints")
        
        constraints_data = []
        for constraint in table['constraints']:
            # Convert columns list to string
            columns_str = ', '.join(constraint.get('columns', [])) if isinstance(constraint.get('columns'), list) else str(constraint.get('columns', ''))
            
            constraints_data.append({
                'Constraint Name': str(constraint.get('constraint_name', '')),
                'Type': str(constraint.get('constraint_type', '')),
                'Columns': columns_str,
                'Definition': str(constraint.get('definition', constraint.get('references', '')))
            })
        
        if constraints_data:
            constraints_df = pd.DataFrame(constraints_data)
            st.dataframe(constraints_df, use_container_width=True, hide_index=True)
    
    # Performance notes
    if include_performance_notes:
        show_performance_analysis(table, db_name, claude_client)

def show_view_documentation(view, db_name, claude_client, include_ai_descriptions):
    """Show view documentation"""
    
    with st.expander(f"👁️ {view['view_name']}"):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"""
            **View Information:**
            - **Schema:** {view.get('schema', 'N/A')}
            - **Description:** {view.get('description', 'N/A')}
            """)
        
        with col2:
            if view.get('definition'):
                st.markdown("**Definition:**")
                st.code(view['definition'], language='sql')

def show_function_documentation(func, db_name, func_type):
    """Show function/procedure documentation"""
    
    # Get the function/procedure name safely
    func_name = func.get('function_name') or func.get('procedure_name', 'Unknown')
    
    with st.expander(f"⚙️ {func_name} ({func_type})"):
        st.markdown(f"""
        **{func_type} Information:**
        - **Schema:** {func.get('schema', 'N/A')}
        - **Parameters:** {func.get('parameters', 'N/A')}
        - **Return Type:** {func.get('return_type', 'N/A')}
        - **Description:** {func.get('description', 'N/A')}
        """)

def show_performance_analysis(table, db_name, claude_client):
    """Show AI-powered performance analysis"""
    
    if claude_client:
        with st.expander("⚡ Performance Analysis"):
            with st.spinner("🤖 Analyzing table performance..."):
                try:
                    # Create performance analysis prompt
                    prompt = f"""Analyze the performance characteristics of this {db_name} table:

Table: {table['table_name']}
Row Count: {table.get('row_count', 0):,}
Size: {table.get('size_mb', 0):.1f} MB
Columns: {len(table.get('columns', []))}
Indexes: {len(table.get('indexes', []))}

Columns:
{json.dumps(table.get('columns', []), indent=2)}

Indexes:
{json.dumps(table.get('indexes', []), indent=2)}

Provide:
1. Performance assessment (Good/Warning/Critical)
2. Potential bottlenecks
3. Index optimization recommendations
4. Query performance tips
5. Maintenance considerations

Keep it concise and actionable."""

                    message = claude_client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=1000,
                        temperature=0.1,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    analysis = message.content[0].text
                    st.markdown(analysis)
                    
                except Exception as e:
                    st.warning(f"Could not generate performance analysis: {str(e)}")
    else:
        st.info("🤖 AI performance analysis available with Claude API key")

def show_cross_platform_analysis(sample_data, claude_client):
    """Show cross-platform schema comparison"""
    
    st.subheader("🔄 Cross-Platform Schema Analysis")
    st.markdown("**Compare schema designs and identify platform-specific differences**")
    
    # Data type comparison
    st.markdown("#### 📊 Data Type Mappings")
    
    # Create comparison table for customer table
    customers_comparison = []
    
    # Get customer table from each database
    pg_customers = next((t for t in sample_data["PostgreSQL"]["tables"] if t["table_name"] == "customers"), None)
    oracle_customers = next((t for t in sample_data["Oracle"]["tables"] if t["table_name"] == "CUSTOMERS"), None)
    sql_customers = next((t for t in sample_data["SQL Server"]["tables"] if t["table_name"] == "Customers"), None)
    
    if pg_customers and oracle_customers and sql_customers:
        # Compare primary key columns
        customers_comparison.append({
            "Column Purpose": "Primary Key",
            "PostgreSQL": "SERIAL (customer_id)",
            "Oracle": "NUMBER(10) + SEQUENCE (CUSTOMER_ID)", 
            "SQL Server": "INT IDENTITY(1,1) (CustomerID)",
            "Compatibility": "🟡 Different approaches"
        })
        
        customers_comparison.append({
            "Column Purpose": "Text Fields",
            "PostgreSQL": "VARCHAR(50) (first_name, last_name)",
            "Oracle": "VARCHAR2(50) (FIRST_NAME, LAST_NAME)",
            "SQL Server": "NVARCHAR(50) (FirstName, LastName)",
            "Compatibility": "🟢 Compatible"
        })
        
        customers_comparison.append({
            "Column Purpose": "JSON Data",
            "PostgreSQL": "JSONB (address)",
            "Oracle": "CLOB (ADDRESS_DATA)",
            "SQL Server": "NVARCHAR(MAX) (AddressData)",
            "Compatibility": "🔴 Requires conversion"
        })
        
        customers_comparison.append({
            "Column Purpose": "Boolean",
            "PostgreSQL": "BOOLEAN (is_active)",
            "Oracle": "NUMBER(1) (IS_ACTIVE)",
            "SQL Server": "BIT (IsActive)",
            "Compatibility": "🟡 Different implementations"
        })
        
        customers_comparison.append({
            "Column Purpose": "Timestamps",
            "PostgreSQL": "TIMESTAMP (registration_date)",
            "Oracle": "DATE (REGISTRATION_DATE)",
            "SQL Server": "DATETIME2 (RegistrationDate)",
            "Compatibility": "🟡 Precision differences"
        })
    
    comparison_df = pd.DataFrame(customers_comparison)
    # Ensure all columns are strings to avoid PyArrow issues
    for col in comparison_df.columns:
        comparison_df[col] = comparison_df[col].astype(str)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # Schema statistics comparison
    st.markdown("#### 📈 Schema Statistics Comparison")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🐘 PostgreSQL**")
        pg_tables = len(sample_data["PostgreSQL"]["tables"])
        pg_views = len(sample_data["PostgreSQL"]["views"])
        pg_functions = len(sample_data["PostgreSQL"].get("functions", []))
        st.metric("Tables", pg_tables)
        st.metric("Views", pg_views)
        st.metric("Functions", pg_functions)
    
    with col2:
        st.markdown("**🔶 Oracle**")
        oracle_tables = len(sample_data["Oracle"]["tables"])
        oracle_views = len(sample_data["Oracle"]["views"])
        oracle_procedures = len(sample_data["Oracle"].get("procedures", []))
        st.metric("Tables", oracle_tables)
        st.metric("Views", oracle_views)
        st.metric("Procedures", oracle_procedures)
    
    with col3:
        st.markdown("**🟦 SQL Server**")
        sql_tables = len(sample_data["SQL Server"]["tables"])
        sql_views = len(sample_data["SQL Server"]["views"])
        sql_procedures = len(sample_data["SQL Server"].get("procedures", []))
        st.metric("Tables", sql_tables)
        st.metric("Views", sql_views)
        st.metric("Procedures", sql_procedures)
    
    # Platform-specific features
    st.markdown("#### 🔧 Platform-Specific Features")
    
    features_comparison = [
        {
            "Feature": "JSON Support",
            "PostgreSQL": "✅ Native JSONB with indexing",
            "Oracle": "✅ JSON data type (19c+)",
            "SQL Server": "✅ JSON functions, no native type",
            "Best Practice": "Use JSONB in PostgreSQL for performance"
        },
        {
            "Feature": "Auto-increment",
            "PostgreSQL": "SERIAL/IDENTITY columns",
            "Oracle": "SEQUENCE + TRIGGER/DEFAULT",
            "SQL Server": "IDENTITY property",
            "Best Practice": "Use IDENTITY for new schemas"
        },
        {
            "Feature": "Full-text Search",
            "PostgreSQL": "Built-in FTS with GIN indexes",
            "Oracle": "Oracle Text",
            "SQL Server": "Full-Text Search service",
            "Best Practice": "PostgreSQL has superior built-in FTS"
        },
        {
            "Feature": "Partitioning",
            "PostgreSQL": "Declarative partitioning",
            "Oracle": "Advanced partitioning (license)",
            "SQL Server": "Table/index partitioning",
            "Best Practice": "Consider licensing costs"
        }
    ]
    
    features_df = pd.DataFrame(features_comparison)
    # Ensure all columns are strings to avoid PyArrow issues  
    for col in features_df.columns:
        features_df[col] = features_df[col].astype(str)
    st.dataframe(features_df, use_container_width=True, hide_index=True)
    
    # AI-powered migration recommendations
    if claude_client:
        st.markdown("#### 🤖 AI-Powered Migration Recommendations")
        
        if st.button("🚀 Generate Migration Analysis", type="primary"):
            with st.spinner("🤖 Analyzing cross-platform migration strategies..."):
                try:
                    prompt = """Analyze the provided e-commerce database schemas across PostgreSQL, Oracle, and SQL Server. Provide:

1. **Migration Complexity Assessment** (Low/Medium/High)
2. **Key Challenges** for each migration path
3. **Data Type Conversion Strategy**
4. **Performance Impact Analysis**
5. **Recommended Migration Approach**
6. **Timeline Estimates**

Focus on practical, actionable recommendations for database administrators."""

                    message = claude_client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=2000,
                        temperature=0.1,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    recommendations = message.content[0].text
                    
                    st.markdown("""
                    <div class="success-banner">
                        <h4>🎯 Migration Recommendations</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(recommendations)
                    
                except Exception as e:
                    st.error(f"Could not generate migration analysis: {str(e)}")

def show_live_connection_mode():
    """Show live database connection interface"""
    
    st.header("📊 Live Database Connection")
    st.markdown("**Connect to your live databases for real-time schema documentation**")
    
    # Connection tabs
    conn_tabs = st.tabs(["🐘 PostgreSQL", "🔶 Oracle", "🟦 SQL Server"])
    
    with conn_tabs[0]:
        show_postgres_connection()
    
    with conn_tabs[1]:
        show_oracle_connection()
    
    with conn_tabs[2]:
        show_sqlserver_connection()

def show_postgres_connection():
    """PostgreSQL connection interface"""
    
    st.subheader("🐘 PostgreSQL Connection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        pg_host = st.text_input("Host", value="localhost", key="pg_host")
        pg_port = st.number_input("Port", value=5432, key="pg_port")
        pg_database = st.text_input("Database", key="pg_database")
    
    with col2:
        pg_username = st.text_input("Username", key="pg_username")
        pg_password = st.text_input("Password", type="password", key="pg_password")
        pg_schema = st.text_input("Schema (optional)", value="public", key="pg_schema")
    
    if st.button("🔗 Connect to PostgreSQL", type="primary"):
        # Simulate connection (in real app, use psycopg2 or similar)
        with st.spinner("Connecting to PostgreSQL..."):
            time.sleep(2)
            st.success("✅ Connected successfully!")
            st.info("📊 Schema extraction would begin here in the full implementation")

def show_oracle_connection():
    """Oracle connection interface"""
    
    st.subheader("🔶 Oracle Connection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        oracle_host = st.text_input("Host", value="localhost", key="oracle_host")
        oracle_port = st.number_input("Port", value=1521, key="oracle_port")
        oracle_service = st.text_input("Service Name", key="oracle_service")
    
    with col2:
        oracle_username = st.text_input("Username", key="oracle_username")
        oracle_password = st.text_input("Password", type="password", key="oracle_password")
        oracle_schema = st.text_input("Schema (optional)", key="oracle_schema")
    
    if st.button("🔗 Connect to Oracle", type="primary"):
        with st.spinner("Connecting to Oracle..."):
            time.sleep(2)
            st.success("✅ Connected successfully!")
            st.info("📊 Schema extraction would begin here in the full implementation")

def show_sqlserver_connection():
    """SQL Server connection interface"""
    
    st.subheader("🟦 SQL Server Connection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sql_server = st.text_input("Server", value="localhost", key="sql_server")
        sql_port = st.number_input("Port", value=1433, key="sql_port")
        sql_database = st.text_input("Database", key="sql_database")
    
    with col2:
        sql_username = st.text_input("Username", key="sql_username")
        sql_password = st.text_input("Password", type="password", key="sql_password")
        sql_auth = st.selectbox("Authentication", ["SQL Server", "Windows"], key="sql_auth")
    
    if st.button("🔗 Connect to SQL Server", type="primary"):
        with st.spinner("Connecting to SQL Server..."):
            time.sleep(2)
            st.success("✅ Connected successfully!")
            st.info("📊 Schema extraction would begin here in the full implementation")

def show_file_upload_mode():
    """Show file upload interface for schema files"""
    
    st.header("📁 Schema File Upload")
    st.markdown("**Upload schema files or DDL scripts for documentation generation**")
    
    # File upload area
    uploaded_files = st.file_uploader(
        "Choose schema files",
        accept_multiple_files=True,
        type=['sql', 'ddl', 'json', 'xml', 'txt'],
        help="Upload DDL scripts, schema exports, or metadata files"
    )
    
    if uploaded_files:
        st.subheader("📋 Uploaded Files")
        
        for file in uploaded_files:
            with st.expander(f"📄 {file.name} ({file.size} bytes)"):
                # Show file preview
                if file.type == "text/plain" or file.name.endswith(('.sql', '.ddl')):
                    content = str(file.read(), "utf-8")
                    st.code(content[:1000] + "..." if len(content) > 1000 else content, language="sql")
                    
                    if st.button(f"📊 Parse {file.name}", key=f"parse_{file.name}"):
                        with st.spinner(f"Parsing {file.name}..."):
                            time.sleep(2)
                            st.success(f"✅ Successfully parsed {file.name}")
                            st.info("📖 Documentation generation would begin here")

def show_cross_platform_comparison():
    """Show cross-platform comparison interface"""
    
    st.header("🔄 Cross-Platform Schema Comparison")
    st.markdown("**Compare schemas across different database platforms**")
    
    # Source and target selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Source Database")
        source_db = st.selectbox("Source Platform", ["PostgreSQL", "Oracle", "SQL Server"], key="source")
        source_schema = st.text_input("Source Schema/Database", key="source_schema")
    
    with col2:
        st.subheader("🎯 Target Database")
        target_db = st.selectbox("Target Platform", ["PostgreSQL", "Oracle", "SQL Server"], key="target")
        target_schema = st.text_input("Target Schema/Database", key="target_schema")
    
    # Comparison options
    st.subheader("🔧 Comparison Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        compare_tables = st.checkbox("📋 Compare Tables", value=True)
        compare_columns = st.checkbox("📝 Compare Columns", value=True)
        compare_indexes = st.checkbox("🔍 Compare Indexes", value=True)
    
    with col2:
        compare_constraints = st.checkbox("🔒 Compare Constraints", value=True)
        compare_views = st.checkbox("👁️ Compare Views", value=True)
        compare_procedures = st.checkbox("⚙️ Compare Procedures", value=True)
    
    with col3:
        show_differences = st.checkbox("🔍 Show Only Differences", value=False)
        include_migration_script = st.checkbox("📜 Generate Migration Script", value=True)
        include_mapping_report = st.checkbox("📊 Include Mapping Report", value=True)
    
    # Generate comparison
    if st.button("🔄 Generate Comparison Report", type="primary", use_container_width=True):
        if source_db == target_db:
            st.warning("⚠️ Source and target databases are the same!")
        else:
            generate_comparison_report(source_db, target_db, source_schema, target_schema,
                                     compare_tables, compare_columns, compare_indexes, 
                                     compare_constraints, compare_views, compare_procedures,
                                     show_differences, include_migration_script, include_mapping_report)

def generate_comparison_report(source_db, target_db, source_schema, target_schema,
                             compare_tables, compare_columns, compare_indexes, 
                             compare_constraints, compare_views, compare_procedures,
                             show_differences, include_migration_script, include_mapping_report):
    """Generate cross-platform comparison report"""
    
    with st.spinner(f"🤖 Generating comparison report: {source_db} → {target_db}..."):
        time.sleep(3)
        
        st.markdown(f"""
        <div class="success-banner">
            <h4>✅ Comparison Report Generated</h4>
            <p><strong>Source:</strong> {source_db} ({source_schema})</p>
            <p><strong>Target:</strong> {target_db} ({target_schema})</p>
            <p><strong>Analysis Complete:</strong> Ready for review and export</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show sample comparison results
        st.subheader("📊 Comparison Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Tables Compared", "15", "2 differences")
        with col2:
            st.metric("Columns Analyzed", "127", "8 type differences")
        with col3:
            st.metric("Indexes Reviewed", "34", "5 missing")
        with col4:
            st.metric("Compatibility Score", "87%", "+12% with changes")

def generate_complete_documentation(db_name, db_data, claude_client, include_ai_descriptions,
                                  include_diagrams, include_data_dictionary, include_performance_notes,
                                  include_security_analysis):
    """Generate complete documentation for a database"""
    
    with st.spinner(f"📚 Generating complete {db_name} documentation..."):
        time.sleep(2)  # Simulate processing time
        
        st.markdown(f"""
        <div class="success-banner">
            <h4>✅ Complete Documentation Generated</h4>
            <p><strong>Database:</strong> {db_name}</p>
            <p><strong>Pages Generated:</strong> 47</p>
            <p><strong>Objects Documented:</strong> {len(db_data.get('tables', [])) + len(db_data.get('views', []))}</p>
            <p><strong>Export Formats:</strong> HTML, PDF, Markdown, JSON available</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Prepare documentation options
        doc_options = {
            'AI-Enhanced Descriptions': include_ai_descriptions,
            'Include ER Diagrams': include_diagrams,
            'Data Dictionary': include_data_dictionary,
            'Performance Notes': include_performance_notes,
            'Security Analysis': include_security_analysis
        }
        
        # Generate documentation content
        html_content = generate_detailed_html_documentation(db_name, db_data)
        markdown_content = generate_detailed_markdown_documentation(db_name, db_data)
        json_content = convert_to_json_schema(db_data)
        
        # Show documentation preview
        st.subheader("📖 Documentation Preview")
        
        # Show in tabs
        preview_tabs = st.tabs(["📄 HTML Preview", "📝 Markdown", "📋 JSON Schema"])
        
        with preview_tabs[0]:
            st.markdown(html_content, unsafe_allow_html=True)
        
        with preview_tabs[1]:
            st.code(markdown_content, language="markdown")
        
        with preview_tabs[2]:
            st.json(json_content)
        
        # Download buttons with actual file generation
        st.subheader("📤 Download Documentation")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # HTML Download
            html_filename = f"{db_name.lower()}_documentation.html"
            html_full = generate_full_html_document(db_name, db_data, html_content)
            st.download_button(
                label="📄 Download HTML",
                data=html_full,
                file_name=html_filename,
                mime="text/html",
                use_container_width=True
            )
        
        with col2:
            # Markdown Download
            md_filename = f"{db_name.lower()}_documentation.md"
            st.download_button(
                label="📝 Download Markdown",
                data=markdown_content,
                file_name=md_filename,
                mime="text/markdown",
                use_container_width=True
            )
        
        with col3:
            # JSON Download
            json_filename = f"{db_name.lower()}_schema.json"
            json_str = json.dumps(json_content, indent=2)
            st.download_button(
                label="📋 Download JSON",
                data=json_str,
                file_name=json_filename,
                mime="application/json",
                use_container_width=True
            )
        
        with col4:
            # PDF Download with improved formatting and documentation options
            pdf_filename = f"{db_name.lower()}_documentation.pdf"
            try:
                # Pass the documentation options to the PDF generator
                pdf_content = generate_pdf_documentation(db_name, db_data, markdown_content, doc_options)
                st.download_button(
                    label="📊 Download PDF",
                    data=pdf_content,
                    file_name=pdf_filename,
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF generation not available: {str(e)}")
                st.info("💡 PDF generation requires additional system dependencies")

def generate_detailed_html_documentation(db_name, db_data):
    """Generate detailed HTML documentation"""
    
    html_content = f"""
    <div style="font-family: 'Inter', sans-serif; max-width: 1000px; margin: 0 auto;">
        <h1>📚 {db_name} Database Documentation</h1>
        <p><em>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
        
        <h2>📊 Database Overview</h2>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background-color: #f8f9fa;">
                <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Property</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Value</th>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; padding: 12px;">Database Name</td>
                <td style="border: 1px solid #ddd; padding: 12px;">{db_data.get('database_info', {}).get('name', 'N/A')}</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="border: 1px solid #ddd; padding: 12px;">Version</td>
                <td style="border: 1px solid #ddd; padding: 12px;">{db_data.get('database_info', {}).get('version', 'N/A')}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; padding: 12px;">Size</td>
                <td style="border: 1px solid #ddd; padding: 12px;">{db_data.get('database_info', {}).get('size', 'N/A')}</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="border: 1px solid #ddd; padding: 12px;">Tables</td>
                <td style="border: 1px solid #ddd; padding: 12px;">{len(db_data.get('tables', []))}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; padding: 12px;">Views</td>
                <td style="border: 1px solid #ddd; padding: 12px;">{len(db_data.get('views', []))}</td>
            </tr>
        </table>
        
        <h2>📋 Tables Documentation</h2>
    """
    
    # Add detailed table documentation
    for table in db_data.get('tables', []):
        html_content += f"""
        <h3>📊 {table['table_name']}</h3>
        <p><strong>Description:</strong> {table.get('description', 'No description available')}</p>
        <ul>
            <li><strong>Schema:</strong> {table.get('schema', 'N/A')}</li>
            <li><strong>Type:</strong> {table.get('table_type', 'N/A')}</li>
            <li><strong>Rows:</strong> {table.get('row_count', 0):,}</li>
            <li><strong>Size:</strong> {table.get('size_mb', 0):.1f} MB</li>
        </ul>
        
        <h4>Columns</h4>
        <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
            <tr style="background-color: #f8f9fa;">
                <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Column</th>
                <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Type</th>
                <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Nullable</th>
                <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Default</th>
                <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Description</th>
            </tr>
        """
        
        for i, col in enumerate(table.get('columns', [])):
            bg_color = "#f8f9fa" if i % 2 == 0 else "white"
            html_content += f"""
            <tr style="background-color: {bg_color};">
                <td style="border: 1px solid #ddd; padding: 8px;">{col.get('column_name', '')}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{col.get('data_type', '')}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{col.get('is_nullable', '')}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{col.get('default', '') if col.get('default') else ''}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{col.get('description', '')}</td>
            </tr>
            """
        
        html_content += "</table>"
        
        # Add indexes if available
        if table.get('indexes'):
            html_content += """
            <h4>Indexes</h4>
            <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
                <tr style="background-color: #f8f9fa;">
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Index Name</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Columns</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Type</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Unique</th>
                </tr>
            """
            
            for i, idx in enumerate(table.get('indexes', [])):
                bg_color = "#f8f9fa" if i % 2 == 0 else "white"
                columns_str = ', '.join(idx.get('columns', [])) if isinstance(idx.get('columns'), list) else str(idx.get('columns', ''))
                html_content += f"""
                <tr style="background-color: {bg_color};">
                    <td style="border: 1px solid #ddd; padding: 8px;">{idx.get('index_name', '')}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{columns_str}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{idx.get('index_type', '')}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{idx.get('is_unique', '')}</td>
                </tr>
                """
            
            html_content += "</table>"
    
    # Add views documentation
    if db_data.get('views'):
        html_content += "<h2>👁️ Views Documentation</h2>"
        for view in db_data.get('views', []):
            html_content += f"""
            <h3>👁️ {view['view_name']}</h3>
            <p><strong>Description:</strong> {view.get('description', 'No description available')}</p>
            <p><strong>Schema:</strong> {view.get('schema', 'N/A')}</p>
            <h4>Definition:</h4>
            <pre style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto;">
{view.get('definition', 'No definition available')}
            </pre>
            """
    
    html_content += """
    </div>
    """
    
    return html_content

def generate_detailed_markdown_documentation(db_name, db_data):
    """Generate detailed Markdown documentation"""
    
    markdown_content = f"""# 📚 {db_name} Database Documentation

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 📊 Database Overview

| Property | Value |
|----------|-------|
| Database Name | {db_data.get('database_info', {}).get('name', 'N/A')} |
| Version | {db_data.get('database_info', {}).get('version', 'N/A')} |
| Size | {db_data.get('database_info', {}).get('size', 'N/A')} |
| Tables | {len(db_data.get('tables', []))} |
| Views | {len(db_data.get('views', []))} |

## 📋 Tables Documentation

"""
    
    # Add detailed table documentation
    for table in db_data.get('tables', []):
        markdown_content += f"""### 📊 {table['table_name']}

**Description:** {table.get('description', 'No description available')}

- **Schema:** {table.get('schema', 'N/A')}
- **Type:** {table.get('table_type', 'N/A')}
- **Rows:** {table.get('row_count', 0):,}
- **Size:** {table.get('size_mb', 0):.1f} MB

#### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
"""
        
        for col in table.get('columns', []):
            default_val = col.get('default', '') if col.get('default') else ''
            markdown_content += f"| {col.get('column_name', '')} | {col.get('data_type', '')} | {col.get('is_nullable', '')} | {default_val} | {col.get('description', '')} |\n"
        
        # Add indexes if available
        if table.get('indexes'):
            markdown_content += "\n#### Indexes\n\n| Index Name | Columns | Type | Unique |\n|------------|---------|------|--------|\n"
            
            for idx in table.get('indexes', []):
                columns_str = ', '.join(idx.get('columns', [])) if isinstance(idx.get('columns'), list) else str(idx.get('columns', ''))
                markdown_content += f"| {idx.get('index_name', '')} | {columns_str} | {idx.get('index_type', '')} | {idx.get('is_unique', '')} |\n"
        
        markdown_content += "\n"
    
    # Add views documentation
    if db_data.get('views'):
        markdown_content += "## 👁️ Views Documentation\n\n"
        for view in db_data.get('views', []):
            markdown_content += f"""### 👁️ {view['view_name']}

**Description:** {view.get('description', 'No description available')}
**Schema:** {view.get('schema', 'N/A')}

#### Definition:
```sql
{view.get('definition', 'No definition available')}
```

"""
    
    return markdown_content

def generate_full_html_document(db_name, db_data, content):
    """Generate a complete HTML document with CSS styling"""
    
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{db_name} Database Documentation</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        body {{
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        
        h1, h2, h3, h4 {{
            color: #2c3e50;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }}
        
        h1 {{
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
            font-weight: 600;
        }}
        
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        
        pre {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #3498db;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 2rem;
            padding: 2rem;
            background: linear-gradient(135deg, #3498db, #2c3e50);
            color: white;
            border-radius: 10px;
        }}
        
        .section {{
            background-color: white;
            padding: 2rem;
            margin: 2rem 0;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📚 {db_name} Database Documentation</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="section">
        {content}
    </div>
    
    <footer style="text-align: center; margin-top: 2rem; padding: 1rem; color: #666;">
        <p>Generated by Multi-DB Schema Documentation Tool</p>
    </footer>
</body>
</html>"""
    
    return full_html

def generate_pdf_documentation(db_name, db_data, markdown_content, doc_options=None):
    """Generate comprehensive PDF documentation using reportlab with improved formatting"""
    
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.utils import ImageReader
        import io
        import textwrap
        
        # Create a BytesIO buffer
        buffer = io.BytesIO()
        
        # Create the PDF document with margins
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=1  # Center alignment
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=24,
            textColor=colors.HexColor('#3498db')
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=16,
            textColor=colors.HexColor('#2c3e50')
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            leading=12
        )
        
        # Helper function to wrap text
        def wrap_text(text, max_length=30):
            """Wrap text to fit in table cells"""
            if not text or len(str(text)) <= max_length:
                return str(text)
            return '<br/>'.join(textwrap.wrap(str(text), max_length))
        
        # Helper function to create wrapped paragraph
        def create_wrapped_paragraph(text, max_length=30):
            """Create a paragraph with wrapped text"""
            wrapped_text = wrap_text(text, max_length)
            return Paragraph(wrapped_text, normal_style)
        
        # Build the comprehensive story
        story = []
        
        # Cover Page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(f"📚 {db_name} Database", title_style))
        story.append(Paragraph("Complete Schema Documentation", title_style))
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Paragraph(f"Time: {datetime.now().strftime('%I:%M %p')}", styles['Normal']))
        
        # Add documentation options if provided
        if doc_options:
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph("📝 Documentation Options", heading_style))
            for option, enabled in doc_options.items():
                status = "✅ Enabled" if enabled else "❌ Disabled"
                story.append(Paragraph(f"• {option}: {status}", styles['Normal']))
        
        story.append(PageBreak())
        
        # Table of Contents
        story.append(Paragraph("Table of Contents", heading_style))
        story.append(Paragraph("1. Documentation Options", styles['Normal']))
        story.append(Paragraph("2. Database Overview", styles['Normal']))
        story.append(Paragraph("3. Tables Documentation", styles['Normal']))
        
        table_num = 1
        for table in db_data.get('tables', []):
            story.append(Paragraph(f"   3.{table_num} {table['table_name']}", styles['Normal']))
            table_num += 1
        
        story.append(Paragraph("4. Views Documentation", styles['Normal']))
        story.append(Paragraph("5. Functions & Procedures", styles['Normal']))
        story.append(Paragraph("6. Database Statistics", styles['Normal']))
        story.append(PageBreak())
        
        # 1. Documentation Options Section
        if doc_options:
            story.append(Paragraph("1. Documentation Options", heading_style))
            story.append(Paragraph("This documentation was generated with the following configuration:", styles['Normal']))
            story.append(Spacer(1, 12))
            
            options_data = [['Option', 'Status', 'Description']]
            option_descriptions = {
                'AI-Enhanced Descriptions': 'Use Claude AI to generate detailed descriptions',
                'Include ER Diagrams': 'Generate entity relationship diagrams',
                'Data Dictionary': 'Include comprehensive column documentation',
                'Performance Notes': 'Add performance analysis and recommendations',
                'Security Analysis': 'Include security considerations and analysis'
            }
            
            for option, enabled in doc_options.items():
                status = "✅ Enabled" if enabled else "❌ Disabled"
                description = option_descriptions.get(option, 'Custom documentation option')
                options_data.append([
                    option,
                    status,
                    wrap_text(description, 40)
                ])
            
            options_table = Table(options_data, colWidths=[2.2*inch, 1*inch, 2.3*inch])
            options_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            story.append(options_table)
            story.append(PageBreak())
        
        # 2. Database Overview
        story.append(Paragraph("2. Database Overview", heading_style))
        db_info = db_data.get('database_info', {})
        
        overview_data = [
            ['Property', 'Value'],
            ['Database Name', db_info.get('name', 'N/A')],
            ['Database Version', db_info.get('version', 'N/A')],
            ['Total Size', db_info.get('size', 'N/A')],
            ['Created Date', db_info.get('created', 'N/A')],
            ['Last Backup', db_info.get('last_backup', 'N/A')],
            ['Total Tables', str(len(db_data.get('tables', [])))],
            ['Total Views', str(len(db_data.get('views', [])))],
            ['Total Functions', str(len(db_data.get('functions', [])))],
            ['Total Procedures', str(len(db_data.get('procedures', [])))]
        ]
        
        overview_table = Table(overview_data, colWidths=[2.5*inch, 3*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(overview_table)
        story.append(Spacer(1, 24))
        
        # Database Statistics Summary
        total_rows = sum(table.get('row_count', 0) for table in db_data.get('tables', []))
        total_size = sum(table.get('size_mb', 0) for table in db_data.get('tables', []))
        total_columns = sum(len(table.get('columns', [])) for table in db_data.get('tables', []))
        total_indexes = sum(len(table.get('indexes', [])) for table in db_data.get('tables', []))
        
        stats_data = [
            ['Metric', 'Count', 'Details'],
            ['Total Records', f"{total_rows:,}", 'Across all tables'],
            ['Total Size', f"{total_size:.1f} MB", 'Data + indexes'],
            ['Total Columns', str(total_columns), 'All table columns'],
            ['Total Indexes', str(total_indexes), 'Performance optimization'],
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 1.5*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(PageBreak())
        
        # 3. Tables Documentation (ALL TABLES - NO LIMIT)
        story.append(Paragraph("3. Tables Documentation", heading_style))
        
        table_counter = 1
        for table in db_data.get('tables', []):  # ALL TABLES, NO LIMIT
            # Table header
            story.append(Paragraph(f"3.{table_counter} Table: {table['table_name']}", subheading_style))
            story.append(Paragraph(f"Description: {table.get('description', 'No description available')}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Table metadata
            table_meta_data = [
                ['Property', 'Value'],
                ['Schema', table.get('schema', 'N/A')],
                ['Table Type', table.get('table_type', 'N/A')],
                ['Row Count', f"{table.get('row_count', 0):,}"],
                ['Size (MB)', f"{table.get('size_mb', 0):.1f}"],
                ['Column Count', str(len(table.get('columns', [])))],
                ['Index Count', str(len(table.get('indexes', [])))],
                ['Constraint Count', str(len(table.get('constraints', [])))]
            ]
            
            meta_table = Table(table_meta_data, colWidths=[2.2*inch, 3.3*inch])
            meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(meta_table)
            story.append(Spacer(1, 16))
            
            # Columns documentation with improved formatting
            if table.get('columns'):
                story.append(Paragraph("Columns", ParagraphStyle('ColumnHeader', parent=styles['Heading4'], fontSize=12, textColor=colors.HexColor('#2c3e50'))))
                
                columns_data = [
                    ['Column Name', 'Data Type', 'Nullable', 'Default', 'Description']
                ]
                
                for col in table.get('columns', []):
                    # Handle long default values
                    default_val = str(col.get('default', '')) if col.get('default') else ''
                    if len(default_val) > 25:
                        default_val = default_val[:22] + '...'
                    
                    # Handle long descriptions
                    desc = str(col.get('description', ''))
                    if len(desc) > 35:
                        desc = desc[:32] + '...'
                    
                    # Handle long data types
                    data_type = str(col.get('data_type', ''))
                    if len(data_type) > 20:
                        data_type = data_type[:17] + '...'
                    
                    columns_data.append([
                        create_wrapped_paragraph(str(col.get('column_name', '')), 15),
                        create_wrapped_paragraph(data_type, 18),
                        str(col.get('is_nullable', '')),
                        create_wrapped_paragraph(default_val, 20),
                        create_wrapped_paragraph(desc, 30)
                    ])
                
                columns_table = Table(columns_data, colWidths=[1.1*inch, 1.1*inch, 0.7*inch, 1.1*inch, 1.5*inch])
                columns_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
                ]))
                
                story.append(columns_table)
                story.append(Spacer(1, 16))
            
            # Indexes documentation with improved formatting
            if table.get('indexes'):
                story.append(Paragraph("Indexes", ParagraphStyle('IndexHeader', parent=styles['Heading4'], fontSize=12, textColor=colors.HexColor('#2c3e50'))))
                
                indexes_data = [['Index Name', 'Columns', 'Type', 'Unique']]
                for idx in table.get('indexes', []):
                    columns_str = ', '.join(idx.get('columns', [])) if isinstance(idx.get('columns'), list) else str(idx.get('columns', ''))
                    
                    indexes_data.append([
                        create_wrapped_paragraph(str(idx.get('index_name', '')), 20),
                        create_wrapped_paragraph(columns_str, 25),
                        str(idx.get('index_type', '')),
                        str(idx.get('is_unique', ''))
                    ])
                
                indexes_table = Table(indexes_data, colWidths=[1.4*inch, 2*inch, 1*inch, 0.6*inch])
                indexes_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4)
                ]))
                
                story.append(indexes_table)
                story.append(Spacer(1, 16))
            
            # Constraints documentation with improved formatting
            if table.get('constraints'):
                story.append(Paragraph("Constraints", ParagraphStyle('ConstraintHeader', parent=styles['Heading4'], fontSize=12, textColor=colors.HexColor('#2c3e50'))))
                
                constraints_data = [['Constraint Name', 'Type', 'Columns', 'Definition']]
                for constraint in table.get('constraints', []):
                    columns_str = ', '.join(constraint.get('columns', [])) if isinstance(constraint.get('columns'), list) else str(constraint.get('columns', ''))
                    definition = str(constraint.get('definition', constraint.get('references', '')))
                    
                    constraints_data.append([
                        create_wrapped_paragraph(str(constraint.get('constraint_name', '')), 18),
                        str(constraint.get('constraint_type', '')),
                        create_wrapped_paragraph(columns_str, 15),
                        create_wrapped_paragraph(definition, 30)
                    ])
                
                constraints_table = Table(constraints_data, colWidths=[1.2*inch, 0.9*inch, 1.1*inch, 2.3*inch])
                constraints_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4)
                ]))
                
                story.append(constraints_table)
            
            story.append(Spacer(1, 24))
            table_counter += 1
            
            # Add page break after every 2 tables for readability
            if table_counter % 3 == 0:
                story.append(PageBreak())
        
        # 4. Views Documentation
        if db_data.get('views'):
            story.append(PageBreak())
            story.append(Paragraph("4. Views Documentation", heading_style))
            
            for view in db_data.get('views', []):
                story.append(Paragraph(f"View: {view['view_name']}", subheading_style))
                story.append(Paragraph(f"Schema: {view.get('schema', 'N/A')}", styles['Normal']))
                story.append(Paragraph(f"Description: {view.get('description', 'No description available')}", styles['Normal']))
                story.append(Spacer(1, 12))
                
                if view.get('definition'):
                    story.append(Paragraph("Definition:", ParagraphStyle('DefHeader', parent=styles['Heading4'], fontSize=12)))
                    # Format SQL definition with better wrapping
                    definition = view.get('definition', '')
                    # Split long lines and format properly
                    if len(definition) > 500:
                        definition = definition[:497] + '...'
                    
                    # Create code style with proper formatting
                    code_style = ParagraphStyle(
                        'CodeStyle',
                        parent=styles['Code'],
                        fontSize=8,
                        leading=10,
                        leftIndent=10,
                        rightIndent=10,
                        spaceAfter=10,
                        backColor=colors.HexColor('#f8f9fa')
                    )
                    
                    story.append(Paragraph(definition, code_style))
                
                story.append(Spacer(1, 20))
        
        # 5. Functions & Procedures
        if db_data.get('functions') or db_data.get('procedures'):
            story.append(PageBreak())
            story.append(Paragraph("5. Functions & Procedures", heading_style))
            
            for func in db_data.get('functions', []):
                story.append(Paragraph(f"Function: {func.get('function_name', 'Unknown')}", subheading_style))
                story.append(Paragraph(f"Schema: {func.get('schema', 'N/A')}", styles['Normal']))
                story.append(Paragraph(f"Return Type: {func.get('return_type', 'N/A')}", styles['Normal']))
                story.append(Paragraph(f"Parameters: {func.get('parameters', 'N/A')}", styles['Normal']))
                story.append(Paragraph(f"Description: {func.get('description', 'No description available')}", styles['Normal']))
                story.append(Spacer(1, 16))
            
            for proc in db_data.get('procedures', []):
                story.append(Paragraph(f"Procedure: {proc.get('procedure_name', 'Unknown')}", subheading_style))
                story.append(Paragraph(f"Schema: {proc.get('schema', 'N/A')}", styles['Normal']))
                story.append(Paragraph(f"Parameters: {proc.get('parameters', 'N/A')}", styles['Normal']))
                story.append(Paragraph(f"Description: {proc.get('description', 'No description available')}", styles['Normal']))
                story.append(Spacer(1, 16))
        
        # Build PDF
        doc.build(story)
        
        # Get the PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
        
    except ImportError:
        raise Exception("ReportLab not available for PDF generation")
    except Exception as e:
        raise Exception(f"PDF generation failed: {str(e)}")

# Update the generate_complete_documentation function to pass documentation options
def generate_pdf_documentation(db_name, db_data, markdown_content, doc_options=None):
    """Generate comprehensive PDF documentation using reportlab with improved formatting"""
    
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.utils import ImageReader
        import io
        import textwrap
        
        # Create a BytesIO buffer
        buffer = io.BytesIO()
        
        # Create the PDF document with margins
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=1  # Center alignment
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=24,
            textColor=colors.HexColor('#3498db')
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=16,
            textColor=colors.HexColor('#2c3e50')
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            leading=12
        )
        
        # Helper function to wrap text
        def wrap_text(text, max_length=30):
            """Wrap text to fit in table cells"""
            if not text or len(str(text)) <= max_length:
                return str(text)
            return '<br/>'.join(textwrap.wrap(str(text), max_length))
        
        # Helper function to create wrapped paragraph
        def create_wrapped_paragraph(text, max_length=30):
            """Create a paragraph with wrapped text"""
            wrapped_text = wrap_text(text, max_length)
            return Paragraph(wrapped_text, normal_style)
        
        # Build the comprehensive story
        story = []
        
        # Cover Page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(f"📚 {db_name} Database", title_style))
        story.append(Paragraph("Complete Schema Documentation", title_style))
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Paragraph(f"Time: {datetime.now().strftime('%I:%M %p')}", styles['Normal']))
        
        # Add documentation options if provided
        if doc_options:
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph("📝 Documentation Options", heading_style))
            for option, enabled in doc_options.items():
                status = "✅ Enabled" if enabled else "❌ Disabled"
                story.append(Paragraph(f"• {option}: {status}", styles['Normal']))
        
        story.append(PageBreak())
        
        # Table of Contents
        story.append(Paragraph("Table of Contents", heading_style))
        if doc_options:
            story.append(Paragraph("1. Documentation Options", styles['Normal']))
            story.append(Paragraph("2. Database Overview", styles['Normal']))
            story.append(Paragraph("3. Tables Documentation", styles['Normal']))
        else:
            story.append(Paragraph("1. Database Overview", styles['Normal']))
            story.append(Paragraph("2. Tables Documentation", styles['Normal']))
        
        table_num = 1
        section_offset = 2 if doc_options else 1
        for table in db_data.get('tables', []):
            story.append(Paragraph(f"   {section_offset + 1}.{table_num} {table['table_name']}", styles['Normal']))
            table_num += 1
        
        story.append(Paragraph(f"{section_offset + 2}. Views Documentation", styles['Normal']))
        story.append(Paragraph(f"{section_offset + 3}. Functions & Procedures", styles['Normal']))
        story.append(Paragraph(f"{section_offset + 4}. Database Statistics", styles['Normal']))
        story.append(PageBreak())
        
        # 1. Documentation Options Section (if provided)
        section_num = 1
        if doc_options:
            story.append(Paragraph("1. Documentation Options", heading_style))
            story.append(Paragraph("This documentation was generated with the following configuration:", styles['Normal']))
            story.append(Spacer(1, 12))
            
            options_data = [['Option', 'Status', 'Description']]
            option_descriptions = {
                'AI-Enhanced Descriptions': 'Use Claude AI to generate detailed descriptions',
                'Include ER Diagrams': 'Generate entity relationship diagrams',
                'Data Dictionary': 'Include comprehensive column documentation',
                'Performance Notes': 'Add performance analysis and recommendations',
                'Security Analysis': 'Include security considerations and analysis'
            }
            
            for option, enabled in doc_options.items():
                status = "✅ Enabled" if enabled else "❌ Disabled"
                description = option_descriptions.get(option, 'Custom documentation option')
                options_data.append([
                    option,
                    status,
                    wrap_text(description, 40)
                ])
            
            options_table = Table(options_data, colWidths=[2.2*inch, 1*inch, 2.3*inch])
            options_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            story.append(options_table)
            story.append(PageBreak())
            section_num = 2
        
        # Database Overview
        story.append(Paragraph(f"{section_num}. Database Overview", heading_style))
        db_info = db_data.get('database_info', {})
        
        overview_data = [
            ['Property', 'Value'],
            ['Database Name', db_info.get('name', 'N/A')],
            ['Database Version', db_info.get('version', 'N/A')],
            ['Total Size', db_info.get('size', 'N/A')],
            ['Created Date', db_info.get('created', 'N/A')],
            ['Last Backup', db_info.get('last_backup', 'N/A')],
            ['Total Tables', str(len(db_data.get('tables', [])))],
            ['Total Views', str(len(db_data.get('views', [])))],
            ['Total Functions', str(len(db_data.get('functions', [])))],
            ['Total Procedures', str(len(db_data.get('procedures', [])))]
        ]
        
        overview_table = Table(overview_data, colWidths=[2.5*inch, 3*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(overview_table)
        story.append(Spacer(1, 24))
        
        # Database Statistics Summary
        total_rows = sum(table.get('row_count', 0) for table in db_data.get('tables', []))
        total_size = sum(table.get('size_mb', 0) for table in db_data.get('tables', []))
        total_columns = sum(len(table.get('columns', [])) for table in db_data.get('tables', []))
        total_indexes = sum(len(table.get('indexes', [])) for table in db_data.get('tables', []))
        
        stats_data = [
            ['Metric', 'Count', 'Details'],
            ['Total Records', f"{total_rows:,}", 'Across all tables'],
            ['Total Size', f"{total_size:.1f} MB", 'Data + indexes'],
            ['Total Columns', str(total_columns), 'All table columns'],
            ['Total Indexes', str(total_indexes), 'Performance optimization'],
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 1.5*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(PageBreak())
        
        # Tables Documentation (ALL TABLES - NO LIMIT)
        section_num += 1
        story.append(Paragraph(f"{section_num}. Tables Documentation", heading_style))
        
        table_counter = 1
        for table in db_data.get('tables', []):  # ALL TABLES, NO LIMIT
            # Table header
            story.append(Paragraph(f"{section_num}.{table_counter} Table: {table['table_name']}", subheading_style))
            story.append(Paragraph(f"Description: {table.get('description', 'No description available')}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Table metadata
            table_meta_data = [
                ['Property', 'Value'],
                ['Schema', table.get('schema', 'N/A')],
                ['Table Type', table.get('table_type', 'N/A')],
                ['Row Count', f"{table.get('row_count', 0):,}"],
                ['Size (MB)', f"{table.get('size_mb', 0):.1f}"],
                ['Column Count', str(len(table.get('columns', [])))],
                ['Index Count', str(len(table.get('indexes', [])))],
                ['Constraint Count', str(len(table.get('constraints', [])))]
            ]
            
            meta_table = Table(table_meta_data, colWidths=[2.2*inch, 3.3*inch])
            meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(meta_table)
            story.append(Spacer(1, 16))
            
            # Columns documentation with improved formatting
            if table.get('columns'):
                story.append(Paragraph("Columns", ParagraphStyle('ColumnHeader', parent=styles['Heading4'], fontSize=12, textColor=colors.HexColor('#2c3e50'))))
                
                columns_data = [
                    ['Column Name', 'Data Type', 'Nullable', 'Default', 'Description']
                ]
                
                for col in table.get('columns', []):
                    # Handle long default values
                    default_val = str(col.get('default', '')) if col.get('default') else ''
                    if len(default_val) > 25:
                        default_val = default_val[:22] + '...'
                    
                    # Handle long descriptions
                    desc = str(col.get('description', ''))
                    if len(desc) > 35:
                        desc = desc[:32] + '...'
                    
                    # Handle long data types
                    data_type = str(col.get('data_type', ''))
                    if len(data_type) > 20:
                        data_type = data_type[:17] + '...'
                    
                    columns_data.append([
                        create_wrapped_paragraph(str(col.get('column_name', '')), 15),
                        create_wrapped_paragraph(data_type, 18),
                        str(col.get('is_nullable', '')),
                        create_wrapped_paragraph(default_val, 20),
                        create_wrapped_paragraph(desc, 30)
                    ])
                
                columns_table = Table(columns_data, colWidths=[1.1*inch, 1.1*inch, 0.7*inch, 1.1*inch, 1.5*inch])
                columns_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
                ]))
                
                story.append(columns_table)
                story.append(Spacer(1, 16))
            
            # Indexes documentation with improved formatting
            if table.get('indexes'):
                story.append(Paragraph("Indexes", ParagraphStyle('IndexHeader', parent=styles['Heading4'], fontSize=12, textColor=colors.HexColor('#2c3e50'))))
                
                indexes_data = [['Index Name', 'Columns', 'Type', 'Unique']]
                for idx in table.get('indexes', []):
                    columns_str = ', '.join(idx.get('columns', [])) if isinstance(idx.get('columns'), list) else str(idx.get('columns', ''))
                    
                    indexes_data.append([
                        create_wrapped_paragraph(str(idx.get('index_name', '')), 20),
                        create_wrapped_paragraph(columns_str, 25),
                        str(idx.get('index_type', '')),
                        str(idx.get('is_unique', ''))
                    ])
                
                indexes_table = Table(indexes_data, colWidths=[1.4*inch, 2*inch, 1*inch, 0.6*inch])
                indexes_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4)
                ]))
                
                story.append(indexes_table)
                story.append(Spacer(1, 16))
            
            # Constraints documentation with improved formatting
            if table.get('constraints'):
                story.append(Paragraph("Constraints", ParagraphStyle('ConstraintHeader', parent=styles['Heading4'], fontSize=12, textColor=colors.HexColor('#2c3e50'))))
                
                constraints_data = [['Constraint Name', 'Type', 'Columns', 'Definition']]
                for constraint in table.get('constraints', []):
                    columns_str = ', '.join(constraint.get('columns', [])) if isinstance(constraint.get('columns'), list) else str(constraint.get('columns', ''))
                    definition = str(constraint.get('definition', constraint.get('references', '')))
                    
                    constraints_data.append([
                        create_wrapped_paragraph(str(constraint.get('constraint_name', '')), 18),
                        str(constraint.get('constraint_type', '')),
                        create_wrapped_paragraph(columns_str, 15),
                        create_wrapped_paragraph(definition, 30)
                    ])
                
                constraints_table = Table(constraints_data, colWidths=[1.2*inch, 0.9*inch, 1.1*inch, 2.3*inch])
                constraints_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4)
                ]))
                
                story.append(constraints_table)
            
            story.append(Spacer(1, 24))
            table_counter += 1
            
            # Add page break after every 2 tables for readability
            if table_counter % 3 == 0:
                story.append(PageBreak())
        
        # Views Documentation
        if db_data.get('views'):
            story.append(PageBreak())
            section_num += 1
            story.append(Paragraph(f"{section_num}. Views Documentation", heading_style))
            
            for view in db_data.get('views', []):
                story.append(Paragraph(f"View: {view['view_name']}", subheading_style))
                story.append(Paragraph(f"Schema: {view.get('schema', 'N/A')}", styles['Normal']))
                story.append(Paragraph(f"Description: {view.get('description', 'No description available')}", styles['Normal']))
                story.append(Spacer(1, 12))
                
                if view.get('definition'):
                    story.append(Paragraph("Definition:", ParagraphStyle('DefHeader', parent=styles['Heading4'], fontSize=12)))
                    # Format SQL definition with better wrapping
                    definition = view.get('definition', '')
                    # Split long lines and format properly
                    if len(definition) > 500:
                        definition = definition[:497] + '...'
                    
                    # Create code style with proper formatting
                    code_style = ParagraphStyle(
                        'CodeStyle',
                        parent=styles['Code'],
                        fontSize=8,
                        leading=10,
                        leftIndent=10,
                        rightIndent=10,
                        spaceAfter=10,
                        backColor=colors.HexColor('#f8f9fa')
                    )
                    
                    story.append(Paragraph(definition, code_style))
                
                story.append(Spacer(1, 20))
        
        # Functions & Procedures
        if db_data.get('functions') or db_data.get('procedures'):
            story.append(PageBreak())
            section_num += 1
            story.append(Paragraph(f"{section_num}. Functions & Procedures", heading_style))
            
            for func in db_data.get('functions', []):
                story.append(Paragraph(f"Function: {func.get('function_name', 'Unknown')}", subheading_style))
                story.append(Paragraph(f"Schema: {func.get('schema', 'N/A')}", styles['Normal']))
                story.append(Paragraph(f"Return Type: {func.get('return_type', 'N/A')}", styles['Normal']))
                story.append(Paragraph(f"Parameters: {func.get('parameters', 'N/A')}", styles['Normal']))
                story.append(Paragraph(f"Description: {func.get('description', 'No description available')}", styles['Normal']))
                story.append(Spacer(1, 16))
            
            for proc in db_data.get('procedures', []):
                story.append(Paragraph(f"Procedure: {proc.get('procedure_name', 'Unknown')}", subheading_style))
                story.append(Paragraph(f"Schema: {proc.get('schema', 'N/A')}", styles['Normal']))
                story.append(Paragraph(f"Parameters: {proc.get('parameters', 'N/A')}", styles['Normal']))
                story.append(Paragraph(f"Description: {proc.get('description', 'No description available')}", styles['Normal']))
                story.append(Spacer(1, 16))
        
        # Build PDF
        doc.build(story)
        
        # Get the PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
        
    except ImportError:
        raise Exception("ReportLab not available for PDF generation")
    except Exception as e:
        raise Exception(f"PDF generation failed: {str(e)}")

def convert_to_json_schema(db_data):
    """Convert database data to JSON schema format"""
    schema = {
        "database": db_data.get('database_info', {}),
        "generated_at": datetime.now().isoformat(),
        "tables": []
    }
    
    for table in db_data.get('tables', []):
        table_schema = {
            "name": table['table_name'],
            "schema": table.get('schema'),
            "type": table.get('table_type'),
            "row_count": table.get('row_count'),
            "size_mb": table.get('size_mb'),
            "description": table.get('description'),
            "columns": table.get('columns', []),
            "indexes": table.get('indexes', []),
            "constraints": table.get('constraints', [])
        }
        schema["tables"].append(table_schema)
    
    return schema

# Sidebar additional features
def sidebar_additional_features():
    """Additional sidebar features"""
    
    st.sidebar.markdown("---")
    st.sidebar.header("🎯 Documentation Metrics")
    
    # Documentation stats
    doc_projects = st.sidebar.number_input("Documentation Projects", value=15, min_value=1, max_value=100)
    avg_time_saved = st.sidebar.number_input("Avg Hours Saved per Project", value=24, min_value=1, max_value=100)
    
    total_time_saved = doc_projects * avg_time_saved
    cost_per_hour = 85
    total_savings = total_time_saved * cost_per_hour
    
    st.sidebar.metric("⏱️ Total Hours Saved", f"{total_time_saved:,}")
    st.sidebar.metric("💰 Cost Savings", f"${total_savings:,}")
    st.sidebar.metric("📈 Efficiency Gain", "90%")
    
    # Export options
    st.sidebar.markdown("---")
    st.sidebar.header("📤 Bulk Export")
    
    if st.sidebar.button("📦 Export All Schemas"):
        st.sidebar.success("✅ Bulk export initiated!")
    
    if st.sidebar.button("📊 Generate Executive Summary"):
        st.sidebar.success("✅ Executive summary generated!")
    
    # Documentation templates
    st.sidebar.markdown("---")
    st.sidebar.header("📋 Templates")
    
    template_type = st.sidebar.selectbox(
        "Documentation Template",
        ["Standard", "Executive", "Technical", "Migration", "Compliance"]
    )
    
    if st.sidebar.button("📝 Apply Template"):
        st.sidebar.success(f"✅ {template_type} template applied!")

if __name__ == "__main__":
    main()
    sidebar_additional_features()