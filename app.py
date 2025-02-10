from flask import Flask, render_template, request, redirect, url_for, flash
import pickle
import numpy as np
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask import session
from datetime import datetime




popular_df=pickle.load(open('popular.pkl','rb'))
pt=pickle.load(open('pt.pkl','rb'))
books=pickle.load(open('books.pkl','rb'))
similarity_score=pickle.load(open('similarity_score.pkl','rb'))


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # XAMPP default MySQL password
# app.config['MYSQL_DB'] = 'book recommended'
app.config['MYSQL_DB'] = 'book recommended'  # Use underscores for valid naming


mysql = MySQL(app)

FINE_PER_DAY = 10

MEMBERSHIP_OPTIONS = {
    "Basic": 0,        # Free
    "Premium": 100,    # ₹100 per month
    "VIP": 300         # ₹300 per month
}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please provide both email and password.', 'warning')
            return render_template('login.html')

        try:
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
            user = cursor.fetchone()
            cursor.close()
        except Exception as e:
            flash('Database error occurred. Please try again later.', 'danger')
            return render_template('login.html')

        if user and user[5] == password:  # Assuming password is stored in the 5th column
            session['loggedin'] = True
            session['id'] = user[0]       # Assuming user ID is in the 0th column
            session['email'] = user[4]    # Assuming email is in the 4th colum
            flash('Login successful!', 'success')
            return redirect(url_for('second'))
        elif user:
            flash('Incorrect password. Please try again.', 'danger')
        else:
            flash('Email not found. Please sign up.', 'warning')
            return redirect(url_for('signup'))

    return render_template('login.html')

@app.route('/second')
def second():
    return render_template('second.html' ,book_name=list(popular_df['Book-Title'].values), author=list(popular_df['Book-Author'].values),image=list(popular_df['Image-URL-M'].values), votes=list(popular_df['Book-Rating'].values), rating  =list(popular_df['avg_ratings'].values))

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        published_year = request.form['published_year']

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO books (title, author, genre, published_year) VALUES (%s, %s, %s, %s)",
                           (title, author, genre, published_year))
            mysql.connection.commit()
            cursor.close()
            flash("Book added successfully!", "success")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

        return redirect(url_for('second'))

    return render_template('add_book.html')

@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Fetch all users and books for selection
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()
    
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    
    cursor.close()
    
    if request.method == 'POST':
        user_id = request.form['user_id']
        book_id = request.form['book_id']
        return_date = request.form['return_date']

        try:
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO issued_books (user_id, book_id, return_date) VALUES (%s, %s, %s)",
                (user_id, book_id, return_date)
            )
            mysql.connection.commit()
            cursor.close()
            flash("Book issued successfully!", "success")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

        return redirect(url_for('issue_book'))

    return render_template('issue_book.html', users=users, books=books)

