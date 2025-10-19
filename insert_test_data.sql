-- Insertar datos de prueba para pedidos
-- NOTA: Este script asume que los productos con ID 1 y 2 existen en el inventario
-- Producto 1: Paracetamol 500mg
-- Producto 2: Ibuprofeno 400mg
-- Cliente UUID: f1c2ce13-6623-4f42-a70b-9caadb7b8cbf
-- Vendedor UUID: df3bdc3f-7783-4c1e-981a-8060b114dfb2

INSERT INTO orders (order_number, client_id, vendor_id, status, scheduled_delivery_date, assigned_truck, created_at, updated_at) 
VALUES 
('PED-20241207-12345', 'f1c2ce13-6623-4f42-a70b-9caadb7b8cbf', 'df3bdc3f-7783-4c1e-981a-8060b114dfb2', 'RECIBIDO', '2024-12-08 10:00:00', 'TRK-001', NOW(), NOW()),
('PED-20241207-12346', 'f1c2ce13-6623-4f42-a70b-9caadb7b8cbf', 'df3bdc3f-7783-4c1e-981a-8060b114dfb2', 'EN_PREPARACION', '2024-12-09 14:30:00', 'TRK-002', NOW(), NOW()),
('PED-20241207-12347', 'f1c2ce13-6623-4f42-a70b-9caadb7b8cbf', 'df3bdc3f-7783-4c1e-981a-8060b114dfb2', 'EN_TRANSITO', '2024-12-08 16:45:00', 'TRK-003', NOW(), NOW()),
('PED-20241207-12348', 'f1c2ce13-6623-4f42-a70b-9caadb7b8cbf', 'df3bdc3f-7783-4c1e-981a-8060b114dfb2', 'ENTREGADO', '2024-12-07 09:15:00', 'TRK-004', NOW(), NOW()),
('PED-20241207-12349', 'f1c2ce13-6623-4f42-a70b-9caadb7b8cbf', 'df3bdc3f-7783-4c1e-981a-8060b114dfb2', 'DEVUELTO', '2024-12-06 15:30:00', 'TRK-005', NOW(), NOW());

-- Insertar items para el primer pedido (PED-20241207-12345) - Cliente f1c2ce13-6623-4f42-a70b-9caadb7b8cbf, Vendedor df3bdc3f-7783-4c1e-981a-8060b114dfb2
INSERT INTO order_items (order_id, product_id, quantity) 
VALUES 
(1, 1, 10),  -- 10 Paracetamol
(1, 2, 5);   -- 5 Ibuprofeno

-- Insertar items para el segundo pedido (PED-20241207-12346) - Cliente f1c2ce13-6623-4f42-a70b-9caadb7b8cbf, Vendedor df3bdc3f-7783-4c1e-981a-8060b114dfb2
INSERT INTO order_items (order_id, product_id, quantity) 
VALUES 
(2, 1, 3),   -- 3 Paracetamol
(2, 2, 8),   -- 8 Ibuprofeno
(2, 1, 2);   -- 2 Paracetamol más

-- Insertar items para el tercer pedido (PED-20241207-12347) - Cliente f1c2ce13-6623-4f42-a70b-9caadb7b8cbf, Vendedor df3bdc3f-7783-4c1e-981a-8060b114dfb2
INSERT INTO order_items (order_id, product_id, quantity) 
VALUES 
(3, 2, 15);  -- 15 Ibuprofeno

-- Insertar items para el cuarto pedido (PED-20241207-12348) - Cliente f1c2ce13-6623-4f42-a70b-9caadb7b8cbf, Vendedor df3bdc3f-7783-4c1e-981a-8060b114dfb2
INSERT INTO order_items (order_id, product_id, quantity) 
VALUES 
(4, 1, 20),  -- 20 Paracetamol
(4, 2, 10);  -- 10 Ibuprofeno

-- Insertar items para el quinto pedido (PED-20241207-12349) - Cliente f1c2ce13-6623-4f42-a70b-9caadb7b8cbf, Vendedor df3bdc3f-7783-4c1e-981a-8060b114dfb2
INSERT INTO order_items (order_id, product_id, quantity) 
VALUES 
(5, 1, 5),   -- 5 Paracetamol
(5, 2, 3),   -- 3 Ibuprofeno
(5, 1, 2);   -- 2 Paracetamol más
