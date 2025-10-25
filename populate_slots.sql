-- Script to populate the slots table with initial parking slot data
-- Run this script in MySQL Workbench to add 30 parking slots to your database

USE parking_management;

-- Clear existing slots
DELETE FROM slots;

-- Insert 30 slots (20 regular, 10 reserved)
-- Regular slots (A01-A20)
INSERT INTO slots (code, zone, level, status) VALUES
('A01', 'Zone A', 'Ground', 'available'),
('A02', 'Zone A', 'Ground', 'available'),
('A03', 'Zone A', 'Ground', 'available'),
('A04', 'Zone A', 'Ground', 'available'),
('A05', 'Zone A', 'Ground', 'available'),
('A06', 'Zone A', 'Ground', 'available'),
('A07', 'Zone A', 'Ground', 'available'),
('A08', 'Zone A', 'Ground', 'available'),
('A09', 'Zone A', 'Ground', 'available'),
('A10', 'Zone A', 'Ground', 'available'),
('A11', 'Zone A', 'Ground', 'available'),
('A12', 'Zone A', 'Ground', 'available'),
('A13', 'Zone A', 'Ground', 'available'),
('A14', 'Zone A', 'Ground', 'available'),
('A15', 'Zone A', 'Ground', 'available'),
('A16', 'Zone A', 'Ground', 'available'),
('A17', 'Zone A', 'Ground', 'available'),
('A18', 'Zone A', 'Ground', 'available'),
('A19', 'Zone A', 'Ground', 'available'),
('A20', 'Zone A', 'Ground', 'available');

-- Reserved slots (B01-B10)
INSERT INTO slots (code, zone, level, status) VALUES
('B01', 'Zone B', 'Ground', 'reserved'),
('B02', 'Zone B', 'Ground', 'reserved'),
('B03', 'Zone B', 'Ground', 'reserved'),
('B04', 'Zone B', 'Ground', 'reserved'),
('B05', 'Zone B', 'Ground', 'reserved'),
('B06', 'Zone B', 'Ground', 'reserved'),
('B07', 'Zone B', 'Ground', 'reserved'),
('B08', 'Zone B', 'Ground', 'reserved'),
('B09', 'Zone B', 'Ground', 'reserved'),
('B10', 'Zone B', 'Ground', 'reserved');

-- Verify the data
SELECT COUNT(*) as 'Total Slots' FROM slots;
SELECT zone, status, COUNT(*) as 'Count' FROM slots GROUP BY zone, status;