@app.route('/issued_books')
def issued_books():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT issued_books.id, user.username, books.title, issued_books.issue_date, issued_books.return_date
        FROM issued_books
        JOIN user ON issued_books.user_id = user.id
        JOIN books ON issued_books.book_id = books.id
    """)
    issued_books_list = cursor.fetchall()
    cursor.close()
    
    return render_template("issued_books.html", issued_books=issued_books_list)

@app.route('/return_book', methods=['GET', 'POST'])
def return_book():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch only books that are currently issued (not returned)
    cursor.execute("""
        SELECT issued_books.id, user.username, books.title, issued_books.issue_date, issued_books.return_date, issued_books.fine_amount
        FROM issued_books
        JOIN user ON issued_books.user_id = user.id
        JOIN books ON issued_books.book_id = books.id
        WHERE issued_books.returned = 0
    """)
    issued_books = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        issued_book_id = request.form['issued_book_id']

        # Calculate fine if returned late
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT return_date FROM issued_books WHERE id = %s", (issued_book_id,))
        return_date = cursor.fetchone()[0]
        
        today = datetime.today().date()
        fine = 0
        if today > return_date:
            days_late = (today - return_date).days
            fine = days_late * FINE_PER_DAY

        try:
            cursor.execute(
                "UPDATE issued_books SET returned = 1, fine_amount = %s WHERE id = %s",
                (fine, issued_book_id)
            )
            mysql.connection.commit()
            cursor.close()
            flash(f"Book returned successfully! Fine: ₹{fine}", "success")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

        return redirect(url_for('return_book'))

    return render_template('return_book.html', issued_books=issued_books)

@app.route('/pay_fine', methods=['GET', 'POST'])
def pay_fine():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch books with unpaid fines
    cursor.execute("""
        SELECT issued_books.id, user.username, books.title, issued_books.fine_amount
        FROM issued_books
        JOIN user ON issued_books.user_id = user.id
        JOIN books ON issued_books.book_id = books.id
        WHERE issued_books.fine_amount > 0
    """)
    unpaid_fines = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        issued_book_id = request.form['issued_book_id']

        try:
            cursor = mysql.connection.cursor()
            cursor.execute(
                "UPDATE issued_books SET fine_amount = 0 WHERE id = %s",
                (issued_book_id,)
            )
            mysql.connection.commit()
            cursor.close()
            flash("Fine paid successfully!", "success")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

        return redirect(url_for('pay_fine'))

    return render_template('pay_fine.html', unpaid_fines=unpaid_fines)

@app.route('/membership', methods=['GET', 'POST'])
def membership():
    if 'loggedin' not in session:
        flash("You must be logged in to access this page.", "warning")
        return redirect(url_for('login'))

    user_id = session['id']
    
    # Fetch current membership from the database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT membership FROM user WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        new_membership = request.form['membership']

        if new_membership == user['membership']:
            flash("You're already on this membership plan.", "info")
        else:
            try:
                cursor = mysql.connection.cursor()
                cursor.execute("UPDATE user SET membership = %s WHERE id = %s", (new_membership, user_id))
                mysql.connection.commit()
                cursor.close()
                flash(f"Membership updated to {new_membership}!", "success")
            except Exception as e:
                flash(f"Error updating membership: {str(e)}", "danger")

        return redirect(url_for('membership'))

    return render_template('membership.html', membership=user['membership'], options=MEMBERSHIP_OPTIONS)



@app.route('/recommend')
def recommend():
    return render_template('recommend.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/dev')
def dev():
    return render_template('dev.html')

@app.route('/forgetpass')
def forgetpass():
    return render_template('forgetpass.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Print the form data received from the user
        print(request.form)  # This will print all form fields and their values

        # Now proceed with form validation and insertion into the database
        if 'username' in request.form and 'email' in request.form and 'password' in request.form:
            username = request.form['username']
            email = request.form['email']
            # password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
            password = request.form['password']


            # Insert into MySQL
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO user (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
            mysql.connection.commit()
            cursor.close()

            flash('You have successfully registered!', 'success')
            return redirect(url_for('login'))  # Redirect to login page
        else:
            flash('Missing form data. Please try again.', 'danger')

    return render_template('signup.html')  # Show signup form for GET requests

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

def get_file_id(book_id):
    # Implement your logic to retrieve the file ID for a given book ID
    return "1ufRI06Gj1n4JI84MmALNv5UM6LDhP8Zr"

@app.route("/showbook")
def index():
    # ... your logic to retrieve book data ...
    books = [
        {"book_id": 1, "image": "...", "book_name": "..."},
        {"book_id": 2, "image": "...", "book_name": "..."},
    ]
    return render_template("index.html", books=books)

@app.route('/recommend_books',methods=['post'])
def recommend_book():
    user_input=request.form.get('user_input')
    index = np.where(pt.index == user_input)[0][0]
    
    # Find the most similar items, sorted by similarity score, excluding the first (which is the book itself)
    similar_items = sorted(list(enumerate(similarity_score[index])), key=lambda x: x[1], reverse=True)[1:6]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]].drop_duplicates('Book-Title')
        item.append(temp_df['Book-Title'].values[0])
        item.append(temp_df['Book-Author'].values[0])
        item.append(temp_df['Image-URL-M'].values[0])
        data.append(item)
        
    print(data)
    
    return render_template('recommend.html',data=data)

if __name__ == '__main__':
    app.run(debug=True)

