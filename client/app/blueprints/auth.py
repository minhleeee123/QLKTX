from app.forms.auth_forms import ChangePasswordForm, LoginForm, RegisterForm
from app.services.auth_service import auth_service
from app.utils.decorators import anonymous_required, login_required
from flask import (
    Blueprint,
    flash,
    json,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
@anonymous_required
def login():
    """Login page"""
    form = LoginForm()

    if form.validate_on_submit():
        response = auth_service.login(form.email.data, form.password.data)
        print("Response at login:")  # Uncomment for debugging
        print(
            json.dumps(response, indent=2, ensure_ascii=False)
        )  # Uncomment for debugging
        if response["success"]:
            flash("Đăng nhập thành công!", "success")

            # Redirect to next page or dashboard
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for("dashboard.index"))
        else:
            error_msg = response.get("error", {})
            flash(error_msg, "error")
            return redirect(url_for("auth.login"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
@anonymous_required
def register():
    """Registration page"""
    form = RegisterForm()

    if form.validate_on_submit():
        user_data = {
            "full_name": form.full_name.data,
            "email": form.email.data,
            "phone": form.phone.data,
            "student_id": form.student_id.data if form.role.data == "student" else None,
            "password": form.password.data,
            "role": form.role.data,
        }

        response = auth_service.register(user_data)

        print("Response at register:")  # Uncomment for debugging
        print(
            json.dumps(response, indent=2, ensure_ascii=False)
        )  # Uncomment for debugging

        if response["success"]:
            flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
            return redirect(url_for("auth.login"))
        else:
            error_msg = response.get("message", {})
            flash(error_msg, "error")

    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """Logout user"""
    auth_service.logout()
    flash("Đã đăng xuất thành công!", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change password page"""
    form = ChangePasswordForm()

    if form.validate_on_submit():
        response = auth_service.change_password(
            form.current_password.data,
            form.new_password.data,
            form.confirm_password.data,
        )

        if response["success"]:
            flash("Đổi mật khẩu thành công!", "success")
            return redirect(url_for("dashboard.index"))
        else:
            error_msg = response.get("error", {})
            flash(error_msg, "error")

    return render_template("auth/change_password.html", form=form)
