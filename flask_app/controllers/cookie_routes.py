from flask import Flask, render_template, session, redirect, request
from flask_app import app
from flask_app.models import cookie_order
from flask_app.models import user_model

@app.route("/cookies")
def index():
    #render home page/ display all the orders
    # orders = cookie_order.Cookie_order.get_all()
    user_data={
        "id": session['user_id']
    }
    logged_in_user= user_model.User.get_one_user(user_data)
    users= user_model.User.get_all_users_with_orders()
    return render_template("cookies.html", users=users, current_user= logged_in_user)

@app.route("/cookies/new")
def new_page():
    # render new order form
    return render_template("new_order.html")

@app.route("/cookies/edit/<int:cookie_id>")
def edit_page(cookie_id):
    # render edit order page
    order = cookie_order.Cookie_order.get_by_id(cookie_id)
    return render_template("edit_order.html", order = order)

# post new order, redirect home
@app.route("/cookies", methods=["POST"])
def create_cookie():
    cookie_order.Cookie_order = request.form

    if not cookie_order.Cookie_order.is_valid(cookie_order):
        return redirect("/cookies/new")

    cookie_order.Cookie_order.create(cookie_order)
    
    return redirect("/")

# posts the edited form
@app.route("/cookies/edit/<int:cookie_id>", methods=["POST"])
def update_cookie(cookie_id):
    cookie_order = request.form

    if not cookie_order.Cookie_order.is_valid(cookie_order):
        return redirect(f"/cookies/edit/{cookie_id}")

    cookie_order.Cookie_order.update(cookie_order)
    
    return redirect("/")

@app.route('/cookies/destroy/<int:cookie_id>', methods=["POST"])
def delete_order(cookie_id):
    cookie_order.Cookie_order.destroy()
    return redirect('/cookies')