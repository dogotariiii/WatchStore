import os
from concurrent.futures import ThreadPoolExecutor  # Import ThreadPoolExecutor for parallel processing
from datetime import datetime
from flask import Flask, render_template, send_from_directory, redirect, request, url_for, flash, session
from werkzeug.utils import secure_filename
from db import db
from db_models import Watches, User, Orders, Base
from models.DatabaseFacade import DatabaseFacade
from models.OrderStrategy import StandardOrderStrategy, FreeShippingOrderStrategy
from models.Repository import UserRepository
from models.watch_factory import WatchFactory
from models.watch_decorator import *
from models.observer import Subject, AdminObserver, UserObserver

# Import statements

# Initialize the Flask app
app = Flask(__name__)

# Define constants
UPLOAD_FOLDER = 'photos'

# Configure the Flask app
app.config['SECRET_KEY'] = 'do later'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/watchshopdb'
app.config['UPLOADED_FOLDER'] = UPLOAD_FOLDER

# Initialize the database
db.init_app(app)
db.migrate(app, Base)

# Initialize the DatabaseFacade instance
db_facade = DatabaseFacade()

# Register the admin observer

subject = Subject()
subject.register(AdminObserver())
subject.register(UserObserver())

# Initialize the ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=2)

watch_factory = WatchFactory()


@app.route('/')
def main():
    # Fetch all watches using DatabaseFacade
    watches = db_facade.fetch_all_available_watches()
    user_logged_in = 'user_id' in session
    return render_template('home.html', watches=watches, user_logged_in=user_logged_in, title="Watch Shop")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']

        new_user = db_facade.add_user(username, email, password, full_name)

        flash("User registered successfully", "success")
        return redirect(url_for('login'))

    return render_template('register.html', title="")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Use db.session.query() instead of User.query
        login_user = db.session.query(User).filter_by(username=username, password=password).first()

        if login_user is not None:
            login_user.last_login = datetime.now()  # Update last login time
            db.session.commit()

            # Set user_id in session upon successful login
            session['user_id'] = login_user.id_user

            return redirect(url_for('account'))
        else:
            flash("Invalid username or password", "error")
    return render_template("login.html")


@app.route('/delete-user/<int:id_user>', methods=['GET', 'POST'])
def delete_user(id_user):
    if request.method == 'POST':
        # Check if the user is logged in and is an admin
        if 'user_id' not in session:
            flash("You need to log in to perform this action", "error")
            return redirect(url_for('login'))

        # Call the delete_user method from UserRepository
        if UserRepository.delete_user(id_user):
            flash("User deleted successfully", "success")
        else:
            flash("User not found", "error")

        return redirect(url_for('home'))

    # If the request method is not POST, return a method not allowed error
    return "Method not allowed", 405


@app.route('/account')
def account():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = db_facade.fetch_user_by_id(user_id)
    user_logged_in = True
    username = user.username
    notifications = subject.notifications

    if user.is_admin:
        all_users = db_facade.fetch_all_users()
        all_ordered_watches = db_facade.fetch_all_ordered_watches()
        watches = db_facade.fetch_all_watches()

        return render_template('account.html', ordered_watches=all_ordered_watches, is_admin=user.is_admin,
                               user_logged_in=user_logged_in,
                               all_users=all_users, username=username, watches=watches, notifications=notifications)
    else:
        return render_template('account.html', is_admin=user.is_admin,
                               user_logged_in=user_logged_in, username=username, notifications=notifications)


@app.route('/rented-watches')
def ordered_watches():
    if 'user_id' not in session:
        # Redirect to login if user is not logged in
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = db.session.query(User).get(user_id)
    user_logged_in = True

    if user.is_admin:
        # Fetch all ordered watches if user is an admin
        ordered_watches = db_facade.fetch_all_ordered_watches()
    else:
        # Fetch watches ordered by the current user
        ordered_watches = db_facade.fetch_user_ordered_watches(user_id)

    return render_template('ordered_watches.html', ordered_watches=ordered_watches, user_logged_in=user_logged_in,
                           is_admin=user.is_admin, title="My Ordered Watches")


