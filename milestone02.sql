
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


