# trong một script seed.py hoặc trong flask shell
from app import create_app
from app.extensions import db
from app.models import Role, User, Building, RoomType, Room, Registration, Contract, Payment, MaintenanceRequest
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
import random

app = create_app()
with app.app_context():
    # Seed Roles
    print("Seeding Roles...")
    for name in ["admin", "management", "student", "staff"]:
        if not Role.query.filter_by(role_name=name).first():
            db.session.add(Role(role_name=name))
    db.session.commit()
    print("✓ Roles seeded successfully")

    # Seed Users
    print("Seeding Users...")

    # Lấy các role đã tạo
    admin_role = Role.query.filter_by(role_name='admin').first()
    management_role = Role.query.filter_by(role_name='management').first()
    student_role = Role.query.filter_by(role_name='student').first()
    maintenance_role = Role.query.filter_by(role_name="staff").first()

    # Tạo users mẫu
    users_data = [
        # Admin users
        {
            'role': admin_role,
            'full_name': 'Nguyễn Văn Admin',
            'email': 'admin@qlktx.edu.vn',
            'password': 'admin123',
            'phone_number': '0901234567',
            'student_id': None
        },
        
        # Management users
        {
            'role': management_role,
            'full_name': 'Trần Thị Quản Lý',
            'email': 'quanly@qlktx.edu.vn',
            'password': 'quanly123',
            'phone_number': '0901234568',
            'student_id': None
        },
        {
            'role': management_role,
            'full_name': 'Lê Văn Giám Đốc',
            'email': 'giamdoc@qlktx.edu.vn',
            'password': 'giamdoc123',
            'phone_number': '0901234569',
            'student_id': None
        },
        
        # Maintenance Staff
        {
            'role': maintenance_role,
            'full_name': 'Phạm Văn Sửa Chữa',
            'email': 'baotri1@qlktx.edu.vn',
            'password': 'baotri123',
            'phone_number': '0901234570',
            'student_id': None
        },
        {
            'role': maintenance_role,
            'full_name': 'Hoàng Thị Bảo Trì',
            'email': 'baotri2@qlktx.edu.vn',
            'password': 'baotri123',
            'phone_number': '0901234571',
            'student_id': None
        },
        
        # Students
        {
            'role': student_role,
            'full_name': 'Nguyễn Văn Sinh Viên',
            'email': 'sinhvien1@student.edu.vn',
            'password': 'sinhvien123',
            'phone_number': '0901234572',
            'student_id': 'SV001'
        },
        {
            'role': student_role,
            'full_name': 'Trần Thị Học Sinh',
            'email': 'sinhvien2@student.edu.vn',
            'password': 'sinhvien123',
            'phone_number': '0901234573',
            'student_id': 'SV002'
        },
        {
            'role': student_role,
            'full_name': 'Lê Minh Đức',
            'email': 'sinhvien3@student.edu.vn',
            'password': 'sinhvien123',
            'phone_number': '0901234574',
            'student_id': 'SV003'
        },
        {
            'role': student_role,
            'full_name': 'Phạm Thị Mai',
            'email': 'sinhvien4@student.edu.vn',
            'password': 'sinhvien123',
            'phone_number': '0901234575',
            'student_id': 'SV004'
        },
        {
            'role': student_role,
            'full_name': 'Vũ Văn Nam',
            'email': 'sinhvien5@student.edu.vn',
            'password': 'sinhvien123',
            'phone_number': '0901234576',
            'student_id': 'SV005'
        }
    ]

    for user_data in users_data:
        # Kiểm tra user đã tồn tại chưa
        if not User.query.filter_by(email=user_data['email']).first():
            user = User(
                role_id=user_data['role'].role_id,
                full_name=user_data['full_name'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                phone_number=user_data['phone_number'],
                student_id=user_data['student_id'],
                is_active=True
            )
            db.session.add(user)

    db.session.commit()
    print("✓ Users seeded successfully")

    # Seed Buildings
    print("Seeding Buildings...")
    buildings_data = [
        'Tòa A - Khu Nam',
        'Tòa B - Khu Nam', 
        'Tòa C - Khu Bắc',
        'Tòa D - Khu Bắc',
        'Tòa E - Khu Trung tâm'
    ]

    for building_name in buildings_data:
        if not Building.query.filter_by(building_name=building_name).first():
            db.session.add(Building(building_name=building_name))
    db.session.commit()
    print("✓ Buildings seeded successfully")

    # Seed Room Types
    print("Seeding Room Types...")
    room_types_data = [
        {'type_name': 'Phòng 4 người', 'capacity': 4, 'price': 1500000},
        {'type_name': 'Phòng 6 người', 'capacity': 6, 'price': 1200000},
        {'type_name': 'Phòng 8 người', 'capacity': 8, 'price': 1000000},
        {'type_name': 'Phòng dịch vụ', 'capacity': 2, 'price': 2500000}
    ]

    for room_type_data in room_types_data:
        if not RoomType.query.filter_by(type_name=room_type_data['type_name']).first():
            room_type = RoomType(
                type_name=room_type_data['type_name'],
                capacity=room_type_data['capacity'],
                price=room_type_data['price']
            )
            db.session.add(room_type)
    db.session.commit()
    print("✓ Room Types seeded successfully")

    # Seed Rooms
    print("Seeding Rooms...")
    buildings = Building.query.all()
    room_types = RoomType.query.all()

    if buildings and room_types:
        # Tạo phòng cho mỗi tòa nhà
        for building in buildings:
            for floor in range(1, 6):  # 5 tầng mỗi tòa
                for room_num in range(1, 11):  # 10 phòng mỗi tầng
                    room_number = f"{floor:01d}{room_num:02d}"  # Format: 101, 102, ..., 510

                    # Kiểm tra phòng đã tồn tại chưa
                    existing_room = Room.query.filter_by(
                        room_number=room_number, 
                        building_id=building.building_id
                    ).first()

                    if not existing_room:
                        # Phân bổ loại phòng ngẫu nhiên (với bias cho phòng 6 người)
                        if room_num <= 6:  # 60% phòng 6 người
                            room_type = next((rt for rt in room_types if rt.type_name == 'Phòng 6 người'), room_types[0])
                        elif room_num <= 8:  # 20% phòng 4 người
                            room_type = next((rt for rt in room_types if rt.type_name == 'Phòng 4 người'), room_types[0])
                        elif room_num <= 9:  # 10% phòng 8 người
                            room_type = next((rt for rt in room_types if rt.type_name == 'Phòng 8 người'), room_types[0])
                        else:  # 10% phòng dịch vụ
                            room_type = next((rt for rt in room_types if rt.type_name == 'Phòng dịch vụ'), room_types[0])

                        room = Room(
                            room_number=room_number,
                            building_id=building.building_id,
                            room_type_id=room_type.room_type_id,
                            status='available',
                            current_occupancy=0
                        )
                        db.session.add(room)

        db.session.commit()
        print("✓ Rooms seeded successfully")

    # Seed Registrations
    print("Seeding Registrations...")
    students = User.query.join(Role).filter(Role.role_name == 'student').all()
    available_rooms = Room.query.filter_by(status='available').limit(10).all()  # Lấy 10 phòng đầu tiên

    if students and available_rooms:
        registration_statuses = ['pending', 'approved', 'rejected']

        for i, student in enumerate(students):
            if i < len(available_rooms):  # Đảm bảo có đủ phòng
                room = available_rooms[i]

                # Kiểm tra đã có registration chưa
                existing_registration = Registration.query.filter_by(
                    student_id=student.user_id,
                    room_id=room.room_id
                ).first()

                if not existing_registration:
                    # 70% approved, 20% pending, 10% rejected
                    if i < len(students) * 0.7:
                        status = 'approved'
                    elif i < len(students) * 0.9:
                        status = 'pending'
                    else:
                        status = 'rejected'

                    registration = Registration(
                        student_id=student.user_id,
                        room_id=room.room_id,
                        status=status,
                        registration_date=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                    )
                    db.session.add(registration)

                    # Cập nhật trạng thái phòng nếu approved
                    if status == 'approved':
                        room.current_occupancy += 1
                        if room.current_occupancy >= room.room_type.capacity:
                            room.status = 'occupied'

    db.session.commit()
    print("✓ Registrations seeded successfully")

    # Seed Contracts
    print("Seeding Contracts...")
    approved_registrations = Registration.query.filter_by(status='approved').all()

    for registration in approved_registrations:
        # Kiểm tra đã có contract chưa
        if not Contract.query.filter_by(registration_id=registration.registration_id).first():
            start_date = date.today() - timedelta(days=random.randint(0, 60))
            end_date = start_date + timedelta(days=365)  # Hợp đồng 1 năm

            contract = Contract(
                registration_id=registration.registration_id,
                contract_code=f"HD{registration.registration_id:04d}",
                start_date=start_date,
                end_date=end_date,
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.session.add(contract)

    db.session.commit()
    print("✓ Contracts seeded successfully")

    # Seed Payments
    print("Seeding Payments...")
    contracts = Contract.query.all()
    management_users = User.query.join(Role).filter(Role.role_name == 'management').all()

    for contract in contracts:
        room_price = contract.registration.room.room_type.price

        # Tạo 1-3 khoản thanh toán cho mỗi hợp đồng
        num_payments = random.randint(1, 3)

        for i in range(num_payments):
            # Kiểm tra đã có payment chưa
            existing_payments = Payment.query.filter_by(contract_id=contract.contract_id).count()

            if existing_payments < num_payments:
                # 80% confirmed, 15% pending, 5% failed
                rand = random.random()
                if rand < 0.8:
                    status = 'confirmed'
                    confirmed_by = random.choice(management_users) if management_users else None
                elif rand < 0.95:
                    status = 'pending'
                    confirmed_by = None
                else:
                    status = 'failed'
                    confirmed_by = None

                payment_methods = ['bank_transfer', 'cash']
                payment_method = random.choice(payment_methods)

                payment = Payment(
                    contract_id=contract.contract_id,
                    amount=room_price,
                    payment_date=datetime.utcnow() - timedelta(days=random.randint(0, 90)),
                    payment_method=payment_method,
                    status=status,
                    proof_image_url=f"https://example.com/proof_{contract.contract_id}_{i+1}.jpg" if payment_method == 'bank_transfer' else None,
                    confirmed_by_user_id=confirmed_by.user_id if confirmed_by else None
                )
                db.session.add(payment)

    db.session.commit()
    print("✓ Payments seeded successfully")

    # Seed Maintenance Requests
    print("Seeding Maintenance Requests...")
    students = User.query.join(Role).filter(Role.role_name == 'student').all()
    maintenance_staff = User.query.join(Role).filter(Role.role_name == "staff").all()
    occupied_rooms = Room.query.filter_by(status='occupied').all()

    if students and occupied_rooms:
        # Danh sách các vấn đề bảo trì thường gặp
        maintenance_issues = [
            {
                'title': 'Điều hòa không hoạt động',
                'description': 'Điều hòa trong phòng không thể bật được, có thể do hỏng điều khiển hoặc máy nén.'
            },
            {
                'title': 'Vòi nước bị rò rỉ',
                'description': 'Vòi nước trong phòng tắm bị rò rỉ liên tục, cần thay thế hoặc sửa chữa.'
            },
            {
                'title': 'Đèn trong phòng hỏng',
                'description': 'Đèn LED trong phòng ngủ bị chập chờn và không sáng đều.'
            },
            {
                'title': 'Ổ khóa cửa bị kẹt',
                'description': 'Ổ khóa cửa phòng bị kẹt, khó mở và đóng cửa.'
            },
            {
                'title': 'Quạt trần kêu to',
                'description': 'Quạt trần trong phòng kêu to bất thường, có thể do hỏng động cơ.'
            },
            {
                'title': 'Toilet bị tắc',
                'description': 'Toilet trong phòng tắm bị tắc, nước không thể xả xuống.'
            },
            {
                'title': 'Cửa sổ không đóng được',
                'description': 'Cửa sổ phòng bị lệch khung, không thể đóng chặt.'
            },
            {
                'title': 'Ổ cắm điện hỏng',
                'description': 'Một số ổ cắm điện trong phòng không hoạt động.'
            }
        ]

        # Tạo 10-15 yêu cầu bảo trì
        for i in range(random.randint(10, 15)):
            student = random.choice(students)
            room = random.choice(occupied_rooms)
            issue = random.choice(maintenance_issues)

            # Kiểm tra đã có yêu cầu tương tự chưa
            existing_request = MaintenanceRequest.query.filter_by(
                student_id=student.user_id,
                room_id=room.room_id,
                title=issue['title']
            ).first()

            if not existing_request:
                # Phân bổ trạng thái: 30% pending, 25% assigned, 25% in_progress, 15% completed, 5% cancelled
                rand = random.random()
                if rand < 0.3:
                    status = 'pending'
                    assigned_to = None
                    completed_date = None
                elif rand < 0.55:
                    status = 'assigned'
                    assigned_to = random.choice(maintenance_staff) if maintenance_staff else None
                    completed_date = None
                elif rand < 0.8:
                    status = 'in_progress'
                    assigned_to = random.choice(maintenance_staff) if maintenance_staff else None
                    completed_date = None
                elif rand < 0.95:
                    status = 'completed'
                    assigned_to = random.choice(maintenance_staff) if maintenance_staff else None
                    completed_date = datetime.utcnow() - timedelta(days=random.randint(1, 7))
                else:
                    status = 'cancelled'
                    assigned_to = None
                    completed_date = None

                maintenance_request = MaintenanceRequest(
                    student_id=student.user_id,
                    room_id=room.room_id,
                    title=issue['title'],
                    description=issue['description'],
                    image_url=f"https://example.com/maintenance_photo_{i+1}.jpg" if random.random() > 0.3 else None,
                    status=status,
                    request_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                    assigned_to_user_id=assigned_to.user_id if assigned_to else None,
                    completed_date=completed_date
                )
                db.session.add(maintenance_request)

    db.session.commit()
    print("✓ Maintenance Requests seeded successfully")

    print("\n🎉 All data seeded successfully!")
    print("\n🎉 All data seeded successfully!")
    print(f"Total Roles: {Role.query.count()}")
    print(f"Total Users: {User.query.count()}")
    print(f"  - Admin: {User.query.join(Role).filter(Role.role_name == 'admin').count()}")
    print(f"  - Management: {User.query.join(Role).filter(Role.role_name == 'management').count()}")
    print(f"  - Students: {User.query.join(Role).filter(Role.role_name == 'student').count()}")
    print(
        f"  - Maintenance Staff: {User.query.join(Role).filter(Role.role_name == 'staff').count()}"
    )
    print(f"Total Buildings: {Building.query.count()}")
    print(f"Total Room Types: {RoomType.query.count()}")
    print(f"Total Rooms: {Room.query.count()}")
    print(f"  - Available: {Room.query.filter_by(status='available').count()}")
    print(f"  - Occupied: {Room.query.filter_by(status='occupied').count()}")
    print(f"Total Registrations: {Registration.query.count()}")
    print(f"  - Pending: {Registration.query.filter_by(status='pending').count()}")
    print(f"  - Approved: {Registration.query.filter_by(status='approved').count()}")
    print(f"  - Rejected: {Registration.query.filter_by(status='rejected').count()}")
    print(f"Total Contracts: {Contract.query.count()}")
    print(f"Total Payments: {Payment.query.count()}")
    print(f"  - Pending: {Payment.query.filter_by(status='pending').count()}")
    print(f"  - Confirmed: {Payment.query.filter_by(status='confirmed').count()}")
    print(f"  - Failed: {Payment.query.filter_by(status='failed').count()}")
    print(f"Total Maintenance Requests: {MaintenanceRequest.query.count()}")
    print(f"  - Pending: {MaintenanceRequest.query.filter_by(status='pending').count()}")
    print(f"  - Assigned: {MaintenanceRequest.query.filter_by(status='assigned').count()}")
    print(f"  - In Progress: {MaintenanceRequest.query.filter_by(status='in_progress').count()}")
    print(f"  - Completed: {MaintenanceRequest.query.filter_by(status='completed').count()}")
    print(f"  - Cancelled: {MaintenanceRequest.query.filter_by(status='cancelled').count()}")
