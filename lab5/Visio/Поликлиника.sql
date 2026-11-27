CREATE TABLE District (
  district_no SMALLINT NOT NULL,
  territory NVARCHAR(200) NOT NULL,
  CONSTRAINT PK_District PRIMARY KEY (district_no)
);

CREATE TABLE Specialty (
  specialty_id SMALLINT NOT NULL,
  specialty_name NVARCHAR(60) NOT NULL,
  CONSTRAINT PK_Specialty PRIMARY KEY (specialty_id)
);

CREATE TABLE Room (
  room_no SMALLINT NOT NULL,
  floor TINYINT NOT NULL,
  purpose NVARCHAR(60),
  CONSTRAINT PK_Room PRIMARY KEY (room_no)
);

CREATE TABLE Diagnosis (
  icd_code VARCHAR(7) NOT NULL,
  diagnosis_name NVARCHAR(200) NOT NULL,
  CONSTRAINT PK_Diagnosis PRIMARY KEY (icd_code)
);

CREATE TABLE Medicine (
  medicine_id INT NOT NULL,
  medicine_name NVARCHAR(100) NOT NULL,
  dosage_form NVARCHAR(40) NOT NULL,
  CONSTRAINT PK_Medicine PRIMARY KEY (medicine_id)
);

CREATE TABLE Patient (
  card_no INT NOT NULL,
  district_no SMALLINT NOT NULL,
  last_name NVARCHAR(40) NOT NULL,
  first_name NVARCHAR(40) NOT NULL,
  middle_name NVARCHAR(40),
  birth_date DATE NOT NULL,
  sex CHAR(1) NOT NULL,
  address NVARCHAR(200) NOT NULL,
  phone VARCHAR(16),
  oms_policy CHAR(16) NOT NULL,
  snils CHAR(11),
  CONSTRAINT PK_Patient PRIMARY KEY (card_no),
  CONSTRAINT FK_Patient_District_district_no FOREIGN KEY (district_no) REFERENCES District,
  CONSTRAINT AK_Patient_oms UNIQUE (oms_policy)
);

CREATE TABLE Doctor (
  doctor_id INT NOT NULL,
  specialty_id SMALLINT NOT NULL,
  room_no SMALLINT NOT NULL,
  district_no SMALLINT,
  last_name NVARCHAR(40) NOT NULL,
  first_name NVARCHAR(40) NOT NULL,
  middle_name NVARCHAR(40),
  category NVARCHAR(20),
  CONSTRAINT PK_Doctor PRIMARY KEY (doctor_id),
  CONSTRAINT FK_Doctor_Specialty_specialty_id FOREIGN KEY (specialty_id) REFERENCES Specialty,
  CONSTRAINT FK_Doctor_Room_room_no FOREIGN KEY (room_no) REFERENCES Room,
  CONSTRAINT FK_Doctor_District_district_no FOREIGN KEY (district_no) REFERENCES District
);

CREATE TABLE Ticket (
  doctor_id INT NOT NULL,
  visit_date DATE NOT NULL,
  visit_time TIME(0) NOT NULL,
  card_no INT,
  status NVARCHAR(15) NOT NULL,
  CONSTRAINT PK_Ticket PRIMARY KEY (doctor_id, visit_date, visit_time),
  CONSTRAINT FK_Ticket_Doctor_doctor_id FOREIGN KEY (doctor_id) REFERENCES Doctor,
  CONSTRAINT FK_Ticket_Patient_card_no FOREIGN KEY (card_no) REFERENCES Patient
);

CREATE TABLE Visit (
  doctor_id INT NOT NULL,
  visit_date DATE NOT NULL,
  visit_time TIME(0) NOT NULL,
  icd_code VARCHAR(7) NOT NULL,
  complaints NVARCHAR(500),
  recommendations NVARCHAR(500),
  sick_leave BIT NOT NULL,
  CONSTRAINT PK_Visit PRIMARY KEY (doctor_id, visit_date, visit_time),
  CONSTRAINT FK_Visit_Diagnosis_icd_code FOREIGN KEY (icd_code) REFERENCES Diagnosis,
  CONSTRAINT FK_Visit_Ticket FOREIGN KEY (doctor_id, visit_date, visit_time) REFERENCES Ticket
);

CREATE TABLE Prescription (
  prescription_no INT NOT NULL,
  doctor_id INT NOT NULL,
  visit_date DATE NOT NULL,
  visit_time TIME(0) NOT NULL,
  medicine_id INT NOT NULL,
  dosage NVARCHAR(100) NOT NULL,
  issue_date DATE NOT NULL,
  CONSTRAINT PK_Prescription PRIMARY KEY (prescription_no),
  CONSTRAINT FK_Prescription_Medicine_medicine_id FOREIGN KEY (medicine_id) REFERENCES Medicine,
  CONSTRAINT FK_Prescription_Visit FOREIGN KEY (doctor_id, visit_date, visit_time) REFERENCES Visit
);
