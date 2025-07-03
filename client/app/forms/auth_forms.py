from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
import re

class LoginForm(FlaskForm):
    """Login form"""
    email = StringField('Email', validators=[
        DataRequired(message='Email là bắt buộc'),
        Email(message='Email không hợp lệ')
    ])
    password = PasswordField('Mật khẩu', validators=[
        DataRequired(message='Mật khẩu là bắt buộc')
    ])
    remember_me = BooleanField('Ghi nhớ đăng nhập')
    submit = SubmitField('Đăng nhập')

class RegisterForm(FlaskForm):
    """Registration form"""
    full_name = StringField('Họ và tên', validators=[
        DataRequired(message='Họ và tên là bắt buộc'),
        Length(min=2, max=100, message='Họ và tên phải từ 2-100 ký tự')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email là bắt buộc'),
        Email(message='Email không hợp lệ')
    ])
    phone = StringField('Số điện thoại', validators=[
        DataRequired(message='Số điện thoại là bắt buộc'),
        Length(min=10, max=11, message='Số điện thoại phải từ 10-11 số')
    ])
    student_id = StringField('Mã sinh viên')
    
    password = PasswordField('Mật khẩu', validators=[
        DataRequired(message='Mật khẩu là bắt buộc'),
        Length(min=6, message='Mật khẩu phải ít nhất 6 ký tự')
    ])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[
        DataRequired(message='Xác nhận mật khẩu là bắt buộc'),
        EqualTo('password', message='Mật khẩu xác nhận không khớp')
    ])
    
    role = SelectField('Vai trò', choices=[
        ('student', 'Sinh viên'),
        ('staff', 'Nhân viên')
    ], default='student')
    
    submit = SubmitField('Đăng ký')
    
    def validate_phone(self, phone):
        """Validate phone number format"""
        if not re.match(r'^[0-9]{10,11}$', phone.data):
            raise ValidationError('Số điện thoại chỉ được chứa số và có 10-11 chữ số')
    
    def validate_student_id(self, student_id):
        """Validate student ID for student role"""
        if self.role.data == 'student' and not student_id.data:
            raise ValidationError('Mã sinh viên là bắt buộc cho sinh viên')

class ChangePasswordForm(FlaskForm):
    """Change password form"""
    current_password = PasswordField('Mật khẩu hiện tại', validators=[
        DataRequired(message='Mật khẩu hiện tại là bắt buộc')
    ])
    new_password = PasswordField('Mật khẩu mới', validators=[
        DataRequired(message='Mật khẩu mới là bắt buộc'),
        Length(min=6, message='Mật khẩu phải ít nhất 6 ký tự')
    ])
    confirm_password = PasswordField('Xác nhận mật khẩu mới', validators=[
        DataRequired(message='Xác nhận mật khẩu là bắt buộc'),
        EqualTo('new_password', message='Mật khẩu xác nhận không khớp')
    ])
    submit = SubmitField('Đổi mật khẩu')
