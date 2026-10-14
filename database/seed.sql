-- seed.sql  —  Material Management System (mms_prototype)
-- Run AFTER schema.sql.  Load with:  mysql -u root -p mms_prototype < seed.sql
-- Re-runnable: clears seeded rows, resets auto-increment, re-inserts.

USE mms_prototype;

DELETE FROM conversion_transaction_lines;
DELETE FROM conversion_transactions;
DELETE FROM packing_rules;
DELETE FROM bom_components;
DELETE FROM inventory;
DELETE FROM material_receiving;
DELETE FROM purchase_orders;
DELETE FROM material_requests;
DELETE FROM materials;
DELETE FROM users;

ALTER TABLE materials AUTO_INCREMENT = 1;
ALTER TABLE users     AUTO_INCREMENT = 1;

-- User (id = 1 is hardcoded in every create/verify/approve/convert endpoint)
INSERT INTO users (id, username) VALUES
(1, 'het');

-- Materials (explicit ids so BOM / inventory can reference them)
--   1 Bob Liquid (Ltr) = bulk input
--   2 Can-5L     (Nos) = produced output
--   3 Sticker    (Nos) = BOM component
--   4 Cartoon    (Nos) = packaging
INSERT INTO materials (id, material_name, unit) VALUES
(1, 'Bob Liquid', 'Ltr'),
(2, 'Can-5L',     'Nos'),
(3, 'Sticker',    'Nos'),
(4, 'Cartoon',    'Nos');

-- Starting stock (Can-5L seeded at 0: it is produced, not stocked up front)
INSERT INTO inventory (material_id, available_quantity, incoming_quantity) VALUES
(1, 500, 0),
(2, 0,   0),
(3, 200, 0),
(4, 50,  0);

-- Recipe for Can-5L (output_material_id = 2)
--   BOM:  1 Can needs 5 Ltr Bob Liquid + 2 Stickers
--   Pack: every 4 Cans need 1 Cartoon (remainder stays unpackaged)
INSERT INTO bom_components (output_material_id, component_material_id, qty_per_unit) VALUES
(2, 1, 5),
(2, 3, 2);

INSERT INTO packing_rules (output_material_id, package_material_id, units_per_package) VALUES
(2, 4, 4);
