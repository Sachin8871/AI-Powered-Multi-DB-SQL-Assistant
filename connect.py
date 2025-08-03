import streamlit as st
import pandas as pd
import mysql.connector
import sqlite3
import pyodbc
import psycopg2
import fetch_database

def set_connection(existing_new: str, connection, database):
    cursor = connection.cursor()
    if existing_new == "Create New database":
        cursor.execute(f"CREATE DATABASE {database}")
    cursor.execute(f"USE {database}")
    st.session_state.connection = connection
    st.session_state.cursor = cursor
    st.session_state.database = database
    st.session_state.connected = True
    st.success("✅ Connected to database!")


def connect_to_mysql():
    user_name = st.sidebar.text_input("Enter user name", value = "root")
    host = st.sidebar.text_input("Enter host", value="localhost")
    port = st.sidebar.text_input("Enter port", value=3306)
    password = st.sidebar.text_input("Enter password \n(If not applicable leave it)", type="password")
    
    existing_new = st.sidebar.radio("Select option", ["Existing database","Create New database"], index=0, horizontal=True)
    database = st.sidebar.text_input("Enter database name")

    if st.sidebar.button("Connect to Database"):
        if user_name and host and database:
            try:
                connection = mysql.connector.connect(
                    host=host,
                    user=user_name,
                    port=int(port),
                    password=password
                )

                set_connection(existing_new, connection, database)
                st.session_state.database_info_str = fetch_database.fetch_db_mysql(connection, database)

            except Exception as e:
                st.session_state.connected = False
                st.error(f"❌ Connection failed: {e}")
        else:
            st.warning("Please enter all details.")


def connect_to_sqlite():
    database = st.sidebar.text_input("Database Name")
    if st.sidebar.button("Connect to Database"):
        if database:
            try:
                connection = sqlite3.connect(database, check_same_thread=False)
                cursor = connection.cursor()
                st.session_state.connection = connection
                st.session_state.cursor = cursor
                st.session_state.database = database
                st.session_state.connected = True
                st.success("✅ Connected to database!")
                st.session_state.database_info_str = fetch_database.fetch_db_sqlite(connection, database)

            except Exception as e:
                st.session_state.connected = False
                st.error(f"❌ Connection failed: {e}")
        else:
            st.warning("Please enter all details.")


def connect_to_sqlserver():
    host = st.sidebar.text_input("Host", value = "localhost")
    username = st.sidebar.text_input("User Name")
    password = st.sidebar.text_input("Password", type="password")
    existing_new = st.sidebar.radio("Select option", ["Existing database","Create New database"], index=0, horizontal=True)
    database = st.sidebar.text_input("Enter database name")

    if st.sidebar.button("Connect to database."):
        if host and database:
            try:
                connection = pyodbc.connect(
                    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                    f"SERVER={host};"
                    f"UID={username};"
                    f"PWD={password};"
                    f"Trusted_Connection=yes",
                    autocommit=True
                )
                set_connection(existing_new, connection, database)
                st.session_state.database_info_str = fetch_database.fetch_db_sqlserver(connection, database)

            except Exception as e:
                st.session_state.connected = False
                st.error(f"❌ Connection failed: {e}")
        else:
            st.warning("Please enter all details.")
        


def connect_to_postgresql():
    host = st.sidebar.text_input("Host")
    username = st.sidebar.text_input("User Name")
    password = st.sidebar.text_input("Password", type="password")
    port = st.sidebar.text_input("Port", value=5433)
    database = st.sidebar.text_input("Database Name")

    if st.sidebar.button("Connect to database"):
        if host and username and database:
            try:
                connection = psycopg2.connect(
                    host=host,
                    database="postgres",
                    user=username,
                    password=password,
                    port=int(port)            # default PostgreSQL port is 5432
                )
                cursor = connection.cursor()
                st.session_state.connection = connection
                st.session_state.cursor = cursor
                st.session_state.database = database
                st.session_state.connected = True
                st.success("✅ Connected to database!")
                st.session_state.database_info_str = fetch_database.fetch_db_postgresql(connection, database)

            except Exception as e:
                st.session_state.connected = False
                st.error(f"❌ Connection failed: {e}")
        else:
            st.warning("Please enter all details.")
