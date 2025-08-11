import io
from datetime import date, datetime

from app.extensions import db
from app.models import Contract, ContractHistory, Payment
from flask import make_response

# Note: xlsxwriter needs to be installed: pip install xlsxwriter
try:
    import xlsxwriter
    XLSXWRITER_AVAILABLE = True
except ImportError:
    XLSXWRITER_AVAILABLE = False


class ContractReportService:
    
    @staticmethod
    def generate_contracts_excel_report():
        """Generate Excel report of all contracts"""
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Add formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter'
        })
        
        number_format = workbook.add_format({
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '#,##0'
        })
        
        date_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': 'dd/mm/yyyy'
        })
        
        # Contracts Sheet
        contracts_sheet = workbook.add_worksheet('Hợp đồng')
        contracts_sheet.set_column('A:A', 12)  # Contract Code
        contracts_sheet.set_column('B:B', 20)  # Student Name
        contracts_sheet.set_column('C:C', 15)  # Student ID
        contracts_sheet.set_column('D:D', 25)  # Email
        contracts_sheet.set_column('E:E', 15)  # Phone
        contracts_sheet.set_column('F:F', 10)  # Room
        contracts_sheet.set_column('G:G', 15)  # Building
        contracts_sheet.set_column('H:H', 12)  # Start Date
        contracts_sheet.set_column('I:I', 12)  # End Date
        contracts_sheet.set_column('J:J', 12)  # Status
        contracts_sheet.set_column('K:K', 15)  # Total Paid
        contracts_sheet.set_column('L:L', 12)  # Days Remaining
        
        # Headers
        headers = [
            'Mã hợp đồng', 'Tên sinh viên', 'MSSV', 'Email', 'Điện thoại',
            'Phòng', 'Tòa nhà', 'Ngày bắt đầu', 'Ngày kết thúc', 'Trạng thái',
            'Tổng thanh toán', 'Số ngày còn lại'
        ]
        
        for col, header in enumerate(headers):
            contracts_sheet.write(0, col, header, header_format)
        
        # Data
        contracts = Contract.query.join(Contract.registration).all()
        
        for row, contract in enumerate(contracts, start=1):
            student = contract.registration.student
            room = contract.registration.room
            
            # Determine status
            if contract.is_expired:
                status = 'Hết hạn'
            elif contract.is_active:
                if contract.days_remaining <= 30:
                    status = 'Sắp hết hạn'
                else:
                    status = 'Đang hiệu lực'
            else:
                status = 'Chưa bắt đầu'
            
            contracts_sheet.write(row, 0, contract.contract_code, cell_format)
            contracts_sheet.write(row, 1, student.full_name, cell_format)
            contracts_sheet.write(row, 2, student.student_id, cell_format)
            contracts_sheet.write(row, 3, student.email, cell_format)
            contracts_sheet.write(row, 4, student.phone_number or '', cell_format)
            contracts_sheet.write(row, 5, room.room_number, cell_format)
            contracts_sheet.write(row, 6, room.building.building_name, cell_format)
            contracts_sheet.write(row, 7, contract.start_date, date_format)
            contracts_sheet.write(row, 8, contract.end_date, date_format)
            contracts_sheet.write(row, 9, status, cell_format)
            contracts_sheet.write(row, 10, float(contract.total_paid), number_format)
            contracts_sheet.write(row, 11, contract.days_remaining if not contract.is_expired else 0, number_format)
        
        # Statistics Sheet
        stats_sheet = workbook.add_worksheet('Thống kê')
        stats_sheet.set_column('A:A', 25)
        stats_sheet.set_column('B:B', 15)
        
        stats_sheet.write(0, 0, 'Thống kê hợp đồng', header_format)
        stats_sheet.write(0, 1, 'Số lượng', header_format)
        
        total_contracts = Contract.query.count()
        active_contracts = Contract.query.filter(
            Contract.start_date <= date.today(),
            Contract.end_date >= date.today()
        ).count()
        expired_contracts = Contract.query.filter(
            Contract.end_date < date.today()
        ).count()
        
        stats_data = [
            ('Tổng số hợp đồng', total_contracts),
            ('Hợp đồng đang hiệu lực', active_contracts),
            ('Hợp đồng đã hết hạn', expired_contracts),
            ('Tổng doanh thu (VND)', float(
                db.session.query(db.func.sum(Payment.amount))
                .filter(Payment.status == 'confirmed')
                .scalar() or 0
            ))
        ]
        
        for row, (label, value) in enumerate(stats_data, start=1):
            stats_sheet.write(row, 0, label, cell_format)
            if 'doanh thu' in label.lower():
                stats_sheet.write(row, 1, value, number_format)
            else:
                stats_sheet.write(row, 1, value, number_format)
        
        workbook.close()
        
        output.seek(0)
        
        response = make_response(output.read())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=hop_dong_{date.today().strftime("%Y%m%d")}.xlsx'
        
        return response
    
    @staticmethod
    def generate_contract_history_report(contract_id):
        """Generate history report for a specific contract"""
        
        contract = Contract.query.get(contract_id)
        if not contract:
            return None
            
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Add formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter'
        })
        
        date_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': 'dd/mm/yyyy hh:mm'
        })
        
        # History Sheet
        history_sheet = workbook.add_worksheet('Lịch sử hợp đồng')
        history_sheet.set_column('A:A', 15)  # Date
        history_sheet.set_column('B:B', 15)  # Action
        history_sheet.set_column('C:C', 20)  # User
        history_sheet.set_column('D:D', 50)  # Notes
        history_sheet.set_column('E:E', 30)  # Old Value
        history_sheet.set_column('F:F', 30)  # New Value
        
        # Headers
        headers = ['Thời gian', 'Hành động', 'Người thực hiện', 'Ghi chú', 'Giá trị cũ', 'Giá trị mới']
        
        for col, header in enumerate(headers):
            history_sheet.write(0, col, header, header_format)
        
        # Data
        history_records = ContractHistory.query.filter_by(contract_id=contract_id)\
                                              .order_by(ContractHistory.created_at.desc())\
                                              .all()
        
        import json
        
        for row, history in enumerate(history_records, start=1):
            history_sheet.write(row, 0, history.created_at, date_format)
            history_sheet.write(row, 1, history.action_display, cell_format)
            history_sheet.write(row, 2, history.user.full_name, cell_format)
            history_sheet.write(row, 3, history.notes or '', cell_format)
            
            # Format old and new values
            old_value = json.loads(history.old_value) if history.old_value else {}
            new_value = json.loads(history.new_value) if history.new_value else {}
            
            old_str = ', '.join([f"{k}: {v}" for k, v in old_value.items()]) if old_value else ''
            new_str = ', '.join([f"{k}: {v}" for k, v in new_value.items()]) if new_value else ''
            
            history_sheet.write(row, 4, old_str, cell_format)
            history_sheet.write(row, 5, new_str, cell_format)
        
        workbook.close()
        
        output.seek(0)
        
        response = make_response(output.read())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=lich_su_hop_dong_{contract.contract_code}_{date.today().strftime("%Y%m%d")}.xlsx'
        
        return response
        return response
