
#Import Libraries
import sqlite3
from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd


# Connect to SQLite database
connector = sqlite3.connect('../python_projects-main/book_catalog.db')#Creates a connection to the SQLite database file
cursor = connector.cursor()#The cursor is used to execute SQL commands and fetch data from the database.

# Create table if it does not exist
##Table Creation-books
connector.execute(
    '''CREATE TABLE IF NOT EXISTS Books 
       (Title TEXT, 
        Author TEXT, 
        Genre TEXT, 
        Year INTEGER, 
        ISBN TEXT PRIMARY KEY NOT NULL)'''
)

# ====================================================================================================================================
#############################################FUNCTIONS#######################################################
# ====================================================================================================================================


# ====================================================================================================================================
#############################################SEARCH BOOK#######################################################
# ====================================================================================================================================
def search_books():
    search_term = entry_search.get().strip()
#retrieves the text from the search entry widget and removes any leading or trailing whitespace
    if not search_term:
        mb.showwarning("Input Error", "Please enter a search term!")
        return

    # Clear the Treevie
    tree.delete(*tree.get_children())

    # Case-insensitive search query
    query = '''
        SELECT * FROM Books
        WHERE UPPER(Title) LIKE ? OR UPPER(Author) LIKE ? OR UPPER(Genre) LIKE ? OR ISBN LIKE ? OR  year LIKE?
    '''
    search_pattern = f'%{search_term.upper()}%'

    try:
        cursor = connector.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern,search_pattern))

        # Display the search results
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                tree.insert('', END, values=row)
        else:
            mb.showinfo("No Results", "No books found matching the search term.")
    except sqlite3.Error as e:
        mb.showerror('Database Error', f'An error occurred: {e}')

######################################ADD BOOKS##########################################################################################33


def add_book():# Retrieving Input Values
    title = entry_title.get()
    author = entry_author.get()
    genre = entry_genre.get()
    year = entry_year.get()
    isbn = entry_isbn.get()
#Validating Input
    if not (title and author and genre and year and isbn):
        mb.showwarning("Input Error", "All fields are required!")
        return
#Displays a warning message if any fields are empty.
    try:#Starts a try block to handle any potential exceptions.
        connector.execute(
            'INSERT INTO Books (Title, Author, Genre, Year, ISBN) VALUES (?, ?, ?, ?, ?)',
            (title, author, genre, year, isbn)
        )
        connector.commit()#Saves the changes made by the SQL commands to the database.
        mb.showinfo('Success', 'Book added successfully!')
        clear_entries()
        display_books()#Refreshes the list of books displayed in the Treeview.
    except sqlite3.IntegrityError:
        mb.showerror('Error', 'ISBN already exists in the database!')
#Catches any IntegrityError, which typically occurs if the ISBN already exists in the database


######################################CLEAR BOOKS###################################################################################


def clear_entries():
    entry_title.delete(0, END)
    entry_author.delete(0, END)
    entry_genre.delete(0, END)
    entry_year.delete(0, END)
    entry_isbn.delete(0, END)

# ====================================================================================================================================
#############################################DISPLAY BOOK#######################################################
# ====================================================================================================================================

def display_books():
    tree.delete(*tree.get_children())# Clear all existing rows in the treeview
    cursor = connector.execute('SELECT * FROM Books')## Execute the SQL query to fetch all rows from the Books table
    for row in cursor:#: Iterates over each row returned by the query.
        tree.insert('', END, values=row)# # Insert the row data into the treeview
        #The values=row argument passes the row data as a tuple,
# id3 = tree.insert("", "end", values=("Charlie", 35))

# ====================================================================================================================================
############################################{VIEW  BOOK}#######################################################
# ====================================================================================================================================

def view_book():#Selecting the Book in the Treeview
    try:
        selected_item = tree.focus()#eturns the identifier (ID) of the currently selected row
        selected_book = tree.item(selected_item, 'values')#Retrieving Book Details
# focus() method returns the identifier of the selected item.
#This returns a tuple containing the details of the selected book (like title, author, genre, etc.).
#       Clearing Existing Entries(text) in Entry Widgets
        entry_title.delete(0, END)
        entry_author.delete(0, END)
        entry_genre.delete(0, END)
        entry_year.delete(0, END)
        entry_isbn.delete(0, END)
        # 3.Displaying Selected Book Details
        # # Insert selected book details into the respective entry fields
        entry_title.insert(0, selected_book[0])
        entry_author.insert(0, selected_book[1])
        entry_genre.insert(0, selected_book[2])
        entry_year.insert(0, selected_book[3])
        entry_isbn.insert(0, selected_book[4])

