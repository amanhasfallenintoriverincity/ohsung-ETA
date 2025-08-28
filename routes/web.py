from flask import Blueprint, render_template

web_bp = Blueprint('web', __name__)

@web_bp.route("/login_page")
def login_page():
    return render_template("login.html")

@web_bp.route("/post_page")
def post_page():
    return render_template("post_form.html")

@web_bp.route("/posts_page")
def posts_page():
    return render_template("post_list.html")

@web_bp.route("/posts/<int:post_id>/page")
def post_detail_page(post_id):
    return render_template("post_detail.html", post_id=post_id)
