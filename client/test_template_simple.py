#!/usr/bin/env python3
"""
Direct test of template rendering with debug info
"""
print("Testing dashboard template data flow...")

# Test 1: Check if the stats are being displayed with fallback values
test_stats = {
    'room_stats': {
        'total_rooms': 252,
        'occupied_rooms': 11,
        'available_rooms': 241,
        'occupancy_rate': 4.4
    },
    'user_stats': {
        'total_students': 17
    },
    'payment_stats': {
        'total_revenue': 30600000.0,
        'confirmed_payments': 25,
        'pending_payments': 3
    },
    'contract_stats': {
        'active_contracts': 18,
        'expiring_soon': 2
    },
    'maintenance_stats': {
        'pending_maintenance': 0,
        'in_progress_maintenance': 0
    }
}

print("Sample template expressions with test data:")
print(f"Total rooms: {test_stats.get('room_stats', {}).get('total_rooms', 0)}")
print(f"Occupied rooms: {test_stats.get('room_stats', {}).get('occupied_rooms', 0)}")
print(f"Available rooms: {test_stats.get('room_stats', {}).get('available_rooms', 0)}")
print(f"Total students: {test_stats.get('user_stats', {}).get('total_students', 0)}")
print(f"Total revenue: {'{:,.0f}'.format(test_stats.get('payment_stats', {}).get('total_revenue', 0))}đ")
print(f"Confirmed payments: {test_stats.get('payment_stats', {}).get('confirmed_payments', 0)}")
print(f"Pending payments: {test_stats.get('payment_stats', {}).get('pending_payments', 0)}")
print(f"Expiring contracts: {test_stats.get('contract_stats', {}).get('expiring_soon', 0)}")
print(f"Pending maintenance: {test_stats.get('maintenance_stats', {}).get('pending_maintenance', 0)}")

print("\nTemplate expressions should work correctly with this data structure.")
