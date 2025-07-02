# trong một script seed.py hoặc trong flask shell
from app import create_app
from app.extensions import db
from app.models import Role, User, Building, RoomType, Room
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Seed Roles
    print("Seeding Roles...")
    for name in ['Admin','Management','Student','MaintenanceStaff']:
        if not Role.query.filter_by(role_name=name).first():
            db.session.add(Role(role_name=name))
    db.session.commit()
    print("✓ Roles seeded successfully")
    
    # Seed Users
    print("Seeding Users...")
    
    # Lấy các role đã tạo
    admin_role = Role.query.filter_by(role_name='Admin').first()
    management_role = Role.query.filter_by(role_name='Management').first()
    student_role = Role.query.filter_by(role_name='Student').first()
    maintenance_role = Role.query.filter_by(role_name='MaintenanceStaff').first()
    
    # Tạo users mẫu
    users_data = [
        # Admin users
        {
            'role': admin_role,
            'full_name': 'Nguyễn Văn Admin',
            'email': 'admin@qlktx.edu.vn',
            'password': 'admin123',
            'phone_number': '0901234567',
            'student_code': None
        },
        
        # Management users
        {
            'role': management_role,
            'full_name': 'Trần Thị Quản Lý',
            'email': 'quanly@qlktx.edu.vn',
            'password': 'quanly123',
            'phone_number': '0901234568',
            'student_code': None
        },
        {
            'role': management_role,
            'full_name': 'Lê Văn Giám Đốc',
            'email': 'giamdoc@qlktx.edu.vn',
            'password': 'giamdoc123',
            'phone_number': '0901234569',
            'student_code': None
        },
        
        # Maintenance Staff
        {
            'role': maintenance_role,
            'full_name': 'Phạm Văn Sửa Chữa',
            'email': 'baotri1@qlktx.edu.vn',
            'password': 'baotri123',
            'phone_number': '0901234570',
            'student_code': None
        },
        {
            'role': maintenance_role,
            'full_name': 'Hoàng Thị Bảo Trì',
            'email': 'baotri2@qlktx.edu.vn',
            'password': 'baotri123',
            'phone_number': '0901234571',
            'student_code': None
        },
        
        # Students
        {
            'role': student_role,
            'full_name': 'Nguyễn Văn Sinh Viên',
            'email': 'sinhvien1@student.edu.vn',
            'password': 'sinhvien123',
            'phone_number': '0901234572',
            'student_code': 'SV001'
        },
        {
            'role': student_role,
            'full_name': 'Trần Thị Học Sinh',
            'email': 'sinhvien2@student.edu.vn',
            'password': 'sinhvien123',
            'phone_number': '0901234573',
            'student_code': 'SV002'
        },
        {
            'role': student_role,
            'full_name': 'Lê Minh Đức',
            'email': 'sinhvien3@student.edu.vn',
            'password': 'sinhvien123',
            'phone_number': '0901234574',
            'student_code': 'SV003'
        },
        {
            'role': student_role,
            'full_name': 'Phạm Thị Mai',
            'email': 'sinhvien4@student.edu.vn',
            'password': 'sinhvien123',
            'phone_number': '0901234575',
            'student_code': 'SV004'
        },
        {
            'role': student_role,
            'full_name': 'Vũ Văn Nam',
            'email': 'sinhvien5@student.edu.vn',
            'password': 'sinhvien123',
            'phone_number': '0901234576',
            'student_code': 'SV005'
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
                student_code=user_data['student_code'],
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
    
    print("\n🎉 All data seeded successfully!")
    print(f"Total Roles: {Role.query.count()}")
    print(f"Total Users: {User.query.count()}")
    print(f"  - Admin: {User.query.join(Role).filter(Role.role_name == 'Admin').count()}")
    print(f"  - Management: {User.query.join(Role).filter(Role.role_name == 'Management').count()}")
    print(f"  - Students: {User.query.join(Role).filter(Role.role_name == 'Student').count()}")
    print(f"  - Maintenance Staff: {User.query.join(Role).filter(Role.role_name == 'MaintenanceStaff').count()}")
    print(f"Total Buildings: {Building.query.count()}")
    print(f"Total Room Types: {RoomType.query.count()}")
    print(f"Total Rooms: {Room.query.count()}")


