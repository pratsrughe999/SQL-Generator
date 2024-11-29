import streamlit as st
import pandas as pd
import sqlite3

# Initialize session state for databases and table data
if "databases" not in st.session_state:
    st.session_state.databases = {"default_db": []}  # Default database
if "selected_db" not in st.session_state:
    st.session_state.selected_db = "default_db"
if "table_data" not in st.session_state:
    st.session_state.table_data = {}  # {table_name: {"columns": [], "rows": []}}


def main():
    # Sidebar for Database and Table Navigation
    st.sidebar.title("Database & Table Management")

    # Select or create a database
    st.sidebar.subheader("Databases")
    db_options = list(st.session_state.databases.keys()) + ["Create New Database"]
    db_choice = st.sidebar.selectbox("Select Database", db_options)

    if db_choice == "Create New Database":
        new_db_name = st.sidebar.text_input("Enter new database name:")
        if st.sidebar.button("Add Database"):
            add_database(new_db_name)
    else:
        st.session_state.selected_db = db_choice

    # Show tables in the selected database
    st.sidebar.subheader("Tables")
    tables = st.session_state.databases[st.session_state.selected_db]
    table_options = tables + ["Create New Table"]
    selected_table = st.sidebar.selectbox("Select Table", table_options)

    if selected_table == "Create New Table":
        create_table(st.session_state.selected_db)
    else:
        if selected_table:
            table_operations(st.session_state.selected_db, selected_table)

    # Landing page: SQL Query Editor
    st.title(f"Database: `{st.session_state.selected_db}`")
    st.subheader("Enter Your SQL Queries Here")
    sql_query = st.text_area("SQL Query", height=200)

    # Submit button for SQL query execution
    if st.button("Execute Query"):
        execute_sql_query(sql_query)


# Function to add a new database
def add_database(db_name):
    if db_name and db_name not in st.session_state.databases:
        st.session_state.databases[db_name] = []
        st.success(f"Database `{db_name}` created!")
    elif not db_name:
        st.error("Please enter a valid database name.")
    else:
        st.error(f"Database `{db_name}` already exists.")


# Function to create a new table
def create_table(db_name):
    st.subheader("Create New Table")

    table_name = st.text_input("Enter table name:")
    col_num = st.number_input("Number of Columns:", min_value=1, step=1, value=1)

    column_details = []
    for i in range(int(col_num)):
        col_name = st.text_input(f"Column {i + 1} Name:", key=f"col_name_{i}")
        col_type = st.selectbox(
            f"Data Type for Column {i + 1}:",
            options=["INTEGER", "TEXT", "REAL", "BLOB", "DATE", "BOOLEAN"],
            key=f"col_type_{i}"
        )
        if col_name:
            column_details.append((col_name, col_type))

    if st.button("Create Table"):
        if table_name and column_details:
            if table_name not in st.session_state.databases[db_name]:
                st.session_state.databases[db_name].append(table_name)
                st.session_state.table_data[table_name] = {
                    "columns": [col[0] for col in column_details],
                    "data_types": [col[1] for col in column_details],
                    "rows": []
                }
                st.success(f"Table `{table_name}` created in database `{db_name}`!")
            else:
                st.error(f"Table `{table_name}` already exists.")
        else:
            st.error("Please complete the table details.")


# Function to perform operations on a table
def table_operations(db_name, table_name):
    st.subheader(f"Operations for Table `{table_name}`")

    action = st.radio(
        "Choose an action:",
        ["View Schema", "Insert Data", "Update Data", "Delete Data", "Generate SQL Queries", "Delete Table"]
    )

    if action == "View Schema":
        view_schema(table_name)

    elif action == "Insert Data":
        insert_data(table_name)

    elif action == "Update Data":
        update_data(table_name)

    elif action == "Delete Data":
        delete_data(table_name)

    elif action == "Generate SQL Queries":
        generate_sql_queries(table_name)

    elif action == "Delete Table":
        delete_table(db_name, table_name)


# Function to view table schema
def view_schema(table_name):
    st.write(f"Schema for `{table_name}`:")
    if table_name in st.session_state.table_data:
        columns = st.session_state.table_data[table_name]["columns"]
        st.write(f"Columns: {', '.join(columns)}")
    else:
        st.error("No schema found for this table.")


