from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TextAreaField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from datetime import date


class ContractSearchForm(FlaskForm):
    search = StringField(
        'Tìm kiếm',
        validators=[Optional(), Length(max=100)],
        render_kw={
            'placeholder': 'Nhập mã hợp đồng, tên sinh viên...',
            'class': 'form-control'
        }
    )
    
    status = SelectField(
        'Trạng thái',
        choices=[
            ('', 'Tất cả trạng thái'),
            ('active', 'Đang hiệu lực'),
            ('expired', 'Đã hết hạn'),
            ('pending', 'Chờ xử lý')
        ],
        default='',
        render_kw={'class': 'form-select'}
    )
    
    submit = SubmitField('Tìm kiếm', render_kw={'class': 'btn btn-primary'})


class ContractUpdateForm(FlaskForm):
    contract_id = HiddenField()
    
    end_date = DateField(
        'Ngày kết thúc',
        validators=[DataRequired(message='Ngày kết thúc là bắt buộc')],
        render_kw={
            'class': 'form-control',
            'min': date.today().strftime('%Y-%m-%d')
        }
    )
    
    notes = TextAreaField(
        'Ghi chú',
        validators=[Optional(), Length(max=500)],
        render_kw={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Nhập ghi chú về việc cập nhật hợp đồng...'
        }
    )
    
    submit = SubmitField('Cập nhật hợp đồng', render_kw={'class': 'btn btn-primary'})
