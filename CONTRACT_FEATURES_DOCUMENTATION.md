# Contract Management Features - Implementation Documentation

## Overview
This document describes the enhanced contract management features implemented for the QLKTX (Dormitory Management System).

## New Features Implemented

### 1. Contract Renewal System
- **API Endpoint**: `POST /contracts/{id}/renew`
- **Functionality**: Allows administrators to extend contract duration
- **Parameters**: 
  - `renewal_months`: Number of months to extend (1-60)
- **Features**:
  - Automatic date calculation
  - Smart handling of expired contracts
  - Audit trail creation

### 2. Contract Termination System
- **API Endpoint**: `POST /contracts/{id}/terminate`
- **Functionality**: Early termination of active contracts
- **Parameters**: 
  - `reason`: Required termination reason
- **Features**:
  - Updates room availability
  - Decreases occupancy count
  - Creates termination history record

### 3. Expiring Contracts Management
- **API Endpoint**: `GET /contracts/expiring-soon`
- **Web Interface**: `/contracts/expiring-soon`
- **Functionality**: Lists contracts expiring within specified timeframe
- **Parameters**: 
  - `days`: Number of days ahead to check (default: 30)
- **Features**:
  - Urgency-based color coding
  - Quick contact information
  - Bulk renewal capabilities

### 4. Contract History & Audit Trail
- **Model**: `ContractHistory`
- **API Endpoint**: `GET /contracts/{id}/history`
- **Functionality**: Complete audit trail of all contract changes
- **Tracked Actions**:
  - Contract creation
  - Updates to end dates
  - Renewals with duration
  - Terminations with reasons
- **Features**:
  - JSON-based change tracking
  - User attribution
  - Timestamp tracking
  - Export to Excel

### 5. Enhanced Statistics
- **Updated Statistics Include**:
  - Total contracts count
  - Active contracts count
  - Expired contracts count
  - **NEW**: Expiring soon count (within 30 days)
  - Total revenue from confirmed payments

### 6. Excel Export System
- **Contracts Export**: `GET /contracts/export`
- **History Export**: `GET /contracts/{id}/export-history`
- **Features**:
  - Complete contract information
  - Student and room details
  - Payment summaries
  - Status categorization
  - History timeline with change details

### 7. Enhanced User Interface
- **New Templates**:
  - `contracts/expiring.html`: Dedicated expiring contracts view
  - Enhanced contract list with new action buttons
- **New JavaScript Functions**:
  - `renewContract()`: Interactive renewal dialog
  - `terminateContract()`: Termination confirmation
  - Enhanced statistics loading
- **UI Improvements**:
  - Color-coded urgency badges
  - Responsive action buttons
  - Quick contact links
  - Export functionality

## Database Schema Changes

### New Table: `contract_history`
```sql
CREATE TABLE contract_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    action VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contract_id) REFERENCES contracts (contract_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);
```

### New Indexes for Performance
- `idx_contract_history_contract_id`
- `idx_contract_history_created_at`
- `idx_contracts_end_date`
- `idx_payments_status`

## API Endpoints Summary

### New Endpoints
1. `POST /contracts/{id}/renew` - Renew contract
2. `POST /contracts/{id}/terminate` - Terminate contract early
3. `GET /contracts/expiring-soon` - Get expiring contracts
4. `GET /contracts/{id}/history` - Get contract history
5. `GET /contracts/export` - Export all contracts to Excel
6. `GET /contracts/{id}/export-history` - Export contract history

### Enhanced Endpoints
1. `GET /contracts/statistics` - Now includes expiring_soon count

## Security & Access Control
- All new endpoints require authentication (`@jwt_required()`)
- Most administrative functions require admin/management roles (`@require_role()`)
- Contract history maintains user attribution for accountability

## Dependencies Added
- `XlsxWriter==3.1.9` - For Excel export functionality

## Installation & Deployment

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Database Migration
```bash
# Execute the SQL migration script
sqlite3 your_database.db < migrations/add_contract_history.sql
```

### 3. Update Application
- Restart the Flask server
- The new features will be immediately available

## Usage Examples

### Renewing a Contract
```javascript
// Frontend JavaScript
fetch(`/contracts/123/renew`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify({
        renewal_months: 12
    })
});
```

### Getting Expiring Contracts
```python
# Python API call
GET /contracts/expiring-soon?days=15
```

### Exporting Data
```javascript
// Frontend download
const link = document.createElement('a');
link.href = '/api/contracts/export';
link.download = 'contracts.xlsx';
link.click();
```

## Business Benefits

1. **Proactive Management**: Early warning system for expiring contracts
2. **Audit Compliance**: Complete change tracking for accountability
3. **Operational Efficiency**: Bulk operations and automated workflows
4. **Data Insights**: Enhanced reporting and export capabilities
5. **User Experience**: Intuitive interface with visual indicators

## Future Enhancements

1. **Email Notifications**: Automatic reminders for expiring contracts
2. **Bulk Operations**: Multi-select renewal/termination
3. **Advanced Analytics**: Trend analysis and predictive insights
4. **Mobile Responsiveness**: Enhanced mobile interface
5. **Integration**: Connect with payment systems and student information systems

## Technical Notes

- All date calculations handle edge cases (leap years, month-end dates)
- Excel exports are memory-efficient for large datasets
- History records use JSON for flexible change tracking
- Real-time statistics are calculated on-demand for accuracy

## Support & Maintenance

For technical support or feature requests, please refer to the project documentation or contact the development team.