#The insert() method is used to insert the data from the selected book into the respective entry widgets.
#insert(0, ...) means the text will be inserted at the beginning of the entry widget
    #handling error
    except IndexError:
        mb.showerror('Selection Error', 'Please select a book to view its details.')

# ====================================================================================================================================
#############################################UPDATE BOOK#######################################################
# ====================================================================================================================================
#Selecting the Book to Update
def update_book():
    try:
        selected_item = tree.focus()
        selected_book = tree.item(selected_item, 'values')
        isbn = selected_book[4]#This is used as a unique identifier to update the correct book in the database.

        # Prompt user to enter new details or keep the old ones if no input is given
        new_title = sd.askstring("Update Book", "Enter new title:", initialvalue=selected_book[0])
        new_author = sd.askstring("Update Book", "Enter new author:", initialvalue=selected_book[1])
        new_genre = sd.askstring("Update Book", "Enter new genre:", initialvalue=selected_book[2])
        new_year = sd.askstring("Update Book", "Enter new year:", initialvalue=selected_book[3])
#he initialvalue parameter provides the current value as the default
        # Check if user cancelled the update
        #Handling User Cancellation
        if new_title is None or new_author is None or new_genre is None or new_year is None:
            mb.showinfo("Update Cancelled", "No changes were made.")
            return

        # Update the book details in the database
        connector.execute(
            'UPDATE Books SET Title=?, Author=?, Genre=?, Year=? WHERE ISBN=?',
            (new_title, new_author, new_genre, new_year, isbn)
        )
        connector.commit()
        mb.showinfo('Success', 'Book details updated successfully!')
        display_books()
        # clear_entries()
#Handling error
    except IndexError:
        mb.showerror('Selection Error', 'Please select a book to update its details.')
# ====================================================================================================================================
#############################################DELETE BOOK#######################################################
# ====================================================================================================================================
def delete_book():
    try:
        # Get the ID of the selected item in the Treeview
        selected_item = tree.focus()
        selected_book = tree.item(selected_item, 'values')

        # Check if a book is selected
        if not selected_book:
            raise IndexError

        isbn = selected_book[4]  # Retrieve the ISBN for identifying the book in the database

        # Confirm with the user before deleting the book
        confirm = mb.askyesno('Confirm Delete', 'Are you sure you want to delete this book?')
        if not confirm:
            return

        # Delete the selected book from the database
        connector.execute('DELETE FROM Books WHERE ISBN=?', (isbn,))
        connector.commit()  # Commit the transaction to save the changes

        # Inform the user of the successful deletion and refresh the displayed books
        mb.showinfo('Success', 'Book deleted successfully!')
        display_books()  # Refresh the Treeview to show the updated list of books
        clear_entries()  # Clear the entry fields after deletion

    except IndexError:
        # Handle the case where no book is selected
        mb.showerror('Selection Error', 'Please select a book to delete.')

    except sqlite3.Error as e:
        # Handle any database errors
        mb.showerror('Database Error', f'An error occurred while deleting the book: {e}')


# ====================================================================================================================================
#############################################SHOW ALL#######################################################
# ====================================================================================================================================
def show_all_books():
    # Clear the Treeview
    tree.delete(*tree.get_children())

    # Query the database for all books
    cursor = connector.execute('SELECT * FROM Books')

    # Display all books
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            tree.insert('', END, values=row)
    else:
        mb.showinfo("No Results", "No books found in the database.")


# ====================================================================================================================================
#############################################[GUI BOOK CATALOG]#######################################################
# ====================================================================================================================================
root = Tk()#Creates the main application window
root.title("Book Catalog")#title of the window
root.geometry("800x500")#the dimensions of the window

# Header for the Application
btn_hlb_bg = 'SteelBlue'# background color
Label(root, text='BOOK CATALOG SYSTEM', font=("Noto Sans CJK TC", 15, 'bold'), bg=btn_hlb_bg, fg='White').pack(side=TOP, fill=X)

# Frame for Input Fields
input_frame = Frame(root,bg='lightgrey')
input_frame.pack(side=LEFT, padx=100, pady=100, fill='y', expand=True)



