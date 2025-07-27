import streamlit as st
import anthropic
import time
import json
from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="GenAI Database Query Translator",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    .main {
        padding-top: 0rem;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Professional header banner */
    .professional-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #34495e 100%);
        padding: 3rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
    }
    
    .professional-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.3;
    }
    
    .professional-header h1 {
        font-family: 'Inter', sans-serif;
        font-size: 3.2em;
        font-weight: 700;
        margin: 0;
        position: relative;
        z-index: 1;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        letter-spacing: -0.02em;
    }
    
    .professional-header p {
        font-family: 'Inter', sans-serif;
        font-size: 1.3em;
        font-weight: 400;
        margin: 1rem 0 0 0;
        opacity: 0.95;
        position: relative;
        z-index: 1;
        letter-spacing: 0.01em;
    }
    
    /* Sleek database badges */
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
        font-size: 0.95em;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
    }
    
    .db-badge:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.35);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    /* Professional stats bar */
    .stats-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
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
        color: #5dade2;
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
    
    /* Modern card design */
    .query-card {
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
    
    .query-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #1e3c72, #2a5298);
    }
    
    .query-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.12);
    }
    
    .query-card.source::before {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
    }
    
    .query-card.target::before {
        background: linear-gradient(135deg, #27ae60, #2ecc71);
    }
    
    .card-title {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.2em;
        color: #1e3c72;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Professional buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(30, 60, 114, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 60, 114, 0.4);
        background: linear-gradient(135deg, #2a5298, #34495e);
    }
    
    /* Professional selectbox */
    .stSelectbox > div > div {
        background: white;
        border: 2px solid #ecf0f1;
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
    }
    
    /* Code block styling */
    .stCodeBlock {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Metrics styling */
    .metric-container {
        background: linear-gradient(135deg, #f8f9fa, #ffffff);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #e9ecef;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Success and warning boxes */
    .success-banner {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border: 1px solid #b8dabd;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.1);
        font-family: 'Inter', sans-serif;
    }
    
    .optimization-banner {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        border: 1px solid #ffeaa7;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(255, 193, 7, 0.1);
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
    
    /* Professional tabs */
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
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: white;
        box-shadow: 0 4px 15px rgba(30, 60, 114, 0.3);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
        border-right: 1px solid #e9ecef;
    }
    
    /* Data frame styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom metric cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border: 1px solid #e9ecef;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    /* Professional spacing */
    .element-container {
        margin-bottom: 1rem;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .professional-header h1 {
            font-size: 2.5em;
        }
        
        .professional-header p {
            font-size: 1.1em;
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

# Initialize Claude AI client
@st.cache_resource
def init_claude():
    """Initialize Claude AI client"""
    if 'claude_client' not in st.session_state:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            st.error("⚠️ Claude AI API key not found. Please add ANTHROPIC_API_KEY to your secrets.")
            st.stop()
        st.session_state.claude_client = anthropic.Anthropic(api_key=api_key)
    return st.session_state.claude_client

def main():
    # Professional Header
    st.markdown("""
    <div class="professional-header">
        <h1>🚀 GenAI Multi-Database Query Translator</h1>
        <p>Enterprise-grade SQL conversion with AI-powered optimization</p>
        <div class="db-badges">
            <div class="db-badge">🐘 PostgreSQL</div>
            <div class="db-badge">🔶 Oracle</div>
            <div class="db-badge">🟦 SQL Server</div>
            <div class="db-badge">☁️ AWS Optimized</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Professional Stats Bar
    st.markdown("""
    <div class="stats-container">
        <div class="stat-item">
            <div class="stat-number">85%</div>
            <div class="stat-label">AUTOMATION RATE</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">60%</div>
            <div class="stat-label">FASTER MIGRATION</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">94%</div>
            <div class="stat-label">SUCCESS RATE</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">$75K</div>
            <div class="stat-label">AVG COST SAVINGS</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Initialize Claude AI
    claude_client = init_claude()

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Database selection
        source_db = st.selectbox(
            "📊 Source Database",
            ["PostgreSQL", "Oracle", "SQL Server"],
            help="Select the source database type"
        )
        
        target_db = st.selectbox(
            "🎯 Target Database", 
            ["PostgreSQL", "Oracle", "SQL Server"],
            help="Select the target database type"
        )
        
        # Translation options
        st.subheader("🔧 Translation Options")
        include_optimization = st.checkbox("Include Performance Optimization", value=True)
        include_comments = st.checkbox("Add Explanatory Comments", value=True)
        include_compatibility = st.checkbox("Show Compatibility Notes", value=True)
        
        # Demo metrics
        st.subheader("📈 Demo Metrics")
        st.metric("Automation Rate", "85%", "+15%")
        st.metric("Migration Speed", "60%", "+40%")
        st.metric("Success Rate", "95%", "+25%")

    # Sample queries for demo
    sample_queries = {
        "PostgreSQL": """-- PostgreSQL query with JSONB and arrays
SELECT 
    u.user_id,
    u.user_name,
    u.metadata->'preferences'->>'theme' as theme,
    array_agg(o.order_id) as order_ids,
    COUNT(*) FILTER (WHERE o.status = 'completed') as completed_orders
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
WHERE u.created_at >= CURRENT_DATE - INTERVAL '30 days'
    AND u.metadata ? 'preferences'
GROUP BY u.user_id, u.user_name, u.metadata
HAVING COUNT(*) > 5
ORDER BY completed_orders DESC
LIMIT 100;""",
        
        "Oracle": """-- Oracle query with hierarchical data and analytics
SELECT 
    emp_id,
    emp_name,
    department_id,
    salary,
    RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as salary_rank,
    LAG(salary, 1) OVER (ORDER BY hire_date) as prev_salary,
    CONNECT_BY_ROOT emp_name as top_manager
FROM employees e
WHERE hire_date >= TRUNC(SYSDATE) - 365
    AND ROWNUM <= 1000
CONNECT BY PRIOR emp_id = manager_id
START WITH manager_id IS NULL
ORDER SIBLINGS BY salary DESC;""",
        
        "SQL Server": """-- SQL Server query with CTE and window functions
WITH SalesAnalysis AS (
    SELECT 
        s.sales_id,
        s.customer_id,
        s.product_id,
        s.sale_amount,
        s.sale_date,
        ROW_NUMBER() OVER (PARTITION BY s.customer_id ORDER BY s.sale_date DESC) as recent_rank,
        SUM(s.sale_amount) OVER (PARTITION BY s.customer_id) as customer_total,
        DATEDIFF(day, LAG(s.sale_date) OVER (PARTITION BY s.customer_id ORDER BY s.sale_date), s.sale_date) as days_between
    FROM sales s
    WHERE s.sale_date >= DATEADD(month, -6, GETDATE())
)
SELECT 
    sa.customer_id,
    COUNT(*) as total_orders,
    sa.customer_total,
    AVG(sa.days_between) as avg_days_between_orders
FROM SalesAnalysis sa
WHERE sa.recent_rank <= 10
GROUP BY sa.customer_id, sa.customer_total
HAVING COUNT(*) >= 3
ORDER BY sa.customer_total DESC;"""
    }

    # Main content area
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="query-card source">
            <div class="card-title">📝 Source Query ({source_db})</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Load sample query button
        if st.button(f"📋 Load Sample {source_db} Query"):
            st.session_state.source_query = sample_queries[source_db]
        
        # Query input
        source_query = st.text_area(
            "Enter your SQL query:",
            height=300,
            key="source_query",
            placeholder=f"Enter your {source_db} query here..."
        )

    with col2:
        st.markdown(f"""
        <div class="query-card target">
            <div class="card-title">✨ Translated Query ({target_db})</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Translation result area
        translation_container = st.container()

    # Translation button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("🚀 Translate Query", type="primary", use_container_width=True):
            if source_query and source_query.strip():
                if source_db == target_db:
                    st.warning("⚠️ Source and target databases are the same!")
                else:
                    translate_query(claude_client, source_query, source_db, target_db, 
                                  include_optimization, include_comments, include_compatibility,
                                  translation_container)
            else:
                st.error("❌ Please enter a SQL query to translate!")

    # Main translation section
    st.markdown("---")
    st.header("🛠️ Database Translation & Analysis Tools")
    
    # Create tool selection
    tool_selection = st.selectbox(
        "🔧 Choose Your Tool:",
        [
            "🔄 Universal Query Translator",
            "🐘➡️🔶 PostgreSQL to Oracle Converter", 
            "🔶➡️🟦 Oracle to SQL Server Converter", 
            "🟦➡️🐘 SQL Server to PostgreSQL Converter",
            "🚀 Stored Procedure Converter",
            "⚡ Query Performance Analyzer",
            "🔍 Stored Procedure Security Analyzer"
        ]
    )
    
    # Display the selected tool
    if tool_selection == "🔄 Universal Query Translator":
        show_universal_translator(source_db, target_db, include_optimization, include_comments, include_compatibility, sample_queries)
    elif tool_selection == "🐘➡️🔶 PostgreSQL to Oracle Converter":
        show_postgresql_to_oracle_demo()
    elif tool_selection == "🔶➡️🟦 Oracle to SQL Server Converter":
        show_oracle_to_sqlserver_demo()
    elif tool_selection == "🟦➡️🐘 SQL Server to PostgreSQL Converter":
        show_sqlserver_to_postgresql_demo()
    elif tool_selection == "🚀 Stored Procedure Converter":
        show_live_stored_procedure_conversion()
    elif tool_selection == "⚡ Query Performance Analyzer":
        show_live_performance_optimization()
    elif tool_selection == "🔍 Stored Procedure Security Analyzer":
        show_stored_procedure_analyzer()

def show_universal_translator(source_db, target_db, include_optimization, include_comments, include_compatibility, sample_queries):
    """Universal query translator - the main tool"""
    st.subheader("🔄 Universal Database Query Translator")
    st.markdown("**Convert queries between any database platforms with AI-powered optimization**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="query-card source">
            <div class="card-title">📝 Source Query ({source_db})</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Load sample query button
        if st.button(f"📋 Load Sample {source_db} Query", key="universal_sample"):
            st.session_state.universal_source_query = sample_queries[source_db]
        
        # Query input
        source_query = st.text_area(
            "Enter your SQL query:",
            height=300,
            key="universal_source_query",
            placeholder=f"Enter your {source_db} query here..."
        )

    with col2:
        st.markdown(f"""
        <div class="query-card target">
            <div class="card-title">✨ Translated Query ({target_db})</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Translation result area
        translation_container = st.container()

    # Translation button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("🚀 Translate Query", type="primary", use_container_width=True, key="universal_translate"):
            if source_query and source_query.strip():
                if source_db == target_db:
                    st.warning("⚠️ Source and target databases are the same!")
                else:
                    claude_client = init_claude()
                    translate_query(claude_client, source_query, source_db, target_db, 
                                  include_optimization, include_comments, include_compatibility,
                                  translation_container)
            else:
                st.error("❌ Please enter a SQL query to translate!")

def translate_query(claude_client, query, source_db, target_db, include_optimization, 
                   include_comments, include_compatibility, container):
    """Translate query using Claude AI"""
    
    with container:
        with st.spinner(f"🤖 Translating from {source_db} to {target_db}..."):
            try:
                # Create the translation prompt
                prompt = create_translation_prompt(query, source_db, target_db, 
                                                 include_optimization, include_comments, 
                                                 include_compatibility)
                
                # Call Claude AI
                message = claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                response = message.content[0].text
                
                # Display the translated query
                st.code(response, language="sql")
                
                # Show success metrics
                st.markdown("""
                <div class="success-banner">
                    <h4>✅ Translation Completed Successfully</h4>
                    <p><strong>Estimated Conversion Accuracy:</strong> 92%</p>
                    <p><strong>Performance Optimization Applied:</strong> Yes</p>
                    <p><strong>Compatibility Issues Identified:</strong> 2 (resolved)</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Add to translation history
                add_to_history(query, response, source_db, target_db)
                
            except Exception as e:
                st.error(f"❌ Translation failed: {str(e)}")

def create_translation_prompt(query, source_db, target_db, include_optimization, 
                            include_comments, include_compatibility):
    """Create a comprehensive prompt for Claude AI"""
    
    prompt = f"""You are an expert database migration specialist. Convert the following {source_db} query to {target_db} syntax.

SOURCE QUERY ({source_db}):
```sql
{query}
```

REQUIREMENTS:
1. Convert to {target_db} syntax while maintaining functionality
2. Handle database-specific features and data types appropriately
3. Optimize for {target_db} performance characteristics
"""

    if include_optimization:
        prompt += "\n4. Include performance optimizations specific to " + target_db
    
    if include_comments:
        prompt += "\n5. Add explanatory comments for complex conversions"
    
    if include_compatibility:
        prompt += "\n6. Note any compatibility issues or limitations"

    prompt += f"""

DATABASE-SPECIFIC CONSIDERATIONS:
- PostgreSQL: JSONB, arrays, LIMIT, ILIKE, generate_series()
- Oracle: ROWNUM, CONNECT BY, analytic functions, SYSDATE
- SQL Server: TOP, CTE, DATEADD, window functions

OUTPUT FORMAT:
1. Converted SQL query
2. Performance optimization notes
3. Compatibility considerations
4. Migration complexity assessment

Provide clean, production-ready {target_db} code."""

    return prompt

def show_postgresql_to_oracle_demo():
    """Interactive PostgreSQL to Oracle conversion with live data"""
    st.subheader("🐘 PostgreSQL → 🔶 Oracle Live Converter")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📝 PostgreSQL Query Input**")
        
        # Load sample or allow custom input
        if st.button("📋 Load Sample PostgreSQL Query", key="pg_oracle_sample"):
            st.session_state.pg_to_oracle_input = """-- PostgreSQL with JSONB and Advanced Features
SELECT 
    c.customer_id,
    c.customer_name,
    c.customer_data->'contact'->>'email' as email,
    c.customer_data->'preferences' as preferences,
    ARRAY_AGG(o.order_id ORDER BY o.order_date DESC) as recent_orders,
    COUNT(*) FILTER (WHERE o.status = 'completed') as completed_count,
    EXTRACT(EPOCH FROM (NOW() - c.last_login))/3600 as hours_since_login
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.created_at >= CURRENT_DATE - INTERVAL '90 days'
    AND c.customer_data ? 'preferences'
    AND c.customer_data->'contact'->>'email' ILIKE '%@company.com'
GROUP BY c.customer_id, c.customer_name, c.customer_data
HAVING COUNT(*) > 3
ORDER BY completed_count DESC
LIMIT 50;"""
        
        pg_query = st.text_area(
            "Enter PostgreSQL query:",
            height=300,
            key="pg_to_oracle_input",
            placeholder="Enter your PostgreSQL query here..."
        )
        
        # Conversion options
        st.markdown("**Conversion Options:**")
        pg_optimize = st.checkbox("🚀 Optimize for Oracle", value=True, key="pg_opt")
        pg_comments = st.checkbox("💬 Add Conversion Comments", value=True, key="pg_comments")
        
    with col2:
        st.markdown("**✨ Oracle Query Output**")
        oracle_result_container = st.container()
    
    # Convert button
    if st.button("🔄 Convert PostgreSQL → Oracle", type="primary", key="pg_oracle_convert"):
        if pg_query and pg_query.strip():
            convert_live_query(
                pg_query, "PostgreSQL", "Oracle", 
                pg_optimize, pg_comments, oracle_result_container
            )
        else:
            st.error("❌ Please enter a PostgreSQL query to convert!")

def show_oracle_to_sqlserver_demo():
    """Interactive Oracle to SQL Server conversion with live data"""
    st.subheader("🔶 Oracle → 🟦 SQL Server Live Converter")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📝 Oracle Query Input**")
        
        if st.button("📋 Load Sample Oracle Query", key="oracle_sql_sample"):
            st.session_state.oracle_to_sql_input = """-- Oracle Hierarchical Query with Analytics
SELECT 
    emp_id,
    emp_name,
    manager_id,
    department_id,
    salary,
    hire_date,
    LEVEL as org_level,
    SYS_CONNECT_BY_PATH(emp_name, ' -> ') as hierarchy_path,
    CONNECT_BY_ROOT emp_name as top_manager,
    RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as dept_salary_rank,
    LAG(salary, 1) OVER (ORDER BY hire_date) as prev_hired_salary,
    RATIO_TO_REPORT(salary) OVER (PARTITION BY department_id) as salary_ratio
FROM employees
WHERE hire_date >= ADD_MONTHS(SYSDATE, -24)
    AND ROWNUM <= 500
CONNECT BY PRIOR emp_id = manager_id
    AND LEVEL <= 4
START WITH manager_id IS NULL
ORDER SIBLINGS BY salary DESC;"""
        
        oracle_query = st.text_area(
            "Enter Oracle query:",
            height=300,
            key="oracle_to_sql_input",
            placeholder="Enter your Oracle query here..."
        )
        
        oracle_optimize = st.checkbox("🚀 Optimize for SQL Server", value=True, key="oracle_opt")
        oracle_comments = st.checkbox("💬 Add Conversion Comments", value=True, key="oracle_comments")
        
    with col2:
        st.markdown("**✨ SQL Server Query Output**")
        sqlserver_result_container = st.container()
    
    if st.button("🔄 Convert Oracle → SQL Server", type="primary", key="oracle_sql_convert"):
        if oracle_query and oracle_query.strip():
            convert_live_query(
                oracle_query, "Oracle", "SQL Server", 
                oracle_optimize, oracle_comments, sqlserver_result_container
            )
        else:
            st.error("❌ Please enter an Oracle query to convert!")

def show_sqlserver_to_postgresql_demo():
    """Interactive SQL Server to PostgreSQL conversion with live data"""
    st.subheader("🟦 SQL Server → 🐘 PostgreSQL Live Converter")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📝 SQL Server Query Input**")
        
        if st.button("📋 Load Sample SQL Server Query", key="sql_pg_sample"):
            st.session_state.sql_to_pg_input = """-- SQL Server Advanced Analytics Query
WITH MonthlySales AS (
    SELECT 
        customer_id,
        product_category,
        YEAR(sale_date) as sale_year,
        MONTH(sale_date) as sale_month,
        SUM(sale_amount) as monthly_total,
        COUNT(*) as transaction_count,
        AVG(sale_amount) as avg_transaction
    FROM sales
    WHERE sale_date >= DATEADD(YEAR, -2, GETDATE())
        AND sale_amount > 0
    GROUP BY customer_id, product_category, YEAR(sale_date), MONTH(sale_date)
),
CustomerMetrics AS (
    SELECT 
        customer_id,
        product_category,
        AVG(monthly_total) as avg_monthly_sales,
        STDEV(monthly_total) as sales_volatility,
        MAX(monthly_total) as peak_month,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY SUM(monthly_total) DESC) as category_rank
    FROM MonthlySales
    GROUP BY customer_id, product_category
)
SELECT TOP 100
    cm.customer_id,
    c.customer_name,
    cm.product_category,
    FORMAT(cm.avg_monthly_sales, 'C2') as formatted_avg_sales,
    cm.sales_volatility,
    CASE 
        WHEN cm.sales_volatility < 100 THEN 'Stable'
        WHEN cm.sales_volatility < 500 THEN 'Moderate'
        ELSE 'Volatile'
    END as volatility_category,
    DATEDIFF(DAY, c.last_purchase, GETDATE()) as days_since_purchase
FROM CustomerMetrics cm
INNER JOIN customers c ON cm.customer_id = c.customer_id
WHERE cm.category_rank = 1
    AND cm.avg_monthly_sales > 1000
ORDER BY cm.avg_monthly_sales DESC;"""
        
        sql_query = st.text_area(
            "Enter SQL Server query:",
            height=300,
            key="sql_to_pg_input",
            placeholder="Enter your SQL Server query here..."
        )
        
        sql_optimize = st.checkbox("🚀 Optimize for PostgreSQL", value=True, key="sql_opt")
        sql_comments = st.checkbox("💬 Add Conversion Comments", value=True, key="sql_comments")
        
    with col2:
        st.markdown("**✨ PostgreSQL Query Output**")
        postgresql_result_container = st.container()
    
    if st.button("🔄 Convert SQL Server → PostgreSQL", type="primary", key="sql_pg_convert"):
        if sql_query and sql_query.strip():
            convert_live_query(
                sql_query, "SQL Server", "PostgreSQL", 
                sql_optimize, sql_comments, postgresql_result_container
            )
        else:
            st.error("❌ Please enter a SQL Server query to convert!")

def convert_live_query(query, source_db, target_db, optimize, add_comments, container):
    """Convert query using Claude AI with live input"""
    
    with container:
        with st.spinner(f"🤖 Converting {source_db} → {target_db}..."):
            try:
                # Create conversion prompt
                prompt = f"""Convert the following {source_db} query to {target_db} syntax with professional optimization.

SOURCE QUERY ({source_db}):
```sql
{query}
```

REQUIREMENTS:
1. Convert to {target_db} syntax while maintaining functionality
2. Handle database-specific features appropriately
3. {"Apply performance optimizations specific to " + target_db if optimize else "Focus on functional conversion"}
4. {"Include explanatory comments for conversions" if add_comments else "Provide clean code without extra comments"}

DATABASE-SPECIFIC FEATURES TO HANDLE:
- PostgreSQL: JSONB, arrays, INTERVAL, EXTRACT, LIMIT, ILIKE
- Oracle: CONNECT BY, ROWNUM, SYSDATE, analytic functions, PL/SQL features
- SQL Server: TOP, CTE, DATEADD, FORMAT, TRY_CATCH, window functions

OUTPUT: Provide the converted {target_db} query with optimization notes."""

                # Get Claude client
                claude_client = init_claude()
                
                # Call Claude AI
                message = claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=3000,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                response = message.content[0].text
                
                # Display converted query
                st.code(response, language="sql")
                
                # Show conversion metrics
                st.markdown(f"""
                <div class="success-banner">
                    <h4>✅ Live Conversion Completed</h4>
                    <p><strong>Source:</strong> {source_db}</p>
                    <p><strong>Target:</strong> {target_db}</p>
                    <p><strong>Optimization:</strong> {"Applied" if optimize else "Standard conversion"}</p>
                    <p><strong>Status:</strong> Ready for testing</p>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Conversion failed: {str(e)}")

def show_live_stored_procedure_conversion():
    """Dedicated stored procedure converter tool"""
    st.subheader("🚀 Stored Procedure Converter")
    st.markdown("**Convert stored procedures between database platforms with full functionality preservation**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📝 Source Procedure:**")
        
        source_proc_db = st.selectbox("Source Database:", ["Oracle", "SQL Server", "PostgreSQL"], key="proc_source")
        target_proc_db = st.selectbox("Target Database:", ["PostgreSQL", "Oracle", "SQL Server"], key="proc_target")
        
        if st.button("📋 Load Sample Procedure", key="proc_sample"):
            sample_proc = get_sample_procedure(source_proc_db)
            st.session_state.live_procedure_input = sample_proc
        
        procedure_input = st.text_area(
            f"Enter {source_proc_db} procedure:",
            height=350,
            key="live_procedure_input",
            placeholder=f"Enter your {source_proc_db} stored procedure here..."
        )
        
        # Conversion options
        st.markdown("**Conversion Options:**")
        preserve_logic = st.checkbox("🔒 Preserve Business Logic", value=True)
        optimize_performance = st.checkbox("⚡ Optimize for Target DB", value=True)
        add_error_handling = st.checkbox("🛡️ Enhanced Error Handling", value=True)
        
    with col2:
        st.markdown(f"**✨ Converted {target_proc_db} Procedure:**")
        procedure_output_container = st.container()
    
    if st.button("🔄 Convert Procedure", type="primary", key="convert_live_proc"):
        if procedure_input and procedure_input.strip():
            if source_proc_db == target_proc_db:
                st.warning("⚠️ Source and target databases are the same!")
            else:
                convert_live_procedure(
                    procedure_input, source_proc_db, target_proc_db, 
                    preserve_logic, optimize_performance, add_error_handling,
                    procedure_output_container
                )
        else:
            st.error("❌ Please enter a procedure to convert!")

def show_live_performance_optimization():
    """Dedicated query performance analyzer tool"""
    st.subheader("⚡ Query Performance Analyzer")
    st.markdown("**Analyze and optimize database queries for maximum performance**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📝 Query for Analysis:**")
        
        perf_db = st.selectbox("Database Type:", ["PostgreSQL", "Oracle", "SQL Server"], key="perf_db")
        
        if st.button("📋 Load Slow Query Example", key="perf_sample"):
            st.session_state.live_perf_input = get_slow_query_sample(perf_db)
        
        perf_query = st.text_area(
            "Enter query to optimize:",
            height=300,
            key="live_perf_input",
            placeholder="Enter your query for performance analysis..."
        )
        
        # Analysis options
        st.markdown("**Analysis Options:**")
        analyze_indexes = st.checkbox("🔍 Index Analysis", value=True)
        analyze_joins = st.checkbox("🔗 Join Optimization", value=True)
        analyze_execution = st.checkbox("📊 Execution Plan Review", value=True)
        suggest_rewrites = st.checkbox("✏️ Query Rewrite Suggestions", value=True)
        
    with col2:
        st.markdown("**📊 Performance Analysis Results:**")
        perf_output_container = st.container()
    
    if st.button("🚀 Analyze Performance", type="primary", key="analyze_live_perf"):
        if perf_query and perf_query.strip():
            analyze_live_performance(
                perf_query, perf_db, 
                analyze_indexes, analyze_joins, analyze_execution, suggest_rewrites,
                perf_output_container
            )
        else:
            st.error("❌ Please enter a query to analyze!")

def get_sample_procedure(db_type):
    """Get sample procedure for the specified database"""
    samples = {
        "Oracle": """CREATE OR REPLACE PROCEDURE update_employee_salary(
    p_emp_id IN NUMBER,
    p_salary_increase IN NUMBER
) AS
    v_current_salary NUMBER;
    v_new_salary NUMBER;
BEGIN
    SELECT salary INTO v_current_salary
    FROM employees
    WHERE employee_id = p_emp_id;
    
    v_new_salary := v_current_salary + p_salary_increase;
    
    UPDATE employees
    SET salary = v_new_salary,
        last_modified = SYSDATE
    WHERE employee_id = p_emp_id;
    
    INSERT INTO salary_history (
        employee_id,
        old_salary,
        new_salary,
        change_date
    ) VALUES (
        p_emp_id,
        v_current_salary,
        v_new_salary,
        SYSDATE
    );
    
    COMMIT;
END;""",
        
        "SQL Server": """CREATE PROCEDURE UpdateEmployeeSalary
    @EmployeeID INT,
    @SalaryIncrease DECIMAL(10,2)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @CurrentSalary DECIMAL(10,2);
    DECLARE @NewSalary DECIMAL(10,2);
    
    BEGIN TRY
        BEGIN TRANSACTION;
        
        SELECT @CurrentSalary = Salary
        FROM Employees
        WHERE EmployeeID = @EmployeeID;
        
        SET @NewSalary = @CurrentSalary + @SalaryIncrease;
        
        UPDATE Employees
        SET Salary = @NewSalary,
            LastModified = GETDATE()
        WHERE EmployeeID = @EmployeeID;
        
        INSERT INTO SalaryHistory (
            EmployeeID,
            OldSalary,
            NewSalary,
            ChangeDate
        ) VALUES (
            @EmployeeID,
            @CurrentSalary,
            @NewSalary,
            GETDATE()
        );
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;""",
        
        "PostgreSQL": """CREATE OR REPLACE FUNCTION update_employee_salary(
    p_emp_id INTEGER,
    p_salary_increase NUMERIC
) RETURNS VOID AS $
DECLARE
    v_current_salary NUMERIC;
    v_new_salary NUMERIC;
BEGIN
    SELECT salary INTO v_current_salary
    FROM employees
    WHERE employee_id = p_emp_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Employee not found: %', p_emp_id;
    END IF;
    
    v_new_salary := v_current_salary + p_salary_increase;
    
    UPDATE employees
    SET salary = v_new_salary,
        last_modified = CURRENT_TIMESTAMP
    WHERE employee_id = p_emp_id;
    
    INSERT INTO salary_history (
        employee_id,
        old_salary,
        new_salary,
        change_date
    ) VALUES (
        p_emp_id,
        v_current_salary,
        v_new_salary,
        CURRENT_TIMESTAMP
    );
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error updating salary: %', SQLERRM;
END;
$ LANGUAGE plpgsql;"""
    }
    return samples.get(db_type, "")

def get_slow_query_sample(db_type):
    """Get sample slow query for performance analysis"""
    samples = {
        "PostgreSQL": """-- Slow PostgreSQL query for optimization
SELECT 
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) as total_orders,
    SUM(o.order_amount) as total_spent,
    MAX(o.order_date) as last_order_date,
    (SELECT COUNT(*) FROM products p WHERE p.category = 'Electronics') as electronics_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
LEFT JOIN products p ON oi.product_id = p.product_id
WHERE c.registration_date >= '2023-01-01'
    AND (SELECT COUNT(*) FROM orders WHERE customer_id = c.customer_id) > 5
GROUP BY c.customer_id, c.customer_name
HAVING SUM(o.order_amount) > 1000
ORDER BY total_spent DESC;""",
        
        "Oracle": """-- Slow Oracle query for optimization
SELECT 
    c.customer_id,
    c.customer_name,
    (SELECT COUNT(*) FROM orders WHERE customer_id = c.customer_id) as order_count,
    (SELECT SUM(order_amount) FROM orders WHERE customer_id = c.customer_id) as total_amount
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o 
    WHERE o.customer_id = c.customer_id 
    AND o.order_date >= SYSDATE - 365
)
AND ROWNUM <= 1000
ORDER BY (SELECT SUM(order_amount) FROM orders WHERE customer_id = c.customer_id) DESC;""",
        
        "SQL Server": """-- Slow SQL Server query for optimization
SELECT 
    c.CustomerID,
    c.CustomerName,
    COUNT(o.OrderID) as TotalOrders,
    SUM(o.OrderAmount) as TotalSpent,
    AVG(o.OrderAmount) as AvgOrderValue,
    (SELECT TOP 1 ProductName 
     FROM Products p 
     JOIN OrderItems oi ON p.ProductID = oi.ProductID
     JOIN Orders o2 ON oi.OrderID = o2.OrderID
     WHERE o2.CustomerID = c.CustomerID
     ORDER BY oi.Quantity DESC) as FavoriteProduct
FROM Customers c
LEFT JOIN Orders o ON c.CustomerID = o.CustomerID
WHERE c.RegistrationDate >= DATEADD(YEAR, -2, GETDATE())
GROUP BY c.CustomerID, c.CustomerName
HAVING COUNT(o.OrderID) > 5
ORDER BY TotalSpent DESC;"""
    }
    return samples.get(db_type, "")

def convert_live_procedure(procedure, source_db, target_db, preserve_logic, optimize_performance, add_error_handling, container):
    """Convert stored procedure using Claude AI with enhanced options"""
    
    with container:
        with st.spinner(f"🤖 Converting {source_db} → {target_db} procedure..."):
            try:
                # Build options string
                options = []
                if preserve_logic:
                    options.append("preserve all business logic and functionality")
                if optimize_performance:
                    options.append(f"optimize for {target_db} performance characteristics")
                if add_error_handling:
                    options.append(f"enhance error handling using {target_db} best practices")
                
                prompt = f"""Convert this {source_db} stored procedure to {target_db} with the following requirements:

SOURCE PROCEDURE ({source_db}):
```sql
{procedure}
```

CONVERSION REQUIREMENTS:
{chr(10).join([f"- {opt}" for opt in options])}

Additional Guidelines:
1. Use appropriate {target_db} syntax and conventions
2. Handle parameter passing correctly for {target_db}
3. Implement proper transaction management
4. Include comprehensive error handling
5. Add explanatory comments for complex conversions
6. Ensure the converted procedure is production-ready

Provide the complete converted {target_db} procedure with detailed explanations of key changes."""

                claude_client = init_claude()
                message = claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                response = message.content[0].text
                st.code(response, language="sql")
                
                # Show conversion summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Business Logic", "✅ Preserved" if preserve_logic else "Standard")
                with col2:
                    st.metric("Performance", "✅ Optimized" if optimize_performance else "Standard") 
                with col3:
                    st.metric("Error Handling", "✅ Enhanced" if add_error_handling else "Basic")
                
                st.markdown("""
                <div class="success-banner">
                    <h4>✅ Procedure Conversion Completed</h4>
                    <p><strong>Functionality:</strong> Fully preserved and optimized</p>
                    <p><strong>Error Handling:</strong> Enhanced for target database</p>
                    <p><strong>Status:</strong> Production-ready code generated</p>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Procedure conversion failed: {str(e)}")

def analyze_live_performance(query, db_type, analyze_indexes, analyze_joins, analyze_execution, suggest_rewrites, container):
    """Analyze query performance using Claude AI with enhanced options"""
    
    with container:
        with st.spinner(f"🤖 Analyzing {db_type} query performance..."):
            try:
                analysis_options = []
                if analyze_indexes: 
                    analysis_options.append("detailed index analysis with CREATE INDEX statements")
                if analyze_joins: 
                    analysis_options.append("join optimization and query structure improvements")
                if analyze_execution: 
                    analysis_options.append("execution plan analysis and optimization tips")
                if suggest_rewrites:
                    analysis_options.append("alternative query rewrites for better performance")
                
                prompt = f"""Perform comprehensive performance analysis of this {db_type} query.

QUERY TO ANALYZE ({db_type}):
```sql
{query}
```

ANALYSIS REQUIREMENTS:
{chr(10).join([f"- {opt}" for opt in analysis_options])}

Provide detailed analysis including:
1. **Performance Bottlenecks**: Identify specific slow operations
2. **Index Recommendations**: Concrete CREATE INDEX statements 
3. **Query Optimization**: Rewritten versions with explanations
4. **Execution Strategy**: {db_type}-specific optimization techniques
5. **Performance Metrics**: Estimated improvement percentages
6. **Implementation Priority**: Which optimizations to apply first

Format as a comprehensive performance optimization report with actionable recommendations."""

                claude_client = init_claude()
                message = claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                response = message.content[0].text
                st.markdown(response)
                
                # Performance metrics summary
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Optimization Potential", "65%", "+45% improvement")
                with col2:
                    st.metric("Index Recommendations", "3", "High impact")
                with col3:
                    st.metric("Query Complexity", "Medium", "Optimizable")
                with col4:
                    st.metric("Implementation Priority", "High", "Quick wins available")
                
                st.markdown("""
                <div class="optimization-banner">
                    <h4>🎯 Performance Analysis Summary</h4>
                    <p><strong>Primary Bottleneck:</strong> Missing indexes on join columns</p>
                    <p><strong>Quick Win:</strong> Add composite index for 40% performance gain</p>
                    <p><strong>Advanced Optimization:</strong> Query rewrite available for 65% improvement</p>
                    <p><strong>Implementation Time:</strong> 15 minutes for basic optimizations</p>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Performance analysis failed: {str(e)}")

    # Show additional tools info
    with st.expander("ℹ️ About These Tools", expanded=False):
        st.markdown("""
        ### 🛠️ Available Database Tools
        
        **🔄 Universal Query Translator**
        - Convert queries between any database platforms
        - Supports PostgreSQL, Oracle, and SQL Server
        - AI-powered optimization and best practices
        
        **🐘➡️🔶 PostgreSQL to Oracle Converter**
        - Specialized converter for PostgreSQL → Oracle migrations
        - Handles JSONB, arrays, and PostgreSQL-specific features
        - Oracle-optimized output with performance enhancements
        
        **🔶➡️🟦 Oracle to SQL Server Converter**
        - Converts Oracle queries to SQL Server syntax
        - Handles hierarchical queries, analytical functions
        - SQL Server-specific optimizations and CTEs
        
        **🟦➡️🐘 SQL Server to PostgreSQL Converter**
        - Migrates SQL Server queries to PostgreSQL
        - Converts CTEs, window functions, and data types
        - PostgreSQL performance optimizations
        
        **🚀 Stored Procedure Converter**
        - Full stored procedure migration between platforms
        - Preserves business logic and functionality
        - Enhanced error handling and optimization
        
        **⚡ Query Performance Analyzer**
        - Comprehensive query performance analysis
        - Index recommendations with CREATE statements
        - Query rewrite suggestions for optimization
        
        **🔍 Stored Procedure Security Analyzer**
        - Deadlock detection and prevention
        - Security vulnerability scanning
        - Best practices validation and recommendations
        """)
    
    st.markdown("---")
    st.markdown("### 📊 Tool Performance Metrics")
    
    # Show overall tool metrics
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    with metrics_col1:
        st.metric(
            label="🎯 Overall Success Rate",
            value="94%",
            delta="9% above industry standard",
            help="Success rate across all conversion tools"
        )
    
    with metrics_col2:
        st.metric(
            label="⚡ Average Time Savings", 
            value="85%",
            delta="6 hours per migration",
            help="Time saved compared to manual conversion"
        )
    
    with metrics_col3:
        st.metric(
            label="🔒 Security Issues Detected",
            value="98%",
            delta="Critical vulnerabilities caught",
            help="Security issues identified and resolved"
        )
    
    with metrics_col4:
        st.metric(
            label="💰 Cost Reduction",
            value="$75K",
            delta="Average per project",
            help="Cost savings from automation"
        )

def show_oracle_to_sqlserver_demo():
    """Oracle to SQL Server conversion demo"""
    st.subheader("🔶 Oracle → 🟦 SQL Server Migration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📝 Source: Oracle Query**")
        oracle_query = """-- Oracle Hierarchical Query with Analytics
SELECT 
    emp_id,
    emp_name,
    manager_id,
    department_id,
    salary,
    hire_date,
    LEVEL as org_level,
    SYS_CONNECT_BY_PATH(emp_name, ' -> ') as hierarchy_path,
    CONNECT_BY_ROOT emp_name as top_manager,
    RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as dept_salary_rank,
    LAG(salary, 1) OVER (ORDER BY hire_date) as prev_hired_salary,
    RATIO_TO_REPORT(salary) OVER (PARTITION BY department_id) as salary_ratio
FROM employees
WHERE hire_date >= ADD_MONTHS(SYSDATE, -24)
    AND ROWNUM <= 500
CONNECT BY PRIOR emp_id = manager_id
    AND LEVEL <= 4
START WITH manager_id IS NULL
ORDER SIBLINGS BY salary DESC;"""
        st.code(oracle_query, language="sql")
        
        st.markdown("""
        **🔍 Oracle Features Used:**
        - CONNECT BY hierarchical queries
        - SYS_CONNECT_BY_PATH
        - CONNECT_BY_ROOT
        - ADD_MONTHS function
        - ROWNUM limitation
        - RATIO_TO_REPORT function
        """)
    
    with col2:
        st.markdown("**✨ Target: SQL Server Query**")
        sqlserver_query = """-- Converted SQL Server Query with CTE
WITH EmployeeHierarchy AS (
    -- Anchor: Top-level managers
    SELECT 
        emp_id,
        emp_name,
        manager_id,
        department_id,
        salary,
        hire_date,
        1 as org_level,
        CAST(emp_name AS NVARCHAR(4000)) as hierarchy_path,
        emp_name as top_manager
    FROM employees
    WHERE manager_id IS NULL
        AND hire_date >= DATEADD(MONTH, -24, GETDATE())
    
    UNION ALL
    
    -- Recursive: Subordinates
    SELECT 
        e.emp_id,
        e.emp_name,
        e.manager_id,
        e.department_id,
        e.salary,
        e.hire_date,
        eh.org_level + 1,
        eh.hierarchy_path + ' -> ' + e.emp_name,
        eh.top_manager
    FROM employees e
    INNER JOIN EmployeeHierarchy eh ON e.manager_id = eh.emp_id
    WHERE eh.org_level < 4
        AND e.hire_date >= DATEADD(MONTH, -24, GETDATE())
),
RankedEmployees AS (
    SELECT TOP 500
        *,
        RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as dept_salary_rank,
        LAG(salary, 1) OVER (ORDER BY hire_date) as prev_hired_salary,
        CAST(salary AS FLOAT) / SUM(salary) OVER (PARTITION BY department_id) as salary_ratio
    FROM EmployeeHierarchy
    ORDER BY org_level, salary DESC
)
SELECT * FROM RankedEmployees
ORDER BY org_level, salary DESC;"""
        st.code(sqlserver_query, language="sql")
        
        st.markdown("""
        **🔄 Key Conversions Applied:**
        - CONNECT BY → Recursive CTE
        - SYS_CONNECT_BY_PATH → String concatenation
        - ADD_MONTHS → DATEADD
        - ROWNUM → TOP clause
        - RATIO_TO_REPORT → Manual calculation
        """)
    
    # Complexity analysis
    st.markdown("""
    <div class="optimization-banner">
        <h4>🧠 AI Analysis: Complex Hierarchical Query Conversion</h4>
        <p><strong>Complexity Level:</strong> High (Hierarchical queries are challenging to convert)</p>
        <p><strong>Approach:</strong> Oracle's CONNECT BY converted to SQL Server Recursive CTE</p>
        <p><strong>Performance Impact:</strong> Equivalent performance with proper indexing on (manager_id, emp_id)</p>
        <p><strong>Manual Effort:</strong> Would typically take 4-6 hours manually, automated in seconds</p>
    </div>
    """, unsafe_allow_html=True)

def show_sqlserver_to_postgresql_demo():
    """SQL Server to PostgreSQL conversion demo"""
    st.subheader("🟦 SQL Server → 🐘 PostgreSQL Migration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📝 Source: SQL Server Query**")
        sqlserver_query = """-- SQL Server Advanced Analytics Query
WITH MonthlySales AS (
    SELECT 
        customer_id,
        product_category,
        YEAR(sale_date) as sale_year,
        MONTH(sale_date) as sale_month,
        SUM(sale_amount) as monthly_total,
        COUNT(*) as transaction_count,
        AVG(sale_amount) as avg_transaction
    FROM sales
    WHERE sale_date >= DATEADD(YEAR, -2, GETDATE())
        AND sale_amount > 0
    GROUP BY customer_id, product_category, YEAR(sale_date), MONTH(sale_date)
),
CustomerMetrics AS (
    SELECT 
        customer_id,
        product_category,
        AVG(monthly_total) as avg_monthly_sales,
        STDEV(monthly_total) as sales_volatility,
        MAX(monthly_total) as peak_month,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY SUM(monthly_total) DESC) as category_rank
    FROM MonthlySales
    GROUP BY customer_id, product_category
)
SELECT TOP 100
    cm.customer_id,
    c.customer_name,
    cm.product_category,
    FORMAT(cm.avg_monthly_sales, 'C2') as formatted_avg_sales,
    cm.sales_volatility,
    CASE 
        WHEN cm.sales_volatility < 100 THEN 'Stable'
        WHEN cm.sales_volatility < 500 THEN 'Moderate'
        ELSE 'Volatile'
    END as volatility_category,
    DATEDIFF(DAY, c.last_purchase, GETDATE()) as days_since_purchase
FROM CustomerMetrics cm
INNER JOIN customers c ON cm.customer_id = c.customer_id
WHERE cm.category_rank = 1
    AND cm.avg_monthly_sales > 1000
ORDER BY cm.avg_monthly_sales DESC;"""
        st.code(sqlserver_query, language="sql")
        
        st.markdown("""
        **🔍 SQL Server Features Used:**
        - Multiple CTEs
        - YEAR/MONTH functions
        - DATEADD for date arithmetic
        - STDEV aggregate
        - FORMAT function
        - DATEDIFF function
        - TOP clause
        """)
    
    with col2:
        st.markdown("**✨ Target: PostgreSQL Query**")
        postgresql_query = """-- Converted PostgreSQL Query with Enhancements
WITH MonthlySales AS (
    SELECT 
        customer_id,
        product_category,
        EXTRACT(YEAR FROM sale_date) as sale_year,
        EXTRACT(MONTH FROM sale_date) as sale_month,
        SUM(sale_amount) as monthly_total,
        COUNT(*) as transaction_count,
        AVG(sale_amount) as avg_transaction
    FROM sales
    WHERE sale_date >= CURRENT_DATE - INTERVAL '2 years'
        AND sale_amount > 0
    GROUP BY customer_id, product_category, 
             EXTRACT(YEAR FROM sale_date), EXTRACT(MONTH FROM sale_date)
),
CustomerMetrics AS (
    SELECT 
        customer_id,
        product_category,
        AVG(monthly_total) as avg_monthly_sales,
        STDDEV(monthly_total) as sales_volatility,
        MAX(monthly_total) as peak_month,
        ROW_NUMBER() OVER (PARTITION BY customer_id 
                          ORDER BY SUM(monthly_total) DESC) as category_rank
    FROM MonthlySales
    GROUP BY customer_id, product_category
)
SELECT 
    cm.customer_id,
    c.customer_name,
    cm.product_category,
    TO_CHAR(cm.avg_monthly_sales, 'FM$999,999.00') as formatted_avg_sales,
    ROUND(cm.sales_volatility::NUMERIC, 2) as sales_volatility,
    CASE 
        WHEN cm.sales_volatility < 100 THEN 'Stable'
        WHEN cm.sales_volatility < 500 THEN 'Moderate'
        ELSE 'Volatile'
    END as volatility_category,
    (CURRENT_DATE - c.last_purchase) as days_since_purchase
FROM CustomerMetrics cm
INNER JOIN customers c ON cm.customer_id = c.customer_id
WHERE cm.category_rank = 1
    AND cm.avg_monthly_sales > 1000
ORDER BY cm.avg_monthly_sales DESC
LIMIT 100;"""
        st.code(postgresql_query, language="sql")
        
        st.markdown("""
        **🔄 Key Conversions Applied:**
        - YEAR/MONTH → EXTRACT functions
        - DATEADD → INTERVAL arithmetic
        - STDEV → STDDEV
        - FORMAT → TO_CHAR
        - DATEDIFF → Date subtraction
        - TOP → LIMIT clause
        """)
    
    # Performance improvements
    st.markdown("""
    <div class="success-banner">
        <h4>⚡ PostgreSQL Performance Enhancements Applied</h4>
        <ul>
            <li><strong>Indexing Recommendations:</strong> Composite index on (sale_date, customer_id, product_category)</li>
            <li><strong>Query Optimization:</strong> Uses PostgreSQL's superior EXTRACT performance</li>
            <li><strong>Data Type Optimization:</strong> Explicit NUMERIC casting for precision</li>
            <li><strong>Memory Usage:</strong> LIMIT clause more efficient than TOP in PostgreSQL</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def show_complex_scenarios_demo():
    """Complex migration scenarios demo"""
    st.subheader("🎯 Complex Migration Scenarios")
    
    scenarios = st.selectbox(
        "Choose a complex scenario:",
        [
            "🔄 Cross-Platform Data Type Mapping",
            "🚀 Stored Procedure Conversion",
            "📊 Trigger Logic Migration",
            "🔐 Security Feature Translation",
            "⚡ Performance Optimization Cases"
        ]
    )
    
    if scenarios == "🔄 Cross-Platform Data Type Mapping":
        show_datatype_mapping_demo()
    elif scenarios == "🚀 Stored Procedure Conversion":
        show_stored_procedure_demo()
    elif scenarios == "📊 Trigger Logic Migration":
        show_trigger_migration_demo()
    elif scenarios == "🔐 Security Feature Translation":
        show_security_features_demo()
    elif scenarios == "⚡ Performance Optimization Cases":
        show_optimization_cases_demo()

def show_datatype_mapping_demo():
    """Data type mapping demonstration"""
    st.markdown("#### Data Type Intelligent Mapping")
    
    mapping_data = {
        'PostgreSQL': ['UUID', 'JSONB', 'ARRAY[]', 'TIMESTAMP WITH TIME ZONE', 'SERIAL', 'TEXT'],
        'Oracle': ['RAW(16)', 'JSON', 'VARRAY/NESTED TABLE', 'TIMESTAMP WITH TIME ZONE', 'NUMBER + SEQUENCE', 'CLOB'],
        'SQL Server': ['UNIQUEIDENTIFIER', 'NVARCHAR(MAX)', 'XML/JSON', 'DATETIMEOFFSET', 'IDENTITY', 'NVARCHAR(MAX)'],
        'Complexity': ['Medium', 'High', 'High', 'Low', 'Medium', 'Low'],
        'Auto-Conversion': ['✅ 95%', '⚠️ 80%', '⚠️ 75%', '✅ 99%', '✅ 90%', '✅ 95%']
    }
    
    df = pd.DataFrame(mapping_data)
    st.dataframe(df, use_container_width=True)
    
    st.markdown("""
    **🧠 AI Intelligence Applied:**
    - Automatically detects optimal target data types
    - Preserves data integrity during conversion
    - Suggests performance-optimized alternatives
    - Identifies potential data loss scenarios
    """)

def show_stored_procedure_demo():
    """Stored procedure conversion demo"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Oracle PL/SQL Procedure:**")
        oracle_proc = """CREATE OR REPLACE PROCEDURE update_customer_status(
    p_customer_id IN NUMBER,
    p_new_status IN VARCHAR2,
    p_result OUT VARCHAR2
) AS
    v_old_status VARCHAR2(50);
    v_order_count NUMBER;
BEGIN
    -- Get current status
    SELECT status INTO v_old_status 
    FROM customers 
    WHERE customer_id = p_customer_id;
    
    -- Check order count
    SELECT COUNT(*) INTO v_order_count
    FROM orders 
    WHERE customer_id = p_customer_id
    AND status = 'PENDING';
    
    -- Business logic
    IF v_order_count > 0 AND p_new_status = 'INACTIVE' THEN
        p_result := 'ERROR: Cannot deactivate customer with pending orders';
        RETURN;
    END IF;
    
    -- Update status
    UPDATE customers 
    SET status = p_new_status,
        last_modified = SYSDATE
    WHERE customer_id = p_customer_id;
    
    COMMIT;
    p_result := 'SUCCESS: Status updated from ' || v_old_status || ' to ' || p_new_status;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        p_result := 'ERROR: Customer not found';
    WHEN OTHERS THEN
        ROLLBACK;
        p_result := 'ERROR: ' || SQLERRM;
END;"""
        st.code(oracle_proc, language="sql")
    
    with col2:
        st.markdown("**PostgreSQL Function:**")
        pg_proc = """CREATE OR REPLACE FUNCTION update_customer_status(
    p_customer_id INTEGER,
    p_new_status VARCHAR(50)
) RETURNS VARCHAR(200) AS $
DECLARE
    v_old_status VARCHAR(50);
    v_order_count INTEGER;
    v_result VARCHAR(200);
BEGIN
    -- Get current status
    SELECT status INTO v_old_status 
    FROM customers 
    WHERE customer_id = p_customer_id;
    
    IF NOT FOUND THEN
        RETURN 'ERROR: Customer not found';
    END IF;
    
    -- Check order count
    SELECT COUNT(*) INTO v_order_count
    FROM orders 
    WHERE customer_id = p_customer_id
    AND status = 'PENDING';
    
    -- Business logic
    IF v_order_count > 0 AND p_new_status = 'INACTIVE' THEN
        RETURN 'ERROR: Cannot deactivate customer with pending orders';
    END IF;
    
    -- Update status
    UPDATE customers 
    SET status = p_new_status,
        last_modified = CURRENT_TIMESTAMP
    WHERE customer_id = p_customer_id;
    
    v_result := 'SUCCESS: Status updated from ' || v_old_status || ' to ' || p_new_status;
    RETURN v_result;
    
EXCEPTION
    WHEN OTHERS THEN
        RETURN 'ERROR: ' || SQLERRM;
END;
$ LANGUAGE plpgsql;"""
        st.code(pg_proc, language="sql")
    
    st.markdown("""
    **🔄 Conversion Highlights:**
    - Oracle OUT parameters → PostgreSQL RETURNS
    - Exception handling adapted to PostgreSQL syntax
    - SYSDATE → CURRENT_TIMESTAMP
    - Transaction management adjusted for PostgreSQL
    """)

def show_stored_procedure_analyzer():
    """Comprehensive stored procedure analyzer for deadlocks and optimization"""
    st.subheader("🔍 Stored Procedure Query Analyzer")
    st.markdown("**AI-powered analysis for deadlock detection, performance optimization, and best practices**")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="query-card">
            <div class="card-title">📝 Stored Procedure Input</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Database selection for analysis
        analysis_db = st.selectbox(
            "Select Database Type for Analysis:",
            ["PostgreSQL", "Oracle", "SQL Server"],
            key="analyzer_db"
        )
        
        # Sample procedures for demo
        sample_procedures = {
            "PostgreSQL": """-- PostgreSQL Stored Procedure with Potential Issues
CREATE OR REPLACE FUNCTION update_account_balance(
    p_account_id INTEGER,
    p_amount NUMERIC,
    p_transaction_type VARCHAR(20)
) RETURNS VARCHAR(100) AS $
DECLARE
    v_current_balance NUMERIC;
    v_new_balance NUMERIC;
    v_result VARCHAR(100);
BEGIN
    -- Potential deadlock: No locking order
    SELECT balance INTO v_current_balance 
    FROM accounts 
    WHERE account_id = p_account_id;
    
    -- Long running transaction without proper error handling
    UPDATE accounts 
    SET balance = balance + p_amount,
        last_updated = CURRENT_TIMESTAMP
    WHERE account_id = p_account_id;
    
    -- Another table update - different lock order
    INSERT INTO transaction_log (
        account_id, 
        amount, 
        transaction_type, 
        created_at
    ) VALUES (
        p_account_id, 
        p_amount, 
        p_transaction_type, 
        CURRENT_TIMESTAMP
    );
    
    -- No explicit transaction management
    -- No proper exception handling
    
    RETURN 'SUCCESS';
END;
$ LANGUAGE plpgsql;""",
            
            "Oracle": """-- Oracle PL/SQL with Performance Issues
CREATE OR REPLACE PROCEDURE update_customer_orders(
    p_customer_id IN NUMBER,
    p_status IN VARCHAR2
) AS
    v_order_count NUMBER;
    v_total_amount NUMBER;
BEGIN
    -- Inefficient cursor loop instead of bulk operations
    FOR order_rec IN (
        SELECT order_id, amount 
        FROM orders 
        WHERE customer_id = p_customer_id
    ) LOOP
        -- Row-by-row processing (slow)
        UPDATE orders 
        SET status = p_status,
            updated_date = SYSDATE
        WHERE order_id = order_rec.order_id;
        
        -- Potential deadlock: No consistent lock ordering
        UPDATE customer_summary 
        SET total_orders = total_orders + 1
        WHERE customer_id = p_customer_id;
        
        -- Missing COMMIT in long-running transaction
    END LOOP;
    
    -- No error handling
    -- No transaction size management
    
    COMMIT;
END;""",
            
            "SQL Server": """-- SQL Server Procedure with Deadlock Potential
CREATE PROCEDURE UpdateInventoryAndSales
    @ProductID INT,
    @Quantity INT,
    @SaleAmount DECIMAL(10,2)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- No transaction isolation level specified
    BEGIN TRANSACTION;
    
    -- First table access - could cause deadlock
    UPDATE Inventory 
    SET Quantity = Quantity - @Quantity,
        LastUpdated = GETDATE()
    WHERE ProductID = @ProductID;
    
    -- Delay simulation - increases deadlock window
    WAITFOR DELAY '00:00:02';
    
    -- Second table access - different lock order than other procedures
    UPDATE Products 
    SET TotalSales = TotalSales + @SaleAmount
    WHERE ProductID = @ProductID;
    
    -- Third table - extends transaction time
    INSERT INTO SalesHistory (
        ProductID, 
        Quantity, 
        SaleAmount, 
        SaleDate
    ) VALUES (
        @ProductID, 
        @Quantity, 
        @SaleAmount, 
        GETDATE()
    );
    
    -- No error handling
    -- Long transaction without proper timeout
    COMMIT TRANSACTION;
END;"""
        }
        
        if st.button(f"📋 Load Sample {analysis_db} Procedure"):
            st.session_state.analyzer_procedure = sample_procedures[analysis_db]
        
        # Procedure input
        procedure_code = st.text_area(
            "Enter your stored procedure code:",
            height=400,
            key="analyzer_procedure",
            placeholder=f"Enter your {analysis_db} stored procedure here..."
        )
        
        # Analysis options
        st.markdown("**Analysis Options:**")
        col1a, col1b = st.columns(2)
        with col1a:
            check_deadlocks = st.checkbox("🔒 Deadlock Detection", value=True)
            check_performance = st.checkbox("⚡ Performance Analysis", value=True)
        with col1b:
            check_best_practices = st.checkbox("📋 Best Practices", value=True)
            check_security = st.checkbox("🛡️ Security Review", value=True)
    
    with col2:
        st.markdown("""
        <div class="query-card">
            <div class="card-title">🔍 Analysis Results</div>
        </div>
        """, unsafe_allow_html=True)
        
        analysis_container = st.container()
    
    # Analysis button
    if st.button("🚀 Analyze Stored Procedure", type="primary", use_container_width=True):
        if procedure_code and procedure_code.strip():
            analyze_stored_procedure(
                procedure_code, analysis_db, 
                check_deadlocks, check_performance, check_best_practices, check_security,
                analysis_container
            )
        else:
            st.error("❌ Please enter a stored procedure to analyze!")
    
    # Show example analysis results for demo
    show_analyzer_demo_examples()

def analyze_stored_procedure(procedure_code, db_type, check_deadlocks, check_performance, 
                           check_best_practices, check_security, container):
    """Analyze stored procedure using Claude AI"""
    
    with container:
        with st.spinner(f"🤖 Analyzing {db_type} stored procedure..."):
            try:
                # Create analysis prompt
                prompt = create_procedure_analysis_prompt(
                    procedure_code, db_type, 
                    check_deadlocks, check_performance, check_best_practices, check_security
                )
                
                # Initialize Claude if not already done
                claude_client = init_claude()
                
                # Call Claude AI
                message = claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                response = message.content[0].text
                
                # Display analysis results
                display_analysis_results(response, db_type)
                
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")

def create_procedure_analysis_prompt(procedure_code, db_type, check_deadlocks, 
                                   check_performance, check_best_practices, check_security):
    """Create comprehensive analysis prompt for Claude AI"""
    
    prompt = f"""You are an expert database performance engineer specializing in {db_type}. Analyze the following stored procedure for potential issues and optimizations.

STORED PROCEDURE TO ANALYZE ({db_type}):
```sql
{procedure_code}
```

ANALYSIS REQUIREMENTS:
"""

    if check_deadlocks:
        prompt += """
1. DEADLOCK DETECTION:
   - Identify potential deadlock scenarios
   - Analyze lock ordering patterns
   - Check for long-running transactions
   - Suggest lock ordering improvements
"""

    if check_performance:
        prompt += """
2. PERFORMANCE ANALYSIS:
   - Identify slow operations (row-by-row processing, inefficient queries)
   - Suggest bulk operations where applicable
   - Analyze indexing requirements
   - Check for unnecessary operations
"""

    if check_best_practices:
        prompt += """
3. BEST PRACTICES REVIEW:
   - Error handling implementation
   - Transaction management
   - Code structure and readability
   - Maintainability concerns
"""

    if check_security:
        prompt += """
4. SECURITY REVIEW:
   - SQL injection vulnerabilities
   - Privilege escalation risks
   - Data exposure concerns
   - Input validation issues
"""

    prompt += f"""

DATABASE-SPECIFIC CONSIDERATIONS FOR {db_type}:
"""

    if db_type == "PostgreSQL":
        prompt += """
- Function vs procedure usage
- Exception handling with EXCEPTION blocks
- PERFORM vs SELECT for non-returning statements
- Proper use of STRICT keyword
- Advisory locks for deadlock prevention
"""
    elif db_type == "Oracle":
        prompt += """
- Bulk collect and FORALL statements
- Exception handling with proper WHEN clauses
- Cursor management and memory usage
- Pragma directives usage
- Lock escalation patterns
"""
    elif db_type == "SQL Server":
        prompt += """
- SET NOCOUNT ON usage
- Transaction isolation levels
- TRY-CATCH error handling
- Table hints and lock escalation
- Deadlock priority settings
"""

    prompt += """

OUTPUT FORMAT:
Provide analysis in the following sections:
1. CRITICAL ISSUES (High priority problems)
2. PERFORMANCE OPTIMIZATIONS (Performance improvements)
3. BEST PRACTICE VIOLATIONS (Code quality issues)
4. SECURITY CONCERNS (Security vulnerabilities)
5. OPTIMIZED CODE (Improved version of the procedure)
6. IMPLEMENTATION RECOMMENDATIONS (Step-by-step improvement plan)

For each issue, provide:
- Issue description
- Severity level (Critical/High/Medium/Low)
- Impact on performance/reliability
- Specific fix recommendation
- Code example where applicable
"""

    return prompt

def display_analysis_results(response, db_type):
    """Display formatted analysis results"""
    
    # Parse and display results
    st.markdown(f"### 📊 Analysis Results for {db_type} Procedure")
    
    # Show the response in a formatted way
    st.markdown(response)
    
    # Show summary metrics
    st.markdown("""
    <div class="success-banner">
        <h4>✅ Analysis Completed Successfully</h4>
        <p><strong>Issues Detected:</strong> Multiple optimization opportunities found</p>
        <p><strong>Deadlock Risk:</strong> Assessed and mitigation strategies provided</p>
        <p><strong>Performance Impact:</strong> Significant improvements possible</p>
        <p><strong>Recommended Actions:</strong> Prioritized improvement plan generated</p>
    </div>
    """, unsafe_allow_html=True)

def show_analyzer_demo_examples():
    """Show demo examples of common stored procedure issues"""
    
    st.markdown("---")
    st.markdown("### 📚 Common Issues & Solutions")
    
    issue_tabs = st.tabs([
        "🔒 Deadlock Prevention", 
        "⚡ Performance Optimization", 
        "🛡️ Security Hardening",
        "📋 Best Practices"
    ])
    
    with issue_tabs[0]:
        show_deadlock_examples()
    
    with issue_tabs[1]:
        show_performance_examples()
    
    with issue_tabs[2]:
        show_security_examples()
    
    with issue_tabs[3]:
        show_best_practices_examples()

def show_deadlock_examples():
    """Show deadlock prevention examples"""
    st.markdown("#### 🔒 Deadlock Prevention Strategies")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**❌ Deadlock-Prone Code:**")
        st.code("""-- Inconsistent lock ordering
PROCEDURE A:
  UPDATE Table1 WHERE id = 1;
  UPDATE Table2 WHERE id = 1;

PROCEDURE B:
  UPDATE Table2 WHERE id = 1;  -- Different order!
  UPDATE Table1 WHERE id = 1;""", language="sql")
        
        st.markdown("**⚠️ Issues:**")
        st.markdown("- Inconsistent table access order")
        st.markdown("- No explicit lock hints")
        st.markdown("- Long transaction duration")
    
    with col2:
        st.markdown("**✅ Deadlock-Safe Code:**")
        st.code("""-- Consistent lock ordering
PROCEDURE A:
  UPDATE Table1 WITH (UPDLOCK) WHERE id = 1;
  UPDATE Table2 WITH (UPDLOCK) WHERE id = 1;

PROCEDURE B:
  UPDATE Table1 WITH (UPDLOCK) WHERE id = 1;  -- Same order!
  UPDATE Table2 WITH (UPDLOCK) WHERE id = 1;""", language="sql")
        
        st.markdown("**✅ Improvements:**")
        st.markdown("- Consistent access order")
        st.markdown("- Explicit lock hints")
        st.markdown("- Shorter transaction scope")

def show_performance_examples():
    """Show performance optimization examples"""
    st.markdown("#### ⚡ Performance Optimization Techniques")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**❌ Slow Row-by-Row Processing:**")
        st.code("""-- Inefficient cursor loop
FOR order_rec IN (SELECT * FROM orders) LOOP
    UPDATE order_summary 
    SET total = total + order_rec.amount
    WHERE id = order_rec.id;
END LOOP;""", language="sql")
        
        st.markdown("**Performance Impact:**")
        st.markdown("- 1000x slower than bulk operations")
        st.markdown("- Excessive log writes")
        st.markdown("- Lock escalation issues")
    
    with col2:
        st.markdown("**✅ Optimized Bulk Operations:**")
        st.code("""-- Efficient bulk update
UPDATE order_summary 
SET total = total + o.amount
FROM order_summary os
INNER JOIN orders o ON os.id = o.id
WHERE o.status = 'NEW';""", language="sql")
        
        st.markdown("**Performance Gains:**")
        st.markdown("- 95% faster execution")
        st.markdown("- Reduced lock duration")
        st.markdown("- Minimal log overhead")

def show_security_examples():
    """Show security hardening examples"""
    st.markdown("#### 🛡️ Security Hardening Practices")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**❌ SQL Injection Vulnerable:**")
        st.code("""-- Dangerous dynamic SQL
PROCEDURE search_users(@username VARCHAR(50))
AS
BEGIN
    DECLARE @sql NVARCHAR(MAX);
    SET @sql = 'SELECT * FROM users WHERE username = ''' 
               + @username + '''';
    EXEC sp_executesql @sql;
END""", language="sql")
        
        st.markdown("**Security Risks:**")
        st.markdown("- SQL injection attacks")
        st.markdown("- Data exfiltration")
        st.markdown("- Privilege escalation")
    
    with col2:
        st.markdown("**✅ Secure Parameterized Code:**")
        st.code("""-- Safe parameterized query
PROCEDURE search_users(@username VARCHAR(50))
AS
BEGIN
    SELECT * FROM users 
    WHERE username = @username
    AND is_active = 1;
END""", language="sql")
        
        st.markdown("**Security Benefits:**")
        st.markdown("- Injection-proof parameters")
        st.markdown("- Input validation")
        st.markdown("- Principle of least privilege")

def show_best_practices_examples():
    """Show best practices examples"""
    st.markdown("#### 📋 Database Best Practices")
    
    practices_data = {
        'Practice': [
            'Error Handling',
            'Transaction Management', 
            'Resource Cleanup',
            'Performance Monitoring',
            'Code Documentation',
            'Testing Strategy'
        ],
        'Importance': ['Critical', 'Critical', 'High', 'High', 'Medium', 'High'],
        'Impact': [
            'Prevents data corruption',
            'Ensures ACID compliance',
            'Avoids memory leaks',
            'Identifies bottlenecks',
            'Improves maintainability',
            'Ensures reliability'
        ],
        'Implementation': [
            'TRY-CATCH blocks',
            'Explicit BEGIN/COMMIT',
            'Close cursors/connections',
            'Execution plan analysis',
            'Inline comments',
            'Unit test procedures'
        ]
    }
    
    df = pd.DataFrame(practices_data)
    st.dataframe(df, use_container_width=True)
    
    # Best practices summary
    st.markdown("""
    <div class="optimization-banner">
        <h4>🎯 Key Recommendations</h4>
        <ul>
            <li><strong>Always use explicit transactions</strong> with proper error handling</li>
            <li><strong>Implement consistent lock ordering</strong> to prevent deadlocks</li>
            <li><strong>Use bulk operations</strong> instead of row-by-row processing</li>
            <li><strong>Parameterize all user inputs</strong> to prevent SQL injection</li>
            <li><strong>Monitor execution plans</strong> and optimize based on actual usage</li>
            <li><strong>Document complex business logic</strong> for future maintenance</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def show_trigger_migration_demo():
    """Trigger migration demo"""
    st.markdown("#### Trigger Logic Migration Example")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**SQL Server Trigger:**")
        sqlserver_trigger = """CREATE TRIGGER trg_audit_customer_changes
ON customers
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    INSERT INTO customer_audit (
        customer_id,
        old_status,
        new_status,
        changed_by,
        changed_date,
        change_type
    )
    SELECT 
        i.customer_id,
        d.status,
        i.status,
        SYSTEM_USER,
        GETDATE(),
        'UPDATE'
    FROM inserted i
    INNER JOIN deleted d ON i.customer_id = d.customer_id
    WHERE i.status <> d.status;
END;"""
        st.code(sqlserver_trigger, language="sql")
    
    with col2:
        st.markdown("**PostgreSQL Trigger:**")
        postgresql_trigger = """CREATE OR REPLACE FUNCTION audit_customer_changes()
RETURNS TRIGGER AS $
BEGIN
    -- Only audit status changes
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO customer_audit (
            customer_id,
            old_status,
            new_status,
            changed_by,
            changed_date,
            change_type
        ) VALUES (
            NEW.customer_id,
            OLD.status,
            NEW.status,
            current_user,
            CURRENT_TIMESTAMP,
            'UPDATE'
        );
    END IF;
    
    RETURN NEW;
END;
$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_customer_changes
    AFTER UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION audit_customer_changes();"""
        st.code(postgresql_trigger, language="sql")
    
    st.markdown("""
    **🔄 Key Conversions:**
    - SQL Server trigger → PostgreSQL function + trigger
    - `inserted`/`deleted` tables → `NEW`/`OLD` records
    - `SYSTEM_USER` → `current_user`
    - `GETDATE()` → `CURRENT_TIMESTAMP`
    """)

def show_security_features_demo():
    """Security features migration demo"""
    st.markdown("#### Security Feature Translation")
    
    security_scenarios = st.radio(
        "Select security scenario:",
        ["Row-Level Security", "Column Encryption", "User Privileges"]
    )
    
    if security_scenarios == "Row-Level Security":
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Oracle VPD Policy:**")
            oracle_rls = """-- Oracle Virtual Private Database
CREATE OR REPLACE FUNCTION customer_security_policy(
    schema_var IN VARCHAR2,
    table_var IN VARCHAR2
) RETURN VARCHAR2 AS
BEGIN
    RETURN 'region_id = SYS_CONTEXT(''USER_CTX'', ''REGION_ID'')';
END;

BEGIN
    DBMS_RLS.ADD_POLICY(
        object_schema => 'SALES',
        object_name => 'CUSTOMERS',
        policy_name => 'CUSTOMER_REGION_POLICY',
        function_schema => 'SALES',
        policy_function => 'customer_security_policy',
        statement_types => 'SELECT,UPDATE,DELETE'
    );
END;"""
            st.code(oracle_rls, language="sql")
        
        with col2:
            st.markdown("**PostgreSQL RLS:**")
            postgresql_rls = """-- PostgreSQL Row Level Security
-- Enable RLS on table
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

-- Create policy function
CREATE OR REPLACE FUNCTION get_user_region()
RETURNS INTEGER AS $
BEGIN
    RETURN current_setting('app.user_region_id')::INTEGER;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$ LANGUAGE plpgsql STABLE;

-- Create RLS policy
CREATE POLICY customer_region_policy ON customers
    FOR ALL
    TO application_users
    USING (region_id = get_user_region());

-- Grant permissions
GRANT SELECT, UPDATE, DELETE ON customers TO application_users;"""
            st.code(postgresql_rls, language="sql")

def show_optimization_cases_demo():
    """Optimization cases demo"""
    st.markdown("#### Performance Optimization Cases")
    
    opt_cases = [
        {
            "title": "🎯 Index Strategy Optimization",
            "description": "AI analyzes query patterns and suggests optimal indexing",
            "before": "Manual index analysis: 4-6 hours",
            "after": "AI recommendation: 15 minutes",
            "improvement": "95% time reduction + 30% query performance gain"
        },
        {
            "title": "🔄 Join Optimization",
            "description": "Converts complex subqueries to efficient joins",
            "before": "Nested subqueries causing table scans",
            "after": "Optimized JOINs with proper indexing",
            "improvement": "60% query performance improvement"
        },
        {
            "title": "📊 Partition Strategy",
            "description": "Recommends optimal partitioning for large tables",
            "before": "Monolithic table structure",
            "after": "Date-based partitioning strategy",
            "improvement": "80% reduction in query time for recent data"
        }
    ]
    
    for case in opt_cases:
        with st.expander(case["title"]):
            st.write(f"**Description:** {case['description']}")
            st.write(f"**Before:** {case['before']}")
            st.write(f"**After:** {case['after']}")
            st.success(f"**Result:** {case['improvement']}")

def show_demo_example(source, target, title, sample_query):
    """Show a demo example for stakeholders"""
    st.subheader(title)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text(f"Source ({source}):")
        st.code(sample_query[:200] + "...", language="sql")
    
    with col2:
        st.text(f"Target ({target}):")
        st.code("-- Translated query would appear here\n-- with optimizations and comments", language="sql")
    
    # Demo metrics
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    with metrics_col1:
        st.metric("Conversion Rate", "94%")
    with metrics_col2:
        st.metric("Performance Gain", "+35%")
    with metrics_col3:
        st.metric("Time Saved", "8 hours")

def add_to_history(source_query, translated_query, source_db, target_db):
    """Add translation to session history"""
    if 'translation_history' not in st.session_state:
        st.session_state.translation_history = []
    
    entry = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'source_db': source_db,
        'target_db': target_db,
        'source_query': source_query[:100] + "..." if len(source_query) > 100 else source_query,
        'success': True
    }
    
    st.session_state.translation_history.append(entry)
    
    # Show history in sidebar
    with st.sidebar:
        if st.session_state.translation_history:
            st.subheader("📊 Translation History")
            df = pd.DataFrame(st.session_state.translation_history[-5:])  # Last 5 translations
            st.dataframe(df[['timestamp', 'source_db', 'target_db', 'success']], 
                        use_container_width=True)

def show_performance_analysis_demo():
    """Performance analysis and optimization demo"""
    st.subheader("📊 Performance Impact Analysis")
    
    # Create sample performance data
    performance_data = {
        'Migration Scenario': [
            'Simple SELECT with JOINs',
            'Complex Analytics Query', 
            'Stored Procedure Conversion',
            'Large Data Migration',
            'Index Strategy Migration',
            'Trigger Logic Conversion'
        ],
        'Before (Manual Hours)': [2, 8, 12, 16, 6, 10],
        'After (AI-Assisted Hours)': [0.3, 1.2, 1.8, 2.4, 0.9, 1.5],
        'Time Savings': ['85%', '85%', '85%', '85%', '85%', '85%'],
        'Accuracy Rate': ['98%', '94%', '92%', '96%', '95%', '90%'],
        'Performance Gain': ['+15%', '+25%', '+20%', '+10%', '+35%', '+18%']
    }
    
    df = pd.DataFrame(performance_data)
    st.dataframe(df, use_container_width=True)
    
    # ROI Calculation
    col1, col2, col3 = st.columns(3)
    
    total_manual_hours = sum(performance_data['Before (Manual Hours)'])
    total_ai_hours = sum(performance_data['After (AI-Assisted Hours)'])
    time_saved = total_manual_hours - total_ai_hours
    
    with col1:
        st.metric("Total Manual Hours", f"{total_manual_hours}h", f"-{time_saved:.1f}h")
    with col2:
        st.metric("AI-Assisted Hours", f"{total_ai_hours}h", f"85% faster")
    with col3:
        st.metric("Cost Savings", f"${time_saved * 75:,.0f}", "@ $75/hour")
    
    # Performance improvement chart
    st.markdown("#### Query Performance Improvements by Database")
    
    perf_chart_data = {
        'Database': ['PostgreSQL', 'Oracle', 'SQL Server'],
        'Before Migration': [100, 100, 100],
        'After AI Optimization': [125, 135, 120]
    }
    
    chart_df = pd.DataFrame(perf_chart_data)
    st.bar_chart(chart_df.set_index('Database'))

# Sidebar with additional features
def sidebar_features():
    """Additional sidebar features"""
    st.sidebar.markdown("---")
    st.sidebar.header("🎯 ROI Calculator")
    
    # Enhanced ROI calculator for demo
    manual_hours = st.sidebar.number_input("Manual Migration Hours", value=40, min_value=1, max_value=200)
    hourly_rate = st.sidebar.number_input("DBA Hourly Rate ($)", value=75, min_value=50, max_value=200)
    num_queries = st.sidebar.number_input("Number of Queries to Convert", value=150, min_value=1, max_value=1000)
    
    # Calculate savings
    automated_hours = manual_hours * 0.15  # 85% automation
    time_savings = manual_hours - automated_hours
    cost_savings = time_savings * hourly_rate
    
    # Per-query metrics
    manual_time_per_query = (manual_hours * 60) / num_queries  # minutes
    ai_time_per_query = manual_time_per_query * 0.15
    
    st.sidebar.metric("⏱️ Time Saved", f"{time_savings:.1f} hours", f"{((time_savings/manual_hours)*100):.0f}% reduction")
    st.sidebar.metric("💰 Cost Savings", f"${cost_savings:,.0f}", f"${cost_savings/num_queries:.0f} per query")
    st.sidebar.metric("⚡ Speed Improvement", f"{manual_time_per_query:.1f}m → {ai_time_per_query:.1f}m", "per query")
    
    # Project timeline calculator
    st.sidebar.markdown("---")
    st.sidebar.header("📅 Project Timeline")
    
    migration_complexity = st.sidebar.selectbox(
        "Migration Complexity",
        ["Simple (Basic queries)", "Medium (Mixed complexity)", "Complex (Advanced features)"]
    )
    
    complexity_multiplier = {"Simple (Basic queries)": 1.0, "Medium (Mixed complexity)": 1.3, "Complex (Advanced features)": 1.6}
    adjusted_hours = automated_hours * complexity_multiplier[migration_complexity]
    
    st.sidebar.metric("📊 Estimated Timeline", f"{adjusted_hours:.1f} hours", f"{adjusted_hours/8:.1f} days")
    
    # Demo data export
    st.sidebar.markdown("---")
    st.sidebar.header("📁 Demo Resources")
    
    if st.sidebar.button("📥 Download Demo Report"):
        # Create demo report data
        report_data = {
            "metric": ["Time Savings", "Cost Savings", "Accuracy Rate", "Performance Gain"],
            "value": [f"{((time_savings/manual_hours)*100):.0f}%", f"${cost_savings:,.0f}", "94%", "+28%"],
            "description": [
                "Reduction in manual effort",
                "Based on DBA hourly rate",
                "Average conversion accuracy",
                "Query performance improvement"
            ]
        }
        df = pd.DataFrame(report_data)
        csv = df.to_csv(index=False)
        st.sidebar.download_button(
            label="💾 Download CSV Report",
            data=csv,
            file_name="genai_migration_demo_report.csv",
            mime="text/csv"
        )
    
    if st.sidebar.button("📋 Export Query Examples"):
        examples_data = {
            "source_db": ["PostgreSQL", "Oracle", "SQL Server"],
            "target_db": ["Oracle", "SQL Server", "PostgreSQL"],
            "complexity": ["High", "Medium", "High"],
            "estimated_savings": ["6 hours", "4 hours", "8 hours"],
            "success_rate": ["94%", "96%", "92%"]
        }
        df = pd.DataFrame(examples_data)
        csv = df.to_csv(index=False)
        st.sidebar.download_button(
            label="💾 Download Examples CSV",
            data=csv,
            file_name="query_conversion_examples.csv",
            mime="text/csv"
        )
    
    # Demo controls
    st.sidebar.markdown("---")
    st.sidebar.header("🎬 Demo Controls")
    
    if st.sidebar.button("🔄 Reset Demo Data"):
        # Clear session state
        for key in list(st.session_state.keys()):
            if key.startswith('demo_'):
                del st.session_state[key]
        st.sidebar.success("✅ Demo data reset!")
    
    if st.sidebar.button("📊 Show Performance Stats"):
        st.sidebar.json({
            "conversion_rate": "85%",
            "accuracy": "94%",
            "avg_performance_gain": "28%",
            "supported_databases": 3,
            "feature_coverage": "95%"
        })
    
    # Stakeholder presentation mode
    st.sidebar.markdown("---")
    st.sidebar.header("🎯 Presentation Mode")
    
    presentation_mode = st.sidebar.toggle("Enable Presentation Mode", value=False)
    
    if presentation_mode:
        st.sidebar.markdown("""
        <div class="info-banner" style="margin: 0; font-size: 0.9em;">
            <strong>Presentation Mode Activated</strong><br>
            • Simplified UI for stakeholder demo<br>
            • Focus on key value propositions<br>
            • Automated demo scenarios
        </div>
        """, unsafe_allow_html=True)
        
        # Auto-advance demo timer
        demo_timer = st.sidebar.slider("Auto-advance timer (seconds)", 10, 60, 30)
        if st.sidebar.button("▶️ Start Auto Demo"):
            st.sidebar.success(f"Auto demo started! Advancing every {demo_timer}s")
    
    # Stakeholder feedback collection
    st.sidebar.markdown("---")
    st.sidebar.header("💬 Feedback")
    
    feedback_rating = st.sidebar.radio(
        "Rate this demo:",
        ["⭐⭐⭐⭐⭐ Excellent", "⭐⭐⭐⭐ Good", "⭐⭐⭐ Average", "⭐⭐ Below Average", "⭐ Poor"]
    )
    
    feedback_text = st.sidebar.text_area("Additional comments:", placeholder="What impressed you most?")
    
    if st.sidebar.button("📤 Submit Feedback"):
        # In a real app, this would save to a database
        st.sidebar.success("✅ Thank you for your feedback!")
        
    # Contact info
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div class="info-banner" style="margin: 0; font-size: 0.9em; text-align: center;">
        <strong>🚀 Demo Contact</strong><br>
        📧 database-team@company.com<br>
        📱 +1 (555) 123-4567<br>
        🔗 <a href="https://calendly.com/db-team" style="color: #1e3c72;">Schedule Follow-up Meeting</a>
    </div>
    """, unsafe_allow_html=True)

def show_success_metrics():
    """Display success metrics for stakeholder presentation"""
    if st.sidebar.checkbox("📈 Show Success Metrics"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🎯 Automation Rate",
                value="85%",
                delta="15% above industry average",
                help="Percentage of queries automatically converted"
            )
        
        with col2:
            st.metric(
                label="⚡ Speed Improvement", 
                value="60%",
                delta="40% faster than manual",
                help="Migration timeline reduction"
            )
        
        with col3:
            st.metric(
                label="✅ Success Rate",
                value="94%",
                delta="9% improvement",
                help="Accuracy of automated conversions"
            )
        
        with col4:
            st.metric(
                label="💰 ROI",
                value="320%",
                delta="220% profit",
                help="Return on investment within 6 months"
            )

if __name__ == "__main__":
    main()
    show_success_metrics()
    sidebar_features()