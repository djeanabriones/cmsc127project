
DROP TABLE IF EXISTS serves;
DROP TABLE IF EXISTS fee;
DROP TABLE IF EXISTS organization;
DROP TABLE IF EXISTS member;


-- CREATE TABLES

CREATE TABLE member(
    memberid INT(5),
    firstname VARCHAR(50),
    lastname VARCHAR(50),
    batch INT(4),
    gender VARCHAR(6),
    degreeprogram VARCHAR(50),
    CONSTRAINT member_memberid_pk PRIMARY KEY(memberid)
);

CREATE TABLE organization(
    organizationid INT(3),
    organizationname VARCHAR(50),
    CONSTRAINT organization_organizationid_pk PRIMARY KEY(organizationid)
);

CREATE TABLE fee(
    feeid INT(3),
    semester INT(1),    
    academicyear VARCHAR(9),
    totaldue INT(6),
    totalpaid INT(6),
    balancedue INT(6),
    paymentstatus VARCHAR(6), /* paid or unpaid*/
    paymentduedate DATE,
    datepaid DATE,
    memberid INT(5),
    organizationid INT(3),
    CONSTRAINT fee_feeid_pk PRIMARY KEY(feeid),
    CONSTRAINT fee_memberid_fk FOREIGN KEY(memberid) REFERENCES member(memberid),
    CONSTRAINT fee_organizationid_fk FOREIGN KEY(organizationid) REFERENCES organization(organizationid)
);


CREATE TABLE serves (
    memberid INT(5),
    organizationid INT(3),
    role VARCHAR(50),
    status VARCHAR(20), -- active, inactive, expelled, suspended, alumni
    committee VARCHAR(50),
    semester INT(1),
    academicyear VARCHAR(9),
    CONSTRAINT serves_memberid_fk FOREIGN KEY (memberid) REFERENCES member(memberid),
    CONSTRAINT serves_organizationid_fk FOREIGN KEY (organizationid) REFERENCES organization(organizationid)
);

-- Insert sample organizations
INSERT INTO organization (organizationid, organizationname) VALUES 
(1, 'Alliance of Statistics Majors - UPLB'),
(2, 'UPLB Career Assistance Program'),
(3, 'Alliance of Computer Science Students - UPLB'),
(4, 'The Philosophical Society of UPLB'),
(5, 'UP Society of Management and Economics Students'),
(6, 'UP Cell Biological Society');

-- Insert sample members
INSERT INTO member (memberid, firstname, lastname, batch, gender, degreeprogram) VALUES 
(1, 'Joremze', 'Ferrer', 2022, 'Male', 'BS Statistics'),
(2, 'Djeana Carel', 'Briones', 2023, 'Female', 'BS Computer Science'),
(3, 'Robin Drey', 'Rebugio', 2023, 'Male', 'BS Computer Science'),
(4, 'Juan', 'Dela Cruz', 2020, 'Male', 'BS Economics'),
(5, 'Maria', 'Santos', 2021, 'Female', 'BS Biology'),
(6, 'Alex', 'Reyes', 2021, 'Male', 'BS Statistics'),
(7, 'Taylor', 'Swift', 2023, 'Female', 'BS Computer Science'),
(8, 'Jordan', 'Garcia', 2020, 'Male', 'BS Economics'),
(9, 'Dana', 'Angeles', 2022, 'Female', 'BS Biology'),
(10, 'Casey', 'Martinez', 2021, 'Male', 'BS Agricultural Engineering');

-- Insert sample memberships (SERVES)
INSERT INTO serves (memberid, organizationid, role, status, committee, semester, academicyear) VALUES 
(1, 1, 'President', 'Active', 'Executive', '2', '2024-2025'),
(2, 2, 'Treasurer', 'Active', 'Executive', '2', '2024-2025'),
(3, 5, 'Member', 'Inactive', 'Membership', '2', '2024-2025'),
(4, 1, 'Member', 'Suspended', 'Legislative', '2', '2024-2025'),
(1, 4, 'Member', 'Alumni', 'Finance', '2', '2024-2025'),
(2, 3, 'Secretary', 'Active', 'Executive', '2', '2024-2025'),
(5, 6, 'Member', 'Inactive', 'Publicity', '1', '2023-2024'),
(5, 4, 'Member', 'Expelled', 'External Affairs', '2', '2023-2024'),
(6, 5, 'Vice President', 'Active', 'Executive', '1', '2023-2024'),
(7, 6, 'Secretary', 'Active', 'Membership', '2', '2023-2024'),
(8, 1, 'Member', 'Alumni', 'Publicity', '1', '2022-2023'),
(9, 2, 'President', 'Active', 'Executive', '2', '2024-2025'),
(10, 6, 'Treasurer', 'Active', 'Finance', '2', '2024-2025'),
(6, 3, 'Member', 'Active', 'Publicity', '2', '2022-2023'),
(7, 4, 'Member', 'Inactive', 'Legislative', '1', '2023-2024'),
(8, 5, 'Member', 'Suspended', 'External Affairs', '2', '2024-2025'),
(9, 3, 'Vice President', 'Alumni', 'Executive', '1', '2021-2022'),
(10, 2, 'Secretary', 'Active', 'Executive', '2', '2022-2023');

