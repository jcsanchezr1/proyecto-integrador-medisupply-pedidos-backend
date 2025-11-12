-- Script SQL para generar datos de prueba para el reporte de Top Productos
-- Este script inserta pedidos con diferentes productos y cantidades
-- para probar el endpoint /orders/reports/top-products
--
-- IMPORTANTE: Este script asume que los productos con IDs 1-15 existen en el servicio de inventarios
-- Si no existen, el reporte mostrará "Producto no disponible" para esos productos

-- Limpiar datos existentes (opcional, descomentar si se desea limpiar)
-- DELETE FROM order_items;
-- DELETE FROM orders;

-- Insertar pedidos con diferentes fechas y productos
INSERT INTO orders (order_number, client_id, vendor_id, status, total_amount, scheduled_delivery_date, assigned_truck, created_at, updated_at) 
VALUES 
-- Pedidos para Producto 1 (será el más vendido: 250 unidades)
('PED-20251015-00001', '82c22166-173c-4bd3-a582-b67d5eb2ce7a', NULL, 'Entregado', 5000.00, '2025-10-20 10:00:00', 'CAM-001', '2025-10-15 08:00:00', '2025-10-15 08:00:00'),
('PED-20251016-00002', '82c22166-173c-4bd3-a582-b67d5eb2ce7a', NULL, 'Entregado', 3000.00, '2025-10-21 14:00:00', 'CAM-002', '2025-10-16 09:00:00', '2025-10-16 09:00:00'),
('PED-20251017-00003', '18b913f3-22bd-43fa-a791-462a114b844d', NULL, 'Entregado', 4500.00, '2025-10-22 11:00:00', 'CAM-001', '2025-10-17 10:00:00', '2025-10-17 10:00:00'),
('PED-20251018-00004', '18b913f3-22bd-43fa-a791-462a114b844d', NULL, 'Entregado', 6000.00, '2025-10-23 15:00:00', 'CAM-003', '2025-10-18 08:30:00', '2025-10-18 08:30:00'),
('PED-20251019-00005', 'c9dd4ad6-6184-4f76-ab2c-c09755be8a25', NULL, 'Entregado', 3500.00, '2025-10-24 09:00:00', 'CAM-002', '2025-10-19 11:00:00', '2025-10-19 11:00:00'),

-- Pedidos para Producto 2 (segundo más vendido: 180 unidades)
('PED-20251020-00006', '82c22166-173c-4bd3-a582-b67d5eb2ce7a', NULL, 'Entregado', 7200.00, '2025-10-25 10:00:00', 'CAM-001', '2025-10-20 08:00:00', '2025-10-20 08:00:00'),
('PED-20251021-00007', '18b913f3-22bd-43fa-a791-462a114b844d', NULL, 'Entregado', 5400.00, '2025-10-26 14:00:00', 'CAM-002', '2025-10-21 09:00:00', '2025-10-21 09:00:00'),
('PED-20251022-00008', 'c9dd4ad6-6184-4f76-ab2c-c09755be8a25', NULL, 'Entregado', 3600.00, '2025-10-27 11:00:00', 'CAM-003', '2025-10-22 10:00:00', '2025-10-22 10:00:00'),

-- Pedidos para Producto 3 (tercero más vendido: 150 unidades)
('PED-20251023-00009', '82c22166-173c-4bd3-a582-b67d5eb2ce7a', NULL, 'Entregado', 4500.00, '2025-10-28 15:00:00', 'CAM-001', '2025-10-23 08:30:00', '2025-10-23 08:30:00'),
('PED-20251024-00010', '18b913f3-22bd-43fa-a791-462a114b844d', NULL, 'Entregado', 6000.00, '2025-10-29 09:00:00', 'CAM-002', '2025-10-24 11:00:00', '2025-10-24 11:00:00'),
('PED-20251025-00011', 'c9dd4ad6-6184-4f76-ab2c-c09755be8a25', NULL, 'Entregado', 4500.00, '2025-10-30 10:00:00', 'CAM-003', '2025-10-25 12:00:00', '2025-10-25 12:00:00'),

