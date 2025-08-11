#!/usr/bin/env python3
"""
Simple test script to check dashboard API endpoints
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import User, Role, Room, Contract, Payment, Registration, MaintenanceRequest

def test_dashboard_stats():
    """Test the dashboard statistics calculation"""
    app = create_app()
    
    with app.app_context():
        try:
            # Test basic counts
            print("Testing basic model counts...")
            
            # Room statistics
            total_rooms = Room.query.count()
            print(f"Total rooms: {total_rooms}")
            
            occupied_rooms = Room.query.filter(Room.current_occupancy > 0).count()
            print(f"Occupied rooms (current_occupancy > 0): {occupied_rooms}")
            
            available_rooms = Room.query.filter_by(status='available').count()
            print(f"Available rooms: {available_rooms}")
            
            maintenance_rooms = Room.query.filter_by(status='maintenance').count()
            print(f"Maintenance rooms: {maintenance_rooms}")
            
            # User statistics
            total_students = User.query.join(Role).filter(Role.role_name == 'student').count()
            print(f"Total students: {total_students}")
            
            total_staff = User.query.join(Role).filter(Role.role_name == 'staff').count()
            print(f"Total staff: {total_staff}")
            
            total_admins = User.query.join(Role).filter(Role.role_name == 'admin').count()
            print(f"Total admins: {total_admins}")
            
            # Contract statistics
            total_contracts = Contract.query.count()
            print(f"Total contracts: {total_contracts}")
            
            active_contracts = Contract.query.filter(
                Contract.start_date <= db.func.current_date(),
                Contract.end_date >= db.func.current_date()
            ).count()
            print(f"Active contracts: {active_contracts}")
            
            # Test room-contract join through registration
            print("\nTesting room-contract join through registration...")
            rooms_with_contracts = db.session.query(Room.room_id).join(
                Registration, Room.room_id == Registration.room_id
            ).join(
                Contract, Registration.registration_id == Contract.registration_id
            ).filter(
                Contract.start_date <= db.func.current_date(),
                Contract.end_date >= db.func.current_date()
            ).distinct().count()
            print(f"Rooms with active contracts: {rooms_with_contracts}")
            
            print("\n✅ Dashboard statistics test completed successfully!")
            
        except Exception as e:
            print(f"❌ Error testing dashboard stats: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_dashboard_stats()