@app.route('/delete-order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    if request.method == 'POST':
        # Check if the user is logged in or has admin privileges (if applicable)
        if 'user_id' not in session:
            flash("You need to log in to perform this action", "error")
            return redirect(url_for('login'))

        # Fetch the order by its ID
        order = db_facade.fetch_order_by_id(order_id)

        # Check if the order exists
        if not order:
            flash("Order not found", "error")
            return redirect(url_for('ordered_watches'))

        # Delete the order from the database
        db_facade.delete_order(order_id)

        flash("Rental deleted successfully", "success")
        return redirect(url_for('ordered_watches'))
    # If the request method is not POST, return a method not allowed error
    return "Method not allowed", 405


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/watches')
def watch_list():
    user_logged_in = 'user_id' in session
    user_is_admin = False
    if user_logged_in:
        # Fetch user details from session or database, assuming User model has an attribute is_admin
        user_id = session['user_id']
        user = db_facade.fetch_user_by_id(user_id)
        user_is_admin = user.is_admin if user else False

    # Fetch all watches using DatabaseFacade
    watches = db_facade.fetch_all_available_watches()

    return render_template('watch_list.html', watches=watches, user_logged_in=user_logged_in, user_is_admin=user_is_admin, title="Our watches - Watch Shop")


@app.route('/delete-watch/<int:watch_id>', methods=['POST'])
def delete_watch(watch_id):
    if request.method == 'POST':
        # Check if the user is logged in and is an admin
        if 'user_id' not in session:
            flash("You need to log in to perform this action", "error")
            return redirect(url_for('login'))

        user_id = session['user_id']
        user = db.session.query(User).get(user_id)

        if not user.is_admin:
            flash("You do not have permission to perform this action", "error")
            return redirect(url_for('watch_list'))

        # Delete the watch from the database
        db_facade.delete_watch_by_id(watch_id)

        flash("watch deleted successfully", "success")
        return redirect(url_for('watch_list'))

    # If the request method is not POST, return a method not allowed error
    return "Method not allowed", 405


@app.route('/add_watch')
def add_watch():
    user_logged_in = 'user_id' in session
    return render_template('add_watch.html', user_logged_in=user_logged_in, title="Add a watch")


@app.route('/watch-details/<int:watch_id>')
def watch_details(watch_id):
    user_logged_in = 'user_id' in session
    watch = db_facade.fetch_watch_by_id(watch_id)
    if watch:
        return render_template('watch_details.html', watch=watch, user_logged_in=user_logged_in)
    else:
        return render_template('404.html'), 404


@app.route('/photos/<path:filename>')
def serve_image(filename):
    return send_from_directory('photos', filename)


@app.route('/submit-new-watch', methods=['POST'])
def submit_new_watch():
    if request.method == 'POST':
        # Extract form data
        name = request.form.get('name')
        model = request.form.get('model')
        case_material = request.form.get('case_material')
        dial_color = request.form.get('dial_color')
        price = request.form.get('price')

        # Handle the file upload
        if 'image_url' in request.files:
            photo = request.files['image_url']
            if photo.filename != '':
                filename = secure_filename(photo.filename)
                photo_path = os.path.join('photos', filename)
                photo.save(photo_path)
                image_url = f"photos/{filename}"
            else:
                image_url = None
        else:
            image_url = None

        # Create the watch using the factory pattern
        new_watch = watch_factory.create(name, model, case_material, dial_color, price, image_url)

        # Add the new watch to the database
        db.session.add(new_watch)
        db.session.commit()

        subject.notify_observers({"watch_model": model})

        # Redirect to the main page or any other appropriate page
        return redirect('/')

    return "Method not allowed", 405


@app.route("/order/<int:watch_id>", methods=['GET', 'POST'])
def order_watch(watch_id):
    if 'user_id' not in session:
        flash("You need to log in to order a watch", "error")
        return redirect(url_for('login'))

    # Get the user ID from the session
    user_id = session['user_id']

    user = db.session.get(User, user_id)
    user_fullname = user.full_name

    # Get the watch object from the database
    watch = db.session.get(Watches, watch_id)

    # Check if the watch exists
    if not watch:
        flash("watch not found", "error")
        return redirect(url_for('main'))

    # Inside the order_watch route
    if request.method == 'POST':
        # Extract form data
        order_date = datetime.now()  # Assuming order date is current date/time
        selected_decorators = request.form.getlist('decorators')  # Assuming decorators are selected as checkboxes

        # Retrieve watch model and name from the database
        watch_model = watch.model
        watch_name = watch.name
        price = watch.price
        quantity = request.form.get('total_items')
        total_items = int(quantity)
        if (price * total_items)> 200:
            order_strategy = FreeShippingOrderStrategy()
        else:
            order_strategy = StandardOrderStrategy()

        # Calculate total price using selected pricing strategy
        total_price = order_strategy.calculate_order(total_items, price)

        # Apply decorator costs
        for decorator_name in selected_decorators:
            if decorator_name == 'SpareStrap':
                watch = SpareStrap(watch)
            elif decorator_name == 'Case':
                watch = Case(watch)
            elif decorator_name == 'GiftBox':
                watch = GiftBox(watch)

        # Create Orders object
        order = Orders(
            user_id=user_id,
            user_fullname=user_fullname,
            watch_id=watch_id,
            watch_model=watch_model,
            watch_name=watch_name,
            decorations=', '.join(selected_decorators),  # Join selected decorators into a string
            order_date=order_date,
            price=price,
            total_price=total_price,  # Update total price with decorators
            total_items=total_items
        )

        # Save the order object to the database
        db.session.add(order)
        db.session.commit()

        # Update the state of the watch to 'sold'
        watch.state = 'sold'
        db.session.commit()

        subject.notify_observers({"watch_model": watch_model, "user_id": user_id})

        # Redirect to the confirmation page
        flash("Order completed successful", "success")
        return redirect(url_for('main'))

    # Render the order form template
    return render_template('ordered_watches.html', watch=watch, title="")

if __name__ == '__main__':
    app.run(debug=True)
