-- Migration script to add contract_history table
-- Run this script to add the new contract history functionality

CREATE TABLE IF NOT EXISTS contract_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    action VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (contract_id) REFERENCES contracts (contract_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_contract_history_contract_id ON contract_history(contract_id);
CREATE INDEX IF NOT EXISTS idx_contract_history_user_id ON contract_history(user_id);
CREATE INDEX IF NOT EXISTS idx_contract_history_created_at ON contract_history(created_at);
CREATE INDEX IF NOT EXISTS idx_contract_history_action ON contract_history(action);

-- Add any missing indexes on existing tables for better performance
CREATE INDEX IF NOT EXISTS idx_contracts_start_date ON contracts(start_date);
CREATE INDEX IF NOT EXISTS idx_contracts_end_date ON contracts(end_date);
CREATE INDEX IF NOT EXISTS idx_contracts_created_at ON contracts(created_at);

CREATE INDEX IF NOT EXISTS idx_payments_contract_id ON payments(contract_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_payment_date ON payments(payment_date);

-- Insert sample history data for existing contracts (optional)
INSERT INTO contract_history (contract_id, user_id, action, new_value, notes, created_at)
SELECT 
    c.contract_id,
    1, -- Assuming admin user has ID 1, adjust as needed
    'created',
    json_object(
        'contract_code', c.contract_code,
        'start_date', c.start_date,
        'end_date', c.end_date,
        'registration_id', c.registration_id
    ),
    'Hợp đồng được tạo (dữ liệu khôi phục)',
    c.created_at
FROM contracts c
WHERE NOT EXISTS (
    SELECT 1 FROM contract_history ch 
    WHERE ch.contract_id = c.contract_id AND ch.action = 'created'
);
