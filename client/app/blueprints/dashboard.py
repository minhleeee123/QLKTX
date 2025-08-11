import json

from app.services.auth_service import auth_service
from app.services.dashboard_service import dashboard_service
from flask import Blueprint, jsonify, redirect, render_template, url_for
from flask_login import current_user, login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    """Main dashboard page - redirects based on user role"""
    if current_user.role == "admin" or current_user.role == "management":
        return redirect(url_for("dashboard.admin"))
    elif current_user.role == "staff":
        return redirect(url_for("dashboard.staff"))
    elif current_user.role == "student":
        return redirect(url_for("dashboard.student"))
    else:
        return redirect(url_for("auth.logout"))


@dashboard_bp.route("/admin")
@login_required
def admin():
    """Admin dashboard"""
    if not auth_service.is_admin() and not auth_service.is_management():
        return redirect(url_for("dashboard.index"))

    user = auth_service.get_current_user()

    # Get dashboard statistics
    try:
        stats_result = dashboard_service.get_admin_dashboard_stats()
        recent_activities_result = dashboard_service.get_recent_activities(10)
        alerts_result = dashboard_service.get_dashboard_alerts()

        dashboard_stats = (
            stats_result.get("data", {}).get("stats", {})
            if isinstance(stats_result, dict) and stats_result.get("success")
            else {}
        )
        recent_activities = (
            recent_activities_result.get("data", {}).get("activities", [])
            if isinstance(recent_activities_result, dict)
            and recent_activities_result.get("success")
            else []
        )
        alerts = (
            alerts_result.get("data", {}).get("alerts", [])
            if isinstance(alerts_result, dict) and alerts_result.get("success")
            else []
        )

    except Exception as e:
        # Fallback to empty data if API fails
        print(f"Error fetching dashboard data: {e}")  # Keep error logging
        dashboard_stats = {}
        recent_activities = []
        alerts = []

    return render_template(
        "dashboard/admin.html",
        user=user,
        stats=dashboard_stats,
        recent_activities=recent_activities,
        alerts=alerts,
    )


@dashboard_bp.route("/api/recent-activities")
@login_required
def recent_activities():
    """API endpoint for refreshing recent activities"""
    if not auth_service.is_admin() and not auth_service.is_management():
        return jsonify({"success": False, "message": "Access denied"})

    try:
        activities_result = dashboard_service.get_recent_activities(10)

        if activities_result.get("success"):
            return jsonify(
                {
                    "success": True,
                    "activities": activities_result.get("data", {}).get(
                        "activities", []
                    ),
                }
            )
        else:
            return jsonify(
                {
                    "success": False,
                    "message": "Failed to fetch activities",
                    "activities": [],
                }
            )
    except Exception as e:
        return jsonify(
            {"success": False, "message": f"Error: {str(e)}", "activities": []}
        )


@dashboard_bp.route("/api/admin-stats")
@login_required
def admin_stats():
    """API endpoint for refreshing dashboard statistics"""
    if not auth_service.is_admin() and not auth_service.is_management():
        return jsonify({"success": False, "message": "Access denied"})

    try:
        stats_result = dashboard_service.get_admin_dashboard_stats()

        if stats_result.get("success"):
            return jsonify(stats_result)
        else:
            return jsonify(
                {"success": False, "message": "Failed to fetch statistics", "data": {}}
            )
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}", "data": {}})


@dashboard_bp.route("/staff")
@login_required
def staff():
    """Staff dashboard"""
    if not auth_service.is_staff():
        return redirect(url_for("dashboard.index"))

    user = auth_service.get_current_user()
    return render_template("dashboard/staff.html", user=user)


@dashboard_bp.route("/student")
@login_required
def student():
    """Student dashboard"""
    if not auth_service.is_student():
        return redirect(url_for("dashboard.index"))

    user = auth_service.get_current_user()

    # Get comprehensive dashboard data
    dashboard_data = dashboard_service.get_student_dashboard_data(user.id)
    recent_activities = dashboard_service.get_recent_activities(
        10
    )  # Use limit instead of user.id

    return render_template(
        "dashboard/student.html",
        user=user,
        dashboard_data=dashboard_data,
        recent_activities=recent_activities,
    )
