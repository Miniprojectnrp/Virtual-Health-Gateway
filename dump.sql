PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                address TEXT,
                phone TEXT,
                gender TEXT
            );
INSERT INTO patients VALUES(1,'mickey',34,'new delhi','8989898987','Male');
INSERT INTO patients VALUES(2,'ni',29,'bangalore','9090909090','Male');
INSERT INTO patients VALUES(3,'sameera',23,'Mysore','8789098789','Female');
INSERT INTO sqlite_sequence VALUES('patients',3);
COMMIT;
