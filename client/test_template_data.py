#!/usr/bin/env python3
"""
Test script to check if dashboard template variables are being passed correctly
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.dashboard_service import dashboard_service
import json

def test_template_data():
    """Test the exact data that would be passed to the admin template"""
    print("=== Testing Dashboard Template Data ===\n")
    
    try:
        # Simulate the exact logic from the admin dashboard route
        stats_result = dashboard_service.get_admin_dashboard_stats()
        recent_activities_result = dashboard_service.get_recent_activities(10)
        alerts_result = dashboard_service.get_dashboard_alerts()

        print("1. Raw API Responses:")
        print(f"   Stats success: {stats_result.get('success') if isinstance(stats_result, dict) else 'Not a dict'}")
        print(f"   Activities success: {recent_activities_result.get('success') if isinstance(recent_activities_result, dict) else 'Not a dict'}")
        print(f"   Alerts success: {alerts_result.get('success') if isinstance(alerts_result, dict) else 'Not a dict'}")

        # Extract data exactly like the dashboard blueprint does
        dashboard_stats = (
            stats_result.get("data", {}).get("stats", {})
            if isinstance(stats_result, dict) and stats_result.get("success")
            else {}
        )
        recent_activities = (
            recent_activities_result.get("data", {}).get("activities", [])
            if isinstance(recent_activities_result, dict) and recent_activities_result.get("success")
            else []
        )
        alerts = (
            alerts_result.get("data", {}).get("alerts", [])
            if isinstance(alerts_result, dict) and alerts_result.get("success")
            else []
        )

        print("\n2. Extracted Template Variables:")
        print(f"   dashboard_stats type: {type(dashboard_stats)}")
        print(f"   dashboard_stats empty: {len(dashboard_stats) == 0}")
        
        if dashboard_stats:
            print(f"   Available stats keys: {list(dashboard_stats.keys())}")
            
            # Test specific stats that should appear in template
            print("\n3. Statistics Values:")
            room_stats = dashboard_stats.get('room_stats', {})
            print(f"   Total rooms: {room_stats.get('total_rooms', 'NOT FOUND')}")
            print(f"   Occupied rooms: {room_stats.get('occupied_rooms', 'NOT FOUND')}")
            print(f"   Available rooms: {room_stats.get('available_rooms', 'NOT FOUND')}")
            print(f"   Occupancy rate: {room_stats.get('occupancy_rate', 'NOT FOUND')}")
            
            user_stats = dashboard_stats.get('user_stats', {})
            print(f"   Total students: {user_stats.get('total_students', 'NOT FOUND')}")
            
            payment_stats = dashboard_stats.get('payment_stats', {})
            print(f"   Total revenue: {payment_stats.get('total_revenue', 'NOT FOUND')}")
            print(f"   Confirmed payments: {payment_stats.get('confirmed_payments', 'NOT FOUND')}")
            print(f"   Pending payments: {payment_stats.get('pending_payments', 'NOT FOUND')}")
            
            contract_stats = dashboard_stats.get('contract_stats', {})
            print(f"   Active contracts: {contract_stats.get('active_contracts', 'NOT FOUND')}")
            print(f"   Expiring soon: {contract_stats.get('expiring_soon', 'NOT FOUND')}")
            
            maintenance_stats = dashboard_stats.get('maintenance_stats', {})
            print(f"   Pending maintenance: {maintenance_stats.get('pending_maintenance', 'NOT FOUND')}")
            print(f"   In progress maintenance: {maintenance_stats.get('in_progress_maintenance', 'NOT FOUND')}")
            
        else:
            print("   ❌ No dashboard stats data available!")
            
        print(f"\n4. Activities and Alerts:")
        print(f"   Recent activities count: {len(recent_activities)}")
        print(f"   Alerts count: {len(alerts)}")

        # Test template expression simulation
        print("\n5. Template Expression Tests:")
        total_revenue = dashboard_stats.get('payment_stats', {}).get('total_revenue', 0)
        print(f"   Revenue format test: {'{:,.0f}'.format(total_revenue)}đ")
        
        print("\n✅ Template data test completed!")

    except Exception as e:
        print(f"❌ Error in template data test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_template_data()
