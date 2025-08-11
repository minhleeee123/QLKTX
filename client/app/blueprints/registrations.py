from app.services.registration_service import registration_service
from app.utils.api_response import APIResponse
from app.utils.decorators import admin_required
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required

# Blueprint registration
registrations_bp = Blueprint('registrations', __name__, url_prefix='/registrations')


@registrations_bp.route('/')
@login_required
@admin_required
def list_registrations():
    """List all registrations with filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        status = request.args.get('status')
        per_page = request.args.get('per_page', 20, type=int)

        response = registration_service.get_registrations(
            page=page,
            per_page=per_page,
            status=status
        )

        if not response.get('success'):
            flash(f'Lỗi khi tải danh sách đăng ký: {response.get("message", "")}', 'danger')
            registrations_data = {'registrations': [], 'pagination': {}}
        else:
            registrations_data = response.get('data', {})

        return render_template(
            'registrations/list.html',
            registrations=registrations_data.get('registrations', []),
            pagination=registrations_data.get('pagination', {}),
            current_page=page,
            status_filter=status,
            per_page=per_page,
            title='Quản lý đăng ký phòng'
        )

    except Exception as e:
        flash(f'Lỗi khi tải danh sách đăng ký: {str(e)}', 'danger')
        return render_template(
            'registrations/list.html',
            registrations=[],
            pagination={},
            current_page=1,
            status_filter=None,
            per_page=20,
            title='Quản lý đăng ký phòng'
        )


@registrations_bp.route('/<int:registration_id>')
@login_required
@admin_required
def view_registration(registration_id):
    """View registration details"""
    try:
        response = registration_service.get_registration(registration_id)

        if not response.get('success'):
            flash(f'Lỗi khi tải thông tin đăng ký: {response.get("message", "")}', 'danger')
            return redirect(url_for('registrations.list_registrations'))

        registration = response.get('data', {}).get('registration', {})

        return render_template(
            'registrations/detail.html',
            registration=registration,
            title=f'Chi tiết đăng ký #{registration_id}'
        )

    except Exception as e:
        flash(f'Lỗi khi tải thông tin đăng ký: {str(e)}', 'danger')
        return redirect(url_for('registrations.list_registrations'))


@registrations_bp.route('/<int:registration_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_registration(registration_id):
    """Approve a registration"""
    try:
        response = registration_service.approve_registration(registration_id)

        if response.get('success'):
            return APIResponse.success(
                message=response.get('message', 'Duyệt đơn thành công!')
            )
        else:
            return APIResponse.error(
                response.get('message', 'Có lỗi xảy ra khi duyệt đơn'),
                response.get('status_code', 400)
            )

    except Exception as e:
        return APIResponse.error(f'Lỗi khi duyệt đơn: {str(e)}', 500)


@registrations_bp.route('/<int:registration_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_registration(registration_id):
    """Reject a registration"""
    try:
        response = registration_service.reject_registration(registration_id)

        if response.get('success'):
            return APIResponse.success(
                message=response.get('message', 'Từ chối đơn thành công!')
            )
        else:
            return APIResponse.error(
                response.get('message', 'Có lỗi xảy ra khi từ chối đơn'),
                response.get('status_code', 400)
            )

    except Exception as e:
        return APIResponse.error(f'Lỗi khi từ chối đơn: {str(e)}', 500)
