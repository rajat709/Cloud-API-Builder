BEGIN;

WITH deleted_sdb AS (
    DELETE FROM "public"."sdb"
    WHERE "lambda_id" = ANY (ARRAY[
        'lambda_id_1',
        'lambda_id_2',
        'lambda_id_3'
    ])
    RETURNING "node_id"
)
DELETE FROM "public"."instance"
WHERE "host_id" IN (SELECT "node_id" FROM deleted_sdb);

COMMIT;
