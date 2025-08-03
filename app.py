import time
import pyodbc
import sqlite3
import psycopg2
import pandas as pd
import streamlit as st
import mysql.connector
from pathlib import Path
from langchain_groq import ChatGroq
from langchain.chat_models import ChatOpenAI
from langchain.chat_models import ChatCohere
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from classify_sql_query import classify_sql_query_hybrid   ## Self-build Module 
import connect           ## Self-build Module
import table_via_csv     ## Self-build Module
import fetch_database    ## Self-build Module

st.set_page_config("mysql management system using AI", page_icon="🦜")
st.title("SQL Management System Using AI")

db_server = st.sidebar.selectbox("Select Database Server", options=["MySQL", "SQLite (Local)", "Microsoft SQL Server (SSMS)", "PostgreSQL-pgAdmin"])
st.sidebar.header("Database Info")

if db_server == "MySQL":
    connect.connect_to_mysql()
elif db_server == "SQLite (Local)":
    connect.connect_to_sqlite()
elif db_server == "Microsoft SQL Server (SSMS)":
    connect.connect_to_sqlserver()
elif db_server == "PostgreSQL-pgAdmin":
    connect.connect_to_postgresql()

if 'connected' not in st.session_state:
    st.session_state.connected = False

## Button for the database
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    show_db_structure = st.checkbox("📂 Show Database Structure", value = False)
with col2:
    table_via_csv_button = st.checkbox("📥 Create table from csv file", value = False)
with col3:
    refresh_structure = st.button("🔄 Refresh", help="Refresh database structure")

if show_db_structure and "database_info_str" in st.session_state:
    st.text_area("Database Structure", st.session_state.database_info_str, height=300, disabled=True)

# ---------- AI Part ----------
## Option for the different AI Models / API Key
st.sidebar.header("Model")
import model_selection  # Self-build module

# === CSV Upload Section ===

if table_via_csv_button:
    st.session_state.table_via_csv = True
    table_via_csv.table_via_csv(db_server)

if st.session_state.connected and 'database_info_str' in st.session_state:
    model = model_selection.get_model()
    st.write("### Ask any SQL query")
    user_input = st.text_area("If you get wrong output or an error, try atlest two times with the same input.", placeholder="i.e. Show all the tables or create table ...")
    # user_input = "Show all the tables" if user_input == "" else user_input

    if "modification_execute" not in st.session_state:
        st.session_state.modification_execute = False

    if (st.button("Generate and Execute SQL Query") or st.session_state.modification_execute) and user_input:
        st.session_state.modification_execute = True
        prompt1 = ChatPromptTemplate.from_messages([
            ("system",
            f"You are an assistant. The user is working with {db_server}.\n\n"
            f"The database contains the following structure:\n{st.session_state.database_info_str}\n\n"
            f"Your job is to generate a valid SQL query specifically for {db_server}.\n"
            "⚠️ Return only the SQL query in plain text (no explanations or formatting like ```sql).\n\n"
            "🧠 Rules:\n"
            f"- If the query is unsupported in {db_server} then explain problem and suggest an alternative that works (In max 5 lines).\n"
            "- If no tables exist, say so.\n"
            f"- If the query is not possible for {db_server}, then say 'Not Possible'.\n"
            ),
            MessagesPlaceholder(variable_name="messages")
        ])

        chain = prompt1 | model
        response = chain.invoke({
            "messages": [HumanMessage(content=user_input)],
            "database_info": st.session_state.database_info_str,
            "db_server": db_server
        })

        query = response.content.strip()
        st.write("#### Query")
        st.code(query, language="sql")

        action_type = classify_sql_query_hybrid(query, model)

        try:
            cursor = st.session_state.cursor
            if action_type == 'retrieve':
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(rows, columns=columns)
                st.write(f"#### Output of the query")  
                st.dataframe(df)
            elif action_type == 'modifying' or st.session_state.modification_execute:
                prompt4 = ChatPromptTemplate.from_messages([
                    ("system", f"You are a helpful assistant. The database contains: \n{st.session_state.database_info_str}\n"
                            "Given the following modification SQL query, explain the query as warning what changes it does in database (in max 3 lines)."),
                    ("human", "{error_message}")
                ])
                chain4 = prompt4 | model
                query_explanation = chain4.invoke({"error_message": str(query)}).content
                st.warning(f"Warning \n\n {query_explanation} \n\n Do you still want to execute the query.", icon="🚨")

                col3, col4 = st.columns([7.5, 1])
                with col3:
                    if st.button("Yes, execute"):
                        cursor.execute(query)
                        st.session_state.connection.commit()
                        st.session_state.executed = True
                        st.session_state.modification_execute = False

                        if db_server == "MySQL": st.session_state.database_info_str = fetch_database.fetch_db_mysql(st.session_state.connection, st.session_state.database)
                        elif db_server == "SQLite (Local)": st.session_state.database_info_str = fetch_database.fetch_db_sqlite(st.session_state.connection, st.session_state.database)
                        elif db_server == "Microsoft SQL Server (SSMS)": st.session_state.database_info_str = fetch_database.fetch_db_sqlserver(st.session_state.connection, st.session_state.database)
                        elif db_server == "PostgreSQL-pgAdmin": st.session_state.database_info_str = fetch_database.fetch_db_postgresql(st.session_state.connection, st.session_state.database)
                with col4:
                    if st.button("Cancel"):
                        st.session_state.cancelled = True
                        st.session_state.modification_execute = False

                if "executed" in st.session_state:
                    st.success(f"Successfully executed\n\n`{query}`", icon="✅")
                    del st.session_state["executed"]
                if "cancelled" in st.session_state:
                    st.success("Cancelled.", icon="✅")
                    del st.session_state["cancelled"]
            else:
                st.warning("⚠️ " + action_type)

        except Exception as e:
            if db_server == "PostgreSQL-pgAdmin":
                st.session_state.connection.rollback()
                
            st.error("❌ SQL Execution Error")
            st.exception(e)
            st.header("Error explanation and Suggestions by AI")
            try:
                prompt4 = ChatPromptTemplate.from_messages([
                    ("system", f"You are a helpful assistant. The database contains: \n{st.session_state.database_info_str}\n"
                            "Given the following SQL error, explain the error and give suggestions."),
                    ("human", "{error_message}")
                ])
                chain4 = prompt4 | model
                error_explanation = chain4.invoke({"error_message": str(e)}).content
                st.error(error_explanation)
            except Exception as model_e:
                st.warning("⚠️ Error explanation failed")
                st.exception(model_e)