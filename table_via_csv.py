import streamlit as st
import pandas as pd
import fetch_database

def table_via_csv(db_server):
    st.write("#### 📥 Upload CSV to Create Table")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file and st.session_state.connected:
        df_csv = pd.read_csv(uploaded_file)

        st.write("### Preview of Uploaded CSV")
        st.dataframe(df_csv.head())

        table_name = st.text_input("Enter table name to create in database:")
        if table_name and st.button("Create Table from CSV"):
            try:
                cursor = st.session_state.cursor

                def infer_sql_type(value):
                    if pd.api.types.is_integer_dtype(value):
                        return "INT"
                    elif pd.api.types.is_float_dtype(value):
                        return "FLOAT"
                    elif pd.api.types.is_bool_dtype(value):
                        return "BOOLEAN"
                    else:
                        return "VARCHAR(255)"

                columns = df_csv.columns
                dtypes = [infer_sql_type(df_csv[col]) for col in columns]

                create_stmt = f"CREATE TABLE {table_name} (\n" + \
                            ",\n".join([f"{col} {dtype}" for col, dtype in zip(columns, dtypes)]) + "\n);"

                cursor.execute(create_stmt)

                # Prepare insert query
                placeholders = ', '.join(['%s'] * len(columns)) if db_server in ['MySQL', 'PostgreSQL-pgAdmin'] else ', '.join(['?'] * len(columns))
                insert_stmt = f"INSERT INTO {table_name} VALUES ({placeholders})"

                for _, row in df_csv.iterrows():
                    row_values = [None if pd.isna(val) else val for val in row]
                    cursor.execute(insert_stmt, tuple(row_values))

                st.session_state.connection.commit()

                # Refresh structure
                if db_server == "MySQL": st.session_state.database_info_str = fetch_database.fetch_db_mysql(st.session_state.connection, st.session_state.database)
                elif db_server == "SQLite (Local)": st.session_state.database_info_str = fetch_database.fetch_db_sqlite(st.session_state.connection, st.session_state.database)
                elif db_server == "Microsoft SQL Server (SSMS)": st.session_state.database_info_str = fetch_database.fetch_db_sqlserver(st.session_state.connection, st.session_state.database)
                elif db_server == "PostgreSQL-pgAdmin": st.session_state.database_info_str = fetch_database.fetch_db_postgresql(st.session_state.connection, st.session_state.database)

                st.success(f"✅ Table `{table_name}` created and {len(df_csv)} rows inserted.")
                del st.session_state["table_via_csv"]
            except Exception as e:
                st.error("❌ Failed to create table or insert data.")
                st.exception(e)

    # === End of CSV Section ===