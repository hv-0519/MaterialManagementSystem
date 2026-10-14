-- schema.sql  —  Material Management System (mms_prototype)
-- Re-runnable: drops existing tables, then recreates all 10.
-- Load with:  mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS mms_prototype
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mms_prototype;

DROP TABLE IF EXISTS conversion_transaction_lines;
DROP TABLE IF EXISTS conversion_transactions;
DROP TABLE IF EXISTS packing_rules;
DROP TABLE IF EXISTS bom_components;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS material_receiving;
DROP TABLE IF EXISTS purchase_orders;
DROP TABLE IF EXISTS material_requests;
DROP TABLE IF EXISTS materials;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    username  VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE materials (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    material_name  VARCHAR(150) NOT NULL,
    unit           VARCHAR(30)  NOT NULL
) ENGINE=InnoDB;

CREATE TABLE material_requests (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    request_no       VARCHAR(20)  NOT NULL UNIQUE,
    material_id      INT          NOT NULL,
    quantity         DECIMAL(12,2) NOT NULL,
    request_type     VARCHAR(20)  NOT NULL,
    required_date    DATE         NULL,
    remarks          TEXT         NULL,
    status           VARCHAR(30)  NOT NULL DEFAULT 'PENDING_VERIFICATION',
    created_by       INT          NOT NULL,
    verified_by      INT          NULL,
    verified_at      DATETIME     NULL,
    approval_status  VARCHAR(20)  NOT NULL DEFAULT 'PENDING',
    approved_by      INT          NULL,
    approved_at      DATETIME     NULL,
    approval_reason  TEXT         NULL,
    created_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE purchase_orders (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    po_number               VARCHAR(20) NOT NULL UNIQUE,
    request_id              INT         NOT NULL,
    status                  VARCHAR(30) NOT NULL DEFAULT 'PO_CREATED',
    expected_receiving_date DATE        NULL,
    created_at              DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE material_receiving (
    id                 INT AUTO_INCREMENT PRIMARY KEY,
    po_id              INT          NOT NULL,
    ordered_quantity   DECIMAL(12,2) NOT NULL,
    received_quantity  DECIMAL(12,2) NOT NULL DEFAULT 0,
    status             VARCHAR(20)  NOT NULL DEFAULT 'PENDING',
    receiving_date     DATETIME     NULL
) ENGINE=InnoDB;

CREATE TABLE inventory (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    material_id          INT          NOT NULL UNIQUE,
    available_quantity   DECIMAL(12,2) NOT NULL DEFAULT 0,
    incoming_quantity    DECIMAL(12,2) NOT NULL DEFAULT 0,
    low_stock_threshold  DECIMAL(12,2) NOT NULL DEFAULT 10
) ENGINE=InnoDB;

CREATE TABLE bom_components (
    id                    INT AUTO_INCREMENT PRIMARY KEY,
    output_material_id    INT          NOT NULL,
    component_material_id INT          NOT NULL,
    qty_per_unit          DECIMAL(12,3) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE packing_rules (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    output_material_id  INT NOT NULL,
    package_material_id INT NOT NULL,
    units_per_package   INT NOT NULL
) ENGINE=InnoDB;

CREATE TABLE conversion_transactions (
    id                 INT AUTO_INCREMENT PRIMARY KEY,
    output_material_id INT          NOT NULL,
    output_qty         DECIMAL(12,2) NOT NULL,
    created_by         INT          NOT NULL,
    created_at         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE conversion_transaction_lines (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id  INT          NOT NULL,
    material_id     INT          NOT NULL,
    qty_change      DECIMAL(12,2) NOT NULL,
    line_type       VARCHAR(20)  NOT NULL
) ENGINE=InnoDB;