# Subtitles for Input Fields
#Creates a label within the input_frame to indicate where to enter book details.
Label(input_frame, text="Enter Book Details", font=("Noto Sans CJK TC", 20, 'bold')).grid(row=0, columnspan=2, pady=10)
#.grid(row=0, columnspan=2, pady=10): Uses the grid layout manager to place the label in row 0 and spans across two columns with a vertical padding of 10 pixels.

# Entry widgets
Label(input_frame, text="Title",font=("Arial", 15)).grid(row=1, column=0, padx=10, pady=5)
entry_title = Entry(input_frame,font=("Arial", 12))
entry_title.grid(row=1, column=1, padx=10, pady=5)

Label(input_frame, text="Author",font=("Arial", 15)).grid(row=2, column=0, padx=10, pady=5)
entry_author = Entry(input_frame,font=("Arial", 12))
entry_author.grid(row=2, column=1, padx=10, pady=5)

Label(input_frame, text="Genre",font=("Arial", 15)).grid(row=3, column=0, padx=10, pady=5)
entry_genre = Entry(input_frame,font=("Arial", 12))
entry_genre.grid(row=3, column=1, padx=10, pady=5)

Label(input_frame, text="Year",font=("Arial", 15)).grid(row=4, column=0, padx=10, pady=5)
entry_year = Entry(input_frame,font=("Arial", 12))
entry_year.grid(row=4, column=1, padx=10, pady=5)

Label(input_frame, text="ISBN",font=("Arial", 15)).grid(row=5, column=0, padx=10, pady=5)
entry_isbn = Entry(input_frame,font=("Arial", 12))
entry_isbn.grid(row=5, column=1, padx=10, pady=5)

# Subtitles for Input Fields
Label(input_frame, text="Search Book Details", font=("Noto Sans CJK TC", 20, 'bold')).grid(row=6, columnspan=2, pady=10)
#Search
Label(input_frame, text="Search",font=("Arial", 15)).grid(row=7, column=0, padx=10, pady=5)
entry_search =Entry(input_frame,font=("Arial", 12))
entry_search.grid(row=7, column=1, padx=10, pady=5)
Button(input_frame, text="Search", command=search_books).grid(row=8, column=1, padx=10, pady=10)



# GUI Setup


# Buttons Frame
button_frame = Frame(root)
button_frame.pack(side=TOP, padx=10, pady=10)

# Configure ttk style for buttons to increase font size
style = ttk.Style()
style.configure('TButton', font=('Noto Sans CJK TC', 12), padding=10)  # Increase font and padding

# Buttons
ttk.Label(button_frame, text="Actions", font=("Noto Sans CJK TC", 20, 'bold')).grid(row=0, columnspan=2, pady=10)

ttk.Button(button_frame, text="Add Book", command=add_book, width=15).grid(row=1, column=0, padx=20, pady=20)
ttk.Button(button_frame, text="View Book", command=view_book, width=15).grid(row=1, column=1, padx=20, pady=20)
ttk.Button(button_frame, text="Update Book", command=update_book, width=15).grid(row=2, column=0, padx=20, pady=20)
ttk.Button(button_frame, text="Delete Book", command=delete_book, width=15).grid(row=2, column=1, padx=20, pady=20)
ttk.Button(button_frame, text="Show All Books", command=show_all_books, width=20).grid(row=4, columnspan=2, padx=20, pady=20)




# Frame for Treeview and Scrollbars
tree_frame = Frame(root)
tree_frame.pack(side=RIGHT, padx=10, pady=10)

# Vertical Scrollbar for Treeview
tree_scroll_y = Scrollbar(tree_frame, orient=VERTICAL)
tree_scroll_y.pack(side=RIGHT, fill=Y)

# Horizontal Scrollbar for Treeview
tree_scroll_x = Scrollbar(tree_frame, orient=HORIZONTAL)
tree_scroll_x.pack(side=BOTTOM, fill=X)

# Treeview for displaying books
tree = ttk.Treeview(tree_frame, columns=("Title", "Author", "Genre", "Year", "ISBN"), show='headings', yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
tree.heading("Title", text="Title")
tree.heading("Author", text="Author")
tree.heading("Genre", text="Genre")
tree.heading("Year", text="Year")
tree.heading("ISBN", text="ISBN")
tree.pack()

# Configure scrollbars to work with the Treeview
tree_scroll_y.config(command=tree.yview)
tree_scroll_x.config(command=tree.xview)

display_books()

# # Start the GUI event loop
root.mainloop()

# Close the database connection when the application exits
connector.close()
