import re

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional,
    ValidationError,
)


class UserForm(FlaskForm):
    """Form for creating/editing users"""
    full_name = StringField('Họ và tên', validators=[
        DataRequired(message='Họ và tên là bắt buộc'),
        Length(min=2, max=100, message='Họ và tên phải từ 2-100 ký tự')
    ])

    email = StringField('Email', validators=[
        DataRequired(message='Email là bắt buộc'),
        Email(message='Email không hợp lệ')
    ])

    phone_number = StringField('Số điện thoại', validators=[
        Optional(),
        Length(min=10, max=11, message='Số điện thoại phải từ 10-11 số')
    ])

    gender = SelectField(
        "Giới tính",
        choices=[("male", "Nam"), ("female", "Nữ"), ("other", "Khác")],
        validators=[DataRequired(message="Giới tính là bắt buộc")],
    )

    student_id = StringField('Mã sinh viên', validators=[
        Optional(),
        Length(max=20, message='Mã sinh viên không được quá 20 ký tự')
    ])

    role_name = SelectField('Vai trò', choices=[
        ('admin', 'Quản trị viên'),
        ('management', 'Quản lý'),
        ('student', 'Sinh viên'),
        ('staff', 'Nhân viên')
    ], validators=[DataRequired(message='Vai trò là bắt buộc')])

    is_active = BooleanField('Kích hoạt', default=True)

    # Password fields - only for create user
    password = PasswordField('Mật khẩu', validators=[
        Optional(),
        Length(min=6, message='Mật khẩu phải ít nhất 6 ký tự')
    ])

    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[
        Optional(),
        EqualTo('password', message='Mật khẩu xác nhận không khớp')
    ])

    submit = SubmitField('Lưu')

    def __init__(self, is_create=True, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.is_create = is_create

        # Make password required only for create form
        if is_create:
            self.password.validators = [
                DataRequired(message='Mật khẩu là bắt buộc'),
                Length(min=6, message='Mật khẩu phải ít nhất 6 ký tự')
            ]
            self.confirm_password.validators = [
                DataRequired(message='Xác nhận mật khẩu là bắt buộc'),
                EqualTo('password', message='Mật khẩu xác nhận không khớp')
            ]

    def validate_phone_number(self, phone_number):
        """Validate phone number format"""
        if phone_number.data and not re.match(r'^[0-9]{10,11}$', phone_number.data):
            raise ValidationError('Số điện thoại chỉ được chứa số và có 10-11 chữ số')

    def validate_student_id(self, student_id):
        """Validate student code for student role"""
        if self.role_name.data == 'student' and not student_id.data:
            raise ValidationError('Mã sinh viên là bắt buộc cho sinh viên')


class UserSearchForm(FlaskForm):
    """Form for searching users"""
    search = StringField('Tìm kiếm', validators=[Optional()], 
                        render_kw={"placeholder": "Tìm theo tên, email, mã sinh viên..."})
    
    role = SelectField('Lọc theo vai trò', choices=[
        ('', 'Tất cả'),
        ('admin', 'Quản trị viên'),
        ('management', 'Quản lý'),
        ('student', 'Sinh viên'),
        ('staff', 'Nhân viên')
    ], default='')
    
    submit = SubmitField('Tìm kiếm')
