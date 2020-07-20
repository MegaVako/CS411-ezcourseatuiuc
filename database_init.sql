CREATE TABLE `Students` (
    `netid` varchar(10)  NOT NULL ,
    `department` varchar(4)  NOT NULL ,
    PRIMARY KEY (
        `netid`
    )
);

CREATE TABLE `Courses` (
    `department` varchar(4)  NOT NULL ,
    `course_code` int  NOT NULL ,
    `semester` varchar(2)  NOT NULL ,
    `year` int  NOT NULL ,
    `requirement_type` varchar(10)  NOT NULL ,
    `requirement_fulfill` varchar(20) NOT NULL,
    `course_description` varchar(1200)  NOT NULL ,
    PRIMARY KEY (
        `department`,`course_code`,`semester`,`year`
    )
);

CREATE TABLE `Teach` (
    `crn` int  NOT NULL ,
    `prof_fname` varchar(20)  NOT NULL ,
    `prof_lname` varchar(20)  NOT NULL ,
    `department` varchar(4)  NOT NULL ,
    `course_code` int  NOT NULL ,
    `semester` varchar(2)  NOT NULL ,
    `year` int  NOT NULL ,
    `credit_hour` int  NOT NULL ,
    `part_of_term` varchar(10)  NOT NULL ,
    `date_start` date  NOT NULL ,
    `date_end` date  NOT NULL ,
    `time_start` time  NOT NULL ,
    `time_end` time  NOT NULL ,
    `location` varchar(20)  NOT NULL ,
    `room_num` varchar(10)  NOT NULL ,
    `lecture_type` varchar(20)  NOT NULL ,
    `avg_gpa` float  NOT NULL ,
    PRIMARY KEY (
        `crn`
    )
);

CREATE TABLE `Instructors` (
    `prof_fname` varchar(20)  NOT NULL ,
    `prof_lname` varchar(20)  NOT NULL ,
    `department` varchar(10)  NOT NULL ,
    PRIMARY KEY (
        `prof_fname`,`prof_lname`,`department`
    )
);

CREATE TABLE `Voted` (
    `netid` varchar(10)  NOT NULL ,
    `department` varchar(4)  NOT NULL ,
    `course_code` int  NOT NULL ,
    `semester` varchar(2)  NOT NULL ,
    `year` int  NOT NULL ,
    `difficulty` int  NOT NULL ,
    `recommand` int  NOT NULL ,
    `comment` varchar(100)  NOT NULL ,
    `current_status` varchar(20)  NOT NULL ,
    `grade` int  NOT NULL 
);

ALTER TABLE `Teach` ADD CONSTRAINT `fk_Teach_prof_fname_prof_lname` FOREIGN KEY(`prof_fname`, `prof_lname`)
REFERENCES `Instructors` (`prof_fname`, `prof_lname`);

ALTER TABLE `Teach` ADD CONSTRAINT `fk_Teach_department_course_code_semester_year` FOREIGN KEY(`department`, `course_code`, `semester`, `year`)
REFERENCES `Courses` (`department`, `course_code`, `semester`, `year`);

ALTER TABLE `Voted` ADD CONSTRAINT `fk_Voted_netid` FOREIGN KEY(`netid`)
REFERENCES `Students` (`netid`);

ALTER TABLE `Voted` ADD CONSTRAINT `fk_Voted_department_course_code_semester_year` FOREIGN KEY(`department`, `course_code`, `semester`, `year`)
REFERENCES `Courses` (`department`, `course_code`, `semester`, `year`);

CREATE INDEX `idx_Students_department`
ON `Students` (`department`);

