USE parking_management;

-- First, let's see what data we have to work with
SELECT '=== CHECKING EXISTING DATA ===' AS Info;

-- Check users
SELECT 'Users in database:' AS Info, COUNT(*) AS Count FROM users;
SELECT id, full_name, role FROM users ORDER BY id;

-- Check vehicles  
SELECT 'Vehicles in database:' AS Info, COUNT(*) AS Count FROM vehicles;
SELECT id, plate_number, user_id FROM vehicles ORDER BY id;

-- Check if flags table is empty
SELECT 'Current flags:' AS Info, COUNT(*) AS Count FROM flags;

-- Clear existing flags (if any)
DELETE FROM flags;

-- Insert sample flags using existing data
-- We'll use the first available guard and vehicle IDs

-- Get the first guard user ID
SET @guard_id = (SELECT id FROM users WHERE role='guard' LIMIT 1);
SET @admin_id = (SELECT id FROM users WHERE role='admin' LIMIT 1);
SET @vehicle_id = (SELECT id FROM vehicles LIMIT 1);

-- Insert open flags
INSERT INTO flags (vehicle_id, raised_by_guard_id, reason, status, created_at) VALUES
(@vehicle_id, @guard_id, 'no_slots', 'open', '2025-10-25 18:04:17'),
(@vehicle_id, @guard_id, 'mismatch', 'open', '2025-10-25 17:04:17');

-- Insert resolved flags
INSERT INTO flags (vehicle_id, raised_by_guard_id, reason, status, created_at, closed_at, closed_by_admin_id, resolution_note) VALUES
(@vehicle_id, @guard_id, 'suspicious', 'closed', '2025-10-24 16:30:00', '2025-10-24 17:00:00', @admin_id, 'Verified with security footage. Vehicle belongs to authorized visitor.'),
(@vehicle_id, @guard_id, 'other', 'closed', '2025-10-24 14:15:00', '2025-10-24 15:30:00', @admin_id, 'Issue resolved by manual slot allocation.');

-- Verify the inserted data
SELECT '=== RESULTS ===' AS Info;
SELECT 'Total Flags:' AS Description, COUNT(*) AS Count FROM flags;
SELECT status, COUNT(*) AS Count FROM flags GROUP BY status;

-- Show all flags with details
SELECT 
    f.id,
    f.reason,
    f.status,
    f.created_at,
    u.full_name as raised_by,
    v.plate_number as vehicle,
    f.resolution_note
FROM flags f
JOIN users u ON u.id = f.raised_by_guard_id
LEFT JOIN vehicles v ON v.id = f.vehicle_id
ORDER BY f.created_at DESC;