-- Insert sample fees
INSERT INTO fee (feeid, semester, academicyear, totaldue, totalpaid, paymentduedate, datepaid, memberid, organizationid) VALUES 
(1, '2', '2024-2025', 500.00, 500.00, '2025-03-15', '2025-03-10', 1, 1),
(2, '2', '2024-2025', 500.00, 500.00, '2025-03-15', '2025-04-12', 2, 1),
(3, '2', '2024-2025', 500.00, 0.00, '2025-03-15', NULL, 3, 1),
(4, '2', '2024-2025', 500.00, 500.00, '2025-03-15', '2025-03-14', 4, 1),
(5, '1', '2023-2024', 400.00, 400.00, '2024-10-15', '2024-10-10', 5, 1),
(6, '2', '2023-2024', 400.00, 200.00, '2025-03-15', '2025-03-20', 5, 1),
(7, '1', '2023-2024', 500.00, 0.00, '2024-10-15', NULL, 6, 1),
(8, '2', '2024-2025', 500.00, 500.00, '2025-03-15', '2025-03-20', 7, 1),
(9, '2', '2024-2025', 500.00, 200.00, '2025-03-15', '2025-04-20', 8, 2),
(10, '1', '2022-2023', 400.00, 400.00, '2023-10-15', '2023-10-14', 9, 3),
(11, '2', '2022-2023', 400.00, 0.00, '2023-03-15', NULL, 10, 4),
(12, '1', '2023-2024', 400.00, 400.00, '2024-10-15', '2024-10-12', 6, 2),
(13, '2', '2023-2024', 400.00, 400.00, '2025-03-15', '2025-03-16', 7, 2),
(14, '1', '2023-2024', 400.00, 0.00, '2024-10-15', NULL, 8, 3),
(15, '2', '2024-2025', 500.00, 250.00, '2025-03-15', '2025-04-01', 9, 4),
(16, '1', '2023-2024', 400.00, 400.00, '2024-10-15', '2024-10-15', 10, 5),
(17, '2', '2024-2025', 500.00, 500.00, '2025-03-15', '2025-03-12', 6, 3),
(18, '1', '2022-2023', 400.00, 0.00, '2023-10-15', NULL, 7, 4),
(19, '2', '2022-2023', 400.00, 400.00, '2023-03-15', '2023-03-10', 8, 5),
(20, '2', '2023-2024', 400.00, 400.00, '2025-03-15', '2025-03-13', 9, 6),
(21, '1', '2023-2024', 400.00, 0.00, '2024-10-15', NULL, 10, 6),
(22, '2', '2024-2025', 500.00, 500.00, '2025-03-15', '2025-03-11', 1, 2),
(23, '1', '2023-2024', 400.00, 400.00, '2024-10-15', '2024-10-12', 2, 3),
(24, '2', '2024-2025', 500.00, 0.00, '2025-03-15', NULL, 3, 4),
(25, '2', '2023-2024', 400.00, 200.00, '2025-03-15', '2025-03-22', 4, 5),
(26, '1', '2023-2024', 400.00, 400.00, '2024-10-15', '2024-10-10', 5, 6),
(27, '2', '2023-2024', 400.00, 400.00, '2025-03-15', '2025-03-14', 6, 5),
(28, '1', '2023-2024', 400.00, 400.00, '2024-10-15', '2024-10-14', 7, 6),
(29, '1', '2022-2023', 400.00, 0.00, '2023-10-15', NULL, 8, 2),
(30, '2', '2024-2025', 500.00, 500.00, '2025-03-15', '2025-03-12', 9, 1);


