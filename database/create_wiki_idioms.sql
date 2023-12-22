BEGIN TRANSACTION;
CREATE TABLE wiki_idioms (
name VARCHAR PRIMARY KEY
);

INSERT INTO wiki_idioms(name)
SELECT name FROM idiom
UNION
SELECT name FROM form_idiom
ORDER BY name;
COMMIT;