-- Pedidos para Productos 4-10
('PED-20251026-00012', '82c22166-173c-4bd3-a582-b67d5eb2ce7a', NULL, 'Entregado', 4200.00, '2025-10-31 14:00:00', 'CAM-001', '2025-10-26 08:00:00', '2025-10-26 08:00:00'),
('PED-20251027-00013', '18b913f3-22bd-43fa-a791-462a114b844d', NULL, 'Entregado', 4800.00, '2025-11-01 11:00:00', 'CAM-002', '2025-10-27 09:00:00', '2025-10-27 09:00:00'),
('PED-20251028-00014', 'c9dd4ad6-6184-4f76-ab2c-c09755be8a25', NULL, 'Entregado', 3900.00, '2025-11-02 15:00:00', 'CAM-003', '2025-10-28 10:00:00', '2025-10-28 10:00:00'),
('PED-20251029-00015', '82c22166-173c-4bd3-a582-b67d5eb2ce7a', NULL, 'Entregado', 5100.00, '2025-11-03 09:00:00', 'CAM-001', '2025-10-29 08:30:00', '2025-10-29 08:30:00'),
('PED-20251030-00016', '18b913f3-22bd-43fa-a791-462a114b844d', NULL, 'Entregado', 3300.00, '2025-11-04 10:00:00', 'CAM-002', '2025-10-30 11:00:00', '2025-10-30 11:00:00'),
('PED-20251031-00017', 'c9dd4ad6-6184-4f76-ab2c-c09755be8a25', NULL, 'Entregado', 5700.00, '2025-11-05 14:00:00', 'CAM-003', '2025-10-31 12:00:00', '2025-10-31 12:00:00'),
('PED-20251101-00018', '82c22166-173c-4bd3-a582-b67d5eb2ce7a', NULL, 'Entregado', 4400.00, '2025-11-06 11:00:00', 'CAM-001', '2025-11-01 08:00:00', '2025-11-01 08:00:00'),
('PED-20251102-00019', '18b913f3-22bd-43fa-a791-462a114b844d', NULL, 'Entregado', 3800.00, '2025-11-07 15:00:00', 'CAM-002', '2025-11-02 09:00:00', '2025-11-02 09:00:00'),
('PED-20251103-00020', 'c9dd4ad6-6184-4f76-ab2c-c09755be8a25', NULL, 'Entregado', 4600.00, '2025-11-08 09:00:00', 'CAM-003', '2025-11-03 10:00:00', '2025-11-03 10:00:00');

-- Insertar items para los pedidos
-- Producto 1: 250 unidades totales (TOP 1 - más vendido)
INSERT INTO order_items (order_id, product_id, quantity)
SELECT id, 1, 
    CASE order_number
        WHEN 'PED-20251015-00001' THEN 50
        WHEN 'PED-20251016-00002' THEN 30
        WHEN 'PED-20251017-00003' THEN 45
        WHEN 'PED-20251018-00004' THEN 60
        WHEN 'PED-20251019-00005' THEN 65
    END
FROM orders 
WHERE order_number IN ('PED-20251015-00001', 'PED-20251016-00002', 'PED-20251017-00003', 'PED-20251018-00004', 'PED-20251019-00005');

-- Producto 2: 180 unidades totales (TOP 2)
INSERT INTO order_items (order_id, product_id, quantity)
SELECT id, 2,
    CASE order_number
        WHEN 'PED-20251020-00006' THEN 80
        WHEN 'PED-20251021-00007' THEN 60
        WHEN 'PED-20251022-00008' THEN 40
    END
FROM orders 
WHERE order_number IN ('PED-20251020-00006', 'PED-20251021-00007', 'PED-20251022-00008');

-- Producto 3: 150 unidades totales (TOP 3)
INSERT INTO order_items (order_id, product_id, quantity)
SELECT id, 3,
    CASE order_number
        WHEN 'PED-20251023-00009' THEN 50
        WHEN 'PED-20251024-00010' THEN 60
        WHEN 'PED-20251025-00011' THEN 40
    END
FROM orders 
WHERE order_number IN ('PED-20251023-00009', 'PED-20251024-00010', 'PED-20251025-00011');

-- Producto 4: 120 unidades totales (TOP 4)
INSERT INTO order_items (order_id, product_id, quantity)
SELECT id, 4,
    CASE order_number
        WHEN 'PED-20251026-00012' THEN 40
        WHEN 'PED-20251027-00013' THEN 50
        WHEN 'PED-20251028-00014' THEN 30
    END
FROM orders 
WHERE order_number IN ('PED-20251026-00012', 'PED-20251027-00013', 'PED-20251028-00014');

-- Producto 5: 100 unidades totales (TOP 5)
INSERT INTO order_items (order_id, product_id, quantity)
SELECT id, 5,
    CASE order_number
        WHEN 'PED-20251029-00015' THEN 50
        WHEN 'PED-20251030-00016' THEN 30
        WHEN 'PED-20251031-00017' THEN 20
    END
FROM orders 
WHERE order_number IN ('PED-20251029-00015', 'PED-20251030-00016', 'PED-20251031-00017');