# Function to insert data into a table
def insert_data(table_name):
    st.subheader(f"Insert Data into `{table_name}`")
    if table_name in st.session_state.table_data:
        columns = st.session_state.table_data[table_name]["columns"]
        new_row = {}
        for col in columns:
            new_row[col] = st.text_input(f"Enter value for `{col}`:", key=f"insert_{table_name}_{col}")

        if st.button("Insert Row"):
            st.session_state.table_data[table_name]["rows"].append(new_row)
            st.success("Row inserted successfully!")

        # Button to view the inserted data in a table format
        if st.button("View Data"):
            view_data_in_table_format(table_name)
    else:
        st.error("Table not found.")


# Function to update data in a specific row and column
def update_data(table_name):
    st.subheader(f"Update Data in `{table_name}`")

    if table_name in st.session_state.table_data:
        rows = st.session_state.table_data[table_name]["rows"]
        columns = st.session_state.table_data[table_name]["columns"]

        # Select row to update
        if rows:
            row_to_update = st.selectbox("Select Row to Update:", range(len(rows)), format_func=lambda x: str(rows[x]))
            column_to_update = st.selectbox("Select Column to Update:", columns)

            # Show the current value and allow the user to update it
            current_value = rows[row_to_update].get(column_to_update, "")
            new_value = st.text_input(f"Current Value: {current_value}", value=current_value)

            if st.button("Update Row"):
                rows[row_to_update][column_to_update] = new_value
                st.success("Row updated successfully!")
        else:
            st.write("No rows to update.")
    else:
        st.error("Table not found.")


# Function to delete data from a table
def delete_data(table_name):
    st.subheader(f"Delete Data from `{table_name}`")
    if table_name in st.session_state.table_data:
        rows = st.session_state.table_data[table_name]["rows"]
        if rows:
            row_to_delete = st.selectbox("Select Row to Delete:", rows)
            if st.button("Delete Selected Row"):
                st.session_state.table_data[table_name]["rows"].remove(row_to_delete)
                st.success("Row deleted successfully!")
        else:
            st.write("No rows to delete.")
    else:
        st.error("Table not found.")


# Function to generate SQL queries for a table
def generate_sql_queries(table_name):
    st.write(f"Generate SQL Queries for `{table_name}`: (Simulated)")


# Function to delete a table
def delete_table(db_name, table_name):
    if st.button("Delete Table"):
        st.session_state.databases[db_name].remove(table_name)
        del st.session_state.table_data[table_name]
        st.success(f"Table `{table_name}` deleted.")


# Function to display the table data in a tabular format using pandas
def view_data_in_table_format(table_name):
    st.subheader(f"Data for `{table_name}` (Tabular Format)")

    if table_name in st.session_state.table_data:
        columns = st.session_state.table_data[table_name]["columns"]
        rows = st.session_state.table_data[table_name]["rows"]

        # Create a DataFrame from the rows and columns
        df = pd.DataFrame(rows, columns=columns)
        st.dataframe(df)  # Display the dataframe in tabular form
    else:
        st.error("Table not found.")


# Function to execute SQL query
def execute_sql_query(sql_query):
    try:
        # Simulate a simple SQLite-like environment using in-memory database (this can be expanded)
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        # Create tables and insert data from session state
        for table_name, table_data in st.session_state.table_data.items():
            columns = table_data["columns"]
            cursor.execute(
                f"CREATE TABLE {table_name} ({', '.join([col + ' ' + data_type for col, data_type in zip(columns, table_data['data_types'])])});")
            for row in table_data["rows"]:
                cursor.execute(
                    f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in columns])});",
                    list(row.values()))

        # Execute the user query
        cursor.execute(sql_query)
        result = cursor.fetchall()

        # Display the query result (if it's a SELECT query)
        if sql_query.strip().upper().startswith("SELECT"):
            df = pd.DataFrame(result, columns=columns)
            st.dataframe(df)  # Display the result in tabular format
        else:
            conn.commit()
            st.success(f"Query executed successfully!")

    except Exception as e:
        st.error(f"Please correct your Query: {e}")


if __name__ == "__main__":
    main()
