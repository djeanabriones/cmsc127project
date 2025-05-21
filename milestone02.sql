-- CREATE TABLES

CREATE TABLE member(
    memberid INT(5),
    firstname VARCHAR(50),
    lastname VARCHAR(50),
    batch INT(4),
    gender VARCHAR(6),
    degreeprogram VARCHAR(50),
    CONSTRAINT member_memberid_pk PRIMARY KEY(memberid)
)

CREATE TABLE organization(
    organizationid INT(3),
    organizationname VARCHAR(50),
    CONSTRAINT organization_organizationid_pk PRIMARY KEY(organizationid)
)

CREATE TABLE fee(
    feeid INT(3),
    semester INT(1),
    academicyear INT(4),
    totaldue INT(6),
    totalpaid INT(6),
    balancedue INT(6),
    paymentstatus VARCHAR(6), /* paid or unpaid*/
    paymentduedate DATE,
    datepaid DATE,
    memberid INT(5),
    organizationid INT(3),
    CONSTRAINT fee_feeid_pk PRIMARY KEY(feeid),
    CONSTRAINT fee_memberid_fk FOREIGN KEY(memberid) REFERENCES member,
    CONSTRAINT fee_organizationid_fk FOREIGN KEY(memberid) REFERENCES organization,
)

CREATE TABLE serves (
    memberid INT(5),
    organizationid INT(3),
    role VARCHAR(50),
    status VARCHAR(20), -- active, inactive, expelled, suspended, alumni
    committee VARCHAR(50),
    semester INT(1),
    academicyear INT(4),
    CONSTRAINT serves_memberid_fk FOREIGN KEY (memberid) REFERENCES member(memberid),
    CONSTRAINT serves_organizationid_fk FOREIGN KEY (organizationid) REFERENCES organization(organizationid)
);

-- FEATURES

-- Add, update, delete, and search for members
INSERT INTO member VALUES (?, "?", "?", ?, "?", "?");

DELETE FROM member WHERE memberid = ?;

SELECT * from member WHERE memberid = ?;

-- View all members of the organization by role, status, gender, degree program, batch (year of
--membership), and committee. (Note: we assume one committee membership only per
--organization per semester)

SELECT s.role, s.status, m.gender, m.degreeprogram, m.batch, s.committee, m.firstname, m.lastname
FROM member m
JOIN serves s ON m.memberid = s.memberid
WHERE s.organizationid = ?;


-- View members for a given organization with unpaid membership fees or dues for a given
-- semester and academic year.

SELECT s.firstname, s.lastname
FROM member m
JOIN fee f ON m.memberid = f.memberid
WHERE f.organizationid = ?
  AND f.semester = ?
  AND f.academicyear = ?
  AND f.paymentstatus = 'unpaid';

-- View a member’s unpaid membership fees or dues for all their organizations (Member’s
--POV).

SELECT o.organizationname, f.semester, f.academicyear, f.balancedue
FROM organization o
JOIN fee f ON o.organizationid = f.organizationid
WHERE f.memberid = ?
  AND f.paymentstatus = 'unpaid';

-- View all executive committee members of a given organization for a given academic year.

SELECT m.firstname, m.lastname
FROM member m
JOIN serves s ON m.memberid = s.memberid
WHERE s.organizationid = ?
    AND s.academicyear = ?
    AND s.role IN ('President', 'Vice President', 'Secretary', 'Treasurer', 'Auditor');

-- View all Presidents (or any other role) of a given organization for every academic year in
-- reverse chronological order (current to past).

SELECT m.firstname, m.lastname, s.academicyear
FROM member m
JOIN serves s ON m.memberid = s.memberid
WHERE s.organizationid = ?
  AND s.role = 'President'
ORDER BY s.academicyear DESC;

-- View all late payments made by all members of a given organization for a given semester
-- and academic year.

SELECT m.firstname, m.lastname, f.datepaid, f.paymentduedate
FROM fee f
JOIN member m ON f.memberid = m.memberid
WHERE f.organizationid = ?
  AND f.semester = ?
  AND f.academicyear = ?
  AND f.datepaid > f.paymentduedate;

-- View the percentage of active vs inactive members of a given organization for the last n
-- semesters. (Note: n is a positive integer)

SELECT 
    status,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM serves WHERE organizationid = ? AND academicyear >= ? AND academicyear <= ?) AS percentage
FROM serves
WHERE organizationid = ?
  AND academicyear >= ?
  AND academicyear <= ?
  AND status IN ('active', 'inactive')
GROUP BY status;

-- View all alumni members of a given organization as of a given date.

SELECT m.firstname, m.lastname
FROM serves s
JOIN member m ON s.memberid = m.memberid
WHERE s.organizationid = ?  
  AND s.status = 'alumni'
  AND MAX(s.academicyear) < ?;


-- View the total amount of unpaid and paid fees or dues of a given organization as of a given
-- date.

SELECT 
    SUM(CASE WHEN paymentstatus = 'paid' THEN totalpaid ELSE 0 END) AS total_paid,
    SUM(CASE WHEN paymentstatus = 'unpaid' THEN balancedue ELSE 0 END) AS total_unpaid
FROM fee
WHERE organizationid = ?
  AND (paymentduedate <= ? OR datepaid <= ?);


-- View the member/s with the highest debt of a given organization for a given semester.

SELECT m.firstname, m.lastname, f.balancedue
FROM fee f
JOIN member m ON f.memberid = m.memberid
WHERE f.organizationid = ?
  AND f.semester = ?
  AND f.balancedue = (
      SELECT MAX(balancedue)
      FROM fee
      WHERE organizationid = ?
        AND semester = ?
  );
