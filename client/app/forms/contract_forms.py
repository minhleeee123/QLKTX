from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    HiddenField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional


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
        "Trạng thái",
        choices=[
            ("", "Tất cả trạng thái"),
            ("active", "Đang hiệu lực"),
            ("expired", "Đã hết hạn"),
            ("expiring_soon", "Sắp hết hạn"),
            ("pending", "Chờ xử lý"),
        ],
        default="",
        render_kw={"class": "form-select"},
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


class ContractRenewalForm(FlaskForm):
    contract_id = HiddenField()

    renewal_months = IntegerField(
        "Số tháng gia hạn",
        validators=[
            DataRequired(message="Số tháng gia hạn là bắt buộc"),
            NumberRange(min=1, max=60, message="Số tháng gia hạn phải từ 1 đến 60"),
        ],
        default=12,
        render_kw={"class": "form-control", "min": "1", "max": "60"},
    )

    notes = TextAreaField(
        "Lý do gia hạn",
        validators=[Optional(), Length(max=500)],
        render_kw={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Nhập lý do gia hạn hợp đồng...",
        },
    )

    submit = SubmitField("Gia hạn hợp đồng", render_kw={"class": "btn btn-warning"})


class ContractTerminationForm(FlaskForm):
    contract_id = HiddenField()

    reason = TextAreaField(
        "Lý do chấm dứt",
        validators=[
            DataRequired(message="Lý do chấm dứt là bắt buộc"),
            Length(max=500),
        ],
        render_kw={
            "class": "form-control",
            "rows": 4,
            "placeholder": "Nhập lý do chấm dứt hợp đồng...",
        },
    )

    submit = SubmitField("Chấm dứt hợp đồng", render_kw={"class": "btn btn-danger"})
