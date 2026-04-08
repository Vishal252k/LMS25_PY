import streamlit as st
import mysql.connector

# Connect to your MySQL database
def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Vichu123@',
        database='library_db'
    )

# Create a Streamlit app with a navbar
def main():
    st.title("📚 Library Management System")
    menu = ["Add New Book", "Lend Book", "Return Book", "Search Book",
            "Add New Publisher", "Add New Member", "Delete Book", "Lent Books", "All Staff"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Add New Book":
        add_new_book()
    elif choice == "Lend Book":
        lend_book()
    elif choice == "Return Book":
        return_book()
    elif choice == "Search Book":
        search_book()
    elif choice == "Add New Publisher":
        add_new_publisher()
    elif choice == "Add New Member":
        add_new_member()
    elif choice == "Delete Book":
        delete_book()
    elif choice == "Lent Books":
        display_lent_books()
    elif choice == "All Staff":
        display_library_staff()


# Function to add a new book
def add_new_book():
    st.title("Add New Book to Library")

    book_ISBN = st.text_input("Enter ISBN:")
    book_Author = st.text_input("Enter Author:")
    book_Title = st.text_input("Enter Title:")
    book_Language = st.selectbox("Select Language:", ["English", "Kannada", "Hindi"])
    book_Genre = st.text_input("Enter Genre:")

    try:
        db_connection = get_connection()
        cursor = db_connection.cursor()

        cursor.execute("SELECT Publisher_ID, Name FROM publisher")
        publishers_data = cursor.fetchall()
        publishers_dict = {name: id for id, name in publishers_data}

        cursor.execute("SELECT Library_ID, Name FROM library")
        libraries_data = cursor.fetchall()
        libraries_dict = {name: id for id, name in libraries_data}

        cursor.close()
        db_connection.close()

        selected_publisher = st.selectbox("Select Publisher:", list(publishers_dict.keys()))
        selected_publisher_id = publishers_dict.get(selected_publisher, None)

        selected_library = st.selectbox("Select Library:", list(libraries_dict.keys()))
        selected_library_id = libraries_dict.get(selected_library, None)

        number_of_copies = st.number_input("Enter Number of Copies:", min_value=1)

        if st.button("Add Book"):
            if selected_publisher_id is not None and selected_library_id is not None:
                db_connection = get_connection()
                cursor = db_connection.cursor()
                cursor.callproc('AddNewBook', (book_ISBN, book_Author, book_Title, book_Language,
                                               book_Genre, selected_publisher_id, selected_library_id,
                                               number_of_copies))
                db_connection.commit()
                cursor.close()
                db_connection.close()
                st.success("Book added successfully!")
            else:
                st.warning("Please select both Publisher and Library.")

    except mysql.connector.Error as e:
        st.error(f"Error: {e.msg}")


# Function to lend a book
def lend_book():
    st.title("Lend Book from Library")

    book_ISBN = st.text_input("Enter ISBN of the book to lend:")
    member_ID = st.number_input("Enter Member ID:", min_value=1)

    if st.button("Lend Book"):
        try:
            db_connection = get_connection()
            cursor = db_connection.cursor()
            cursor.callproc('LendBook', (book_ISBN, member_ID))
            db_connection.commit()
            cursor.close()
            db_connection.close()
            st.success("Book lent successfully!")

        except mysql.connector.Error as e:
            st.error(f"Error: {e.msg}")


# Function to return a book
def return_book():
    st.title("Return Book to Library")

    book_ISBN = st.text_input("Enter ISBN of the book to return:")
    member_ID = st.number_input("Enter Member ID:", min_value=1)
    return_date = st.date_input("Enter Return Date:")

    if st.button("Return Book"):
        try:
            db_connection = get_connection()
            cursor = db_connection.cursor()
            cursor.callproc('ReturnBook', (book_ISBN, member_ID, return_date))
            db_connection.commit()

            cursor.execute(
                "SELECT Fine FROM borrow WHERE ISBN_Number = %s AND Member_ID = %s",
                (book_ISBN, member_ID)
            )
            result = cursor.fetchone()
            cursor.close()
            db_connection.close()

            if result and result[0] > 0:
                st.success(f"Book returned successfully! Fine Amount: {result[0]}")
            else:
                st.success("Book returned successfully!")

        except mysql.connector.Error as e:
            st.error(f"Error: {e.msg}")


# Function to search book by ISBN, author, or title
def search_book():
    st.title("Search Book")

    search_type = st.selectbox("Search by:", ["ISBN", "Author", "Title"])
    search_query = st.text_input(f"Enter {search_type} of the book to search:")

    if st.button("🔍 Search Book"):
        try:
            db_connection = get_connection()
            cursor = db_connection.cursor()

            if search_type == "ISBN":
                cursor.execute("SELECT * FROM book WHERE ISBN_Number = %s", (search_query,))
            elif search_type == "Author":
                cursor.execute("SELECT * FROM book WHERE Author LIKE %s", (f'%{search_query}%',))
            elif search_type == "Title":
                cursor.execute("SELECT * FROM book WHERE Book_Title LIKE %s", (f'%{search_query}%',))

            result = cursor.fetchall()

            if result:
                for row in result:
                    st.markdown(f"**{row[2]}**")
                    st.markdown(f"by **{row[1]}**")
                    st.markdown(f"*{row[0]}* : *{row[3]}*")

                    publisher_id = row[5]
                    cursor.execute("SELECT * FROM publisher WHERE Publisher_ID = %s", (publisher_id,))
                    publisher_info = cursor.fetchone()
                    if publisher_info:
                        st.write(f"{publisher_info[1]}")
                        st.write(f"{publisher_info[2]}, {publisher_info[3]}, {publisher_info[4]}, {publisher_info[5]}")

                    isbn = row[0]
                    cursor.execute("SELECT number_available FROM book_copies WHERE ISBN_Number = %s", (isbn,))
                    copies_info = cursor.fetchone()
                    if copies_info:
                        st.markdown(f"Available: **{copies_info[0]}**")

                    st.markdown("---")
            else:
                st.warning("No books found matching the search criteria.")

            cursor.close()
            db_connection.close()

        except mysql.connector.Error as e:
            st.error(f"Error: {e.msg}")


# Function to delete a book
def delete_book():
    st.title("Delete Book from Library")

    book_ISBN = st.text_input("Enter ISBN of the book to delete:")

    if st.button("Delete Book"):
        try:
            db_connection = get_connection()
            cursor = db_connection.cursor()
            cursor.callproc('DeleteBook', (book_ISBN,))
            db_connection.commit()
            cursor.close()
            db_connection.close()
            st.success("Book deleted successfully!")

        except mysql.connector.Error as e:
            st.error(f"Error: {e.msg}")


# Function to add a new publisher
def add_new_publisher():
    st.title("Add New Publisher")

    try:
        db_connection = get_connection()
        cursor = db_connection.cursor()
        cursor.execute("SELECT MAX(Publisher_ID) FROM publisher")
        max_publisher_id = cursor.fetchone()[0]
        new_publisher_id = max_publisher_id + 1 if max_publisher_id is not None else 1
        cursor.close()
        db_connection.close()

        publisher_name = st.text_input("Enter Publisher Name:")
        publisher_block = st.text_input("Enter Publisher Block:")
        publisher_street = st.text_input("Enter Publisher Street:")
        publisher_city = st.text_input("Enter Publisher City:")
        publisher_pincode = st.text_input("Enter Publisher Pincode:")

        if st.button("Add Publisher"):
            try:
                db_connection = get_connection()
                cursor = db_connection.cursor()
                cursor.execute(
                    "INSERT INTO publisher (Publisher_ID, Name, Block_No, Street, City, Pincode) VALUES (%s, %s, %s, %s, %s, %s)",
                    (new_publisher_id, publisher_name, publisher_block, publisher_street, publisher_city, publisher_pincode)
                )
                db_connection.commit()
                cursor.close()
                db_connection.close()
                st.success("New Publisher added successfully!")

            except mysql.connector.Error as e:
                st.error(f"Error: {e.msg}")

    except mysql.connector.Error as e:
        st.error(f"Error: {e.msg}")


# Function to add a new member
def add_new_member():
    st.title("Add New Member")

    try:
        db_connection = get_connection()
        cursor = db_connection.cursor()
        cursor.execute("SELECT MAX(Member_ID) FROM member")
        max_member_id = cursor.fetchone()[0]
        new_member_id = max_member_id + 1 if max_member_id is not None else 1
        cursor.close()
        db_connection.close()

        member_name = st.text_input("Enter Member Name:")
        member_email = st.text_input("Enter Member Email:")

        if st.button("Add Member"):
            try:
                db_connection = get_connection()
                cursor = db_connection.cursor()
                cursor.execute(
                    "INSERT INTO member (Member_ID, Name, Email) VALUES (%s, %s, %s)",
                    (new_member_id, member_name, member_email)
                )
                db_connection.commit()
                cursor.close()
                db_connection.close()
                st.success("New Member added successfully!")

            except mysql.connector.Error as e:
                st.error(f"Error: {e.msg}")

    except mysql.connector.Error as e:
        st.error(f"Error: {e.msg}")


# Function to display lent books
def display_lent_books():
    st.title("Lent Books")
    try:
        db_connection = get_connection()
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT b.ISBN_Number, b.Author, b.Book_Title, m.Name AS Member_Name, br.Due_Date
            FROM borrow AS br
            INNER JOIN book AS b ON br.ISBN_Number = b.ISBN_Number
            INNER JOIN member AS m ON br.Member_ID = m.Member_ID
            WHERE br.Return_Date IS NULL
        """)
        lent_books = cursor.fetchall()
        cursor.close()
        db_connection.close()

        if lent_books:
            st.header("Lent Books (Yet to be returned)")
            for book in lent_books:
                st.write(f"ISBN: {book[0]}")
                st.write(f"Author: {book[1]}")
                st.write(f"Title: {book[2]}")
                st.write(f"Borrowed by: {book[3]}")
                st.write(f"Due Date: {book[4]}")
                st.write("---")
        else:
            st.warning("No books are currently lent and yet to be returned.")

    except mysql.connector.Error as e:
        st.error(f"Error: {e.msg}")


# Function to display library staff details
def display_library_staff():
    st.title("Library Staff")
    try:
        db_connection = get_connection()
        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM staff")
        staff_members = cursor.fetchall()
        cursor.close()
        db_connection.close()

        if staff_members:
            st.header("Library Staff Members")
            for staff_member in staff_members:
                st.write(f"ID: {staff_member[0]}")
                st.write(f"Name: {staff_member[1]}")
                st.write(f"Role: {staff_member[2]}")
                st.write(f"Contact: {staff_member[3]}")
                st.write("---")
        else:
            st.warning("No library staff members found.")

    except mysql.connector.Error as e:
        st.error(f"Error: {e.msg}")


# Run the Streamlit app
if __name__ == "__main__":
    main()