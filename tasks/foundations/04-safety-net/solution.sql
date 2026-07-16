-- Prove the net works: destroy everything inside a transaction, then change
-- your mind. Nothing is committed, so nothing is lost.
BEGIN;
DELETE FROM vault;
ROLLBACK;

-- Now a change we actually mean: deposit the receipt and commit it.
BEGIN;
INSERT INTO vault (id, item) VALUES (4, 'receipt');
COMMIT;
