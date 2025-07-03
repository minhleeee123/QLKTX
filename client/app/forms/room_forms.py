from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class RoomForm(FlaskForm):
    """Form for creating/editing rooms"""
    room_number = StringField('Số phòng', validators=[
        DataRequired(message='Số phòng là bắt buộc'),
        Length(min=1, max=10, message='Số phòng phải từ 1-10 ký tự')
    ])
    
    building_id = SelectField('Tòa nhà', validators=[
        DataRequired(message='Tòa nhà là bắt buộc')
    ], coerce=int)
    
    room_type_id = SelectField('Loại phòng', validators=[
        DataRequired(message='Loại phòng là bắt buộc')
    ], coerce=int)
    
    status = SelectField('Trạng thái', validators=[
        DataRequired(message='Trạng thái là bắt buộc')
    ], choices=[
        ('available', 'Có sẵn'),
        ('occupied', 'Đã có người ở'),
        ('pending_approval', 'Chờ duyệt'),
        ('maintenance', 'Bảo trì')
    ], default='available')
    
    current_occupancy = IntegerField('Số người hiện tại', validators=[
        NumberRange(min=0, message='Số người phải lớn hơn hoặc bằng 0')
    ], default=0)
    
    submit = SubmitField('Lưu')


class RoomSearchForm(FlaskForm):
    """Form for searching rooms"""
    search = StringField('Tìm kiếm', validators=[Optional()],
                        render_kw={"placeholder": "Tìm theo số phòng..."})
    
    building_id = SelectField('Tòa nhà', validators=[Optional()], coerce=int)
    
    room_type_id = SelectField('Loại phòng', validators=[Optional()], coerce=int)
    
    status = SelectField('Trạng thái', validators=[Optional()], choices=[
        ('', 'Tất cả'),
        ('available', 'Có sẵn'),
        ('occupied', 'Đã có người ở'),
        ('pending_approval', 'Chờ duyệt'),
        ('maintenance', 'Bảo trì')
    ], default='')
    
    submit = SubmitField('Tìm kiếm')


class BuildingForm(FlaskForm):
    """Form for creating/editing buildings"""
    building_name = StringField('Tên tòa nhà', validators=[
        DataRequired(message='Tên tòa nhà là bắt buộc'),
        Length(min=1, max=100, message='Tên tòa nhà phải từ 1-100 ký tự')
    ])
    
    submit = SubmitField('Lưu')


class RoomTypeForm(FlaskForm):
    """Form for creating/editing room types"""
    type_name = StringField('Tên loại phòng', validators=[
        DataRequired(message='Tên loại phòng là bắt buộc'),
        Length(min=1, max=100, message='Tên loại phòng phải từ 1-100 ký tự')
    ])
    
    capacity = IntegerField('Sức chứa', validators=[
        DataRequired(message='Sức chứa là bắt buộc'),
        NumberRange(min=1, message='Sức chứa phải lớn hơn 0')
    ])
    
    price = IntegerField('Giá phòng (VNĐ)', validators=[
        DataRequired(message='Giá phòng là bắt buộc'),
        NumberRange(min=0, message='Giá phòng không được âm')
    ])
    
    submit = SubmitField('Lưu')