-- Producto 6: 90 unidades totales (TOP 6)
INSERT INTO order_items (order_id, product_id, quantity)
SELECT id, 6,
    CASE order_number
        WHEN 'PED-20251101-00018' THEN 45
        WHEN 'PED-20251102-00019' THEN 30
        WHEN 'PED-20251103-00020' THEN 15
    END
FROM orders 
WHERE order_number IN ('PED-20251101-00018', 'PED-20251102-00019', 'PED-20251103-00020');

-- Producto 7: 75 unidades totales (TOP 7)
INSERT INTO order_items (order_id, product_id, quantity)
SELECT id, 7,
    CASE order_number
        WHEN 'PED-20251015-00001' THEN 25
        WHEN 'PED-20251016-00002' THEN 30
        WHEN 'PED-20251017-00003' THEN 20
    END
FROM orders 
WHERE order_number IN ('PED-20251015-00001', 'PED-20251016-00002', 'PED-20251017-00003');

-- Producto 8: 60 unidades totales (TOP 8)
INSERT INTO order_items (order_id, product_id, quantity)
SELECT id, 8,
    CASE order_number
        WHEN 'PED-20251018-00004' THEN 30
        WHEN 'PED-20251019-00005' THEN 20
        WHEN 'PED-20251020-00006' THEN 10
    END
FROM orders 
WHERE order_number IN ('PED-20251018-00004', 'PED-20251019-00005', 'PED-20251020-00006');

-- Producto 9: 50 unidades totales (TOP 9)
INSERT INTO order_items (order_id, product_id, quantity)
SELECT id, 9,
    CASE order_number
        WHEN 'PED-20251021-00007' THEN 25
        WHEN 'PED-20251022-00008' THEN 15
        WHEN 'PED-20251023-00009' THEN 10
    END
FROM orders 
WHERE order_number IN ('PED-20251021-00007', 'PED-20251022-00008', 'PED-20251023-00009');

-- Producto 10: 40 unidades totales (TOP 10)
INSERT INTO order_items (order_id, product_id, quantity)
SELECT id, 10,
    CASE order_number
        WHEN 'PED-20251024-00010' THEN 20
        WHEN 'PED-20251025-00011' THEN 12
        WHEN 'PED-20251026-00012' THEN 8
    END
FROM orders 
WHERE order_number IN ('PED-20251024-00010', 'PED-20251025-00011', 'PED-20251026-00012');

-- Productos adicionales (11-15) con menores cantidades
INSERT INTO order_items (order_id, product_id, quantity)
SELECT id, 11, 
    CASE order_number
        WHEN 'PED-20251027-00013' THEN 15
        WHEN 'PED-20251028-00014' THEN 10
        ELSE 0
    END
FROM orders 
WHERE order_number IN ('PED-20251027-00013', 'PED-20251028-00014');

INSERT INTO order_items (order_id, product_id, quantity)
SELECT id, 12,
    CASE order_number
        WHEN 'PED-20251029-00015' THEN 12
        WHEN 'PED-20251030-00016' THEN 8
        ELSE 0
    END
FROM orders 
WHERE order_number IN ('PED-20251029-00015', 'PED-20251030-00016');

INSERT INTO order_items (order_id, product_id, quantity)
SELECT id, 13,
    CASE order_number
        WHEN 'PED-20251031-00017' THEN 10
        WHEN 'PED-20251101-00018' THEN 5
        ELSE 0
    END
FROM orders 
WHERE order_number IN ('PED-20251031-00017', 'PED-20251101-00018');

INSERT INTO order_items (order_id, product_id, quantity)
SELECT id, 14, 8
FROM orders 
WHERE order_number = 'PED-20251102-00019';

INSERT INTO order_items (order_id, product_id, quantity)
SELECT id, 15, 5
FROM orders 
WHERE order_number = 'PED-20251103-00020';

-- Resumen de datos insertados:
-- ============================================
-- Producto 1:  250 unidades (TOP 1 - más vendido)
-- Producto 2:  180 unidades (TOP 2)
-- Producto 3:  150 unidades (TOP 3)
-- Producto 4:  120 unidades (TOP 4)
-- Producto 5:  100 unidades (TOP 5)
-- Producto 6:   90 unidades (TOP 6)
-- Producto 7:   75 unidades (TOP 7)
-- Producto 8:   60 unidades (TOP 8)
-- Producto 9:   50 unidades (TOP 9)
-- Producto 10:  40 unidades (TOP 10)
-- Producto 11: 25 unidades
-- Producto 12: 20 unidades
-- Producto 13: 15 unidades
-- Producto 14:  8 unidades
-- Producto 15:  5 unidades
-- ============================================
-- Total: 20 pedidos con items de productos variados
-- El reporte mostrará los top 10 productos más vendidos
