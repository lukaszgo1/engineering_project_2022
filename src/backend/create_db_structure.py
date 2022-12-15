from typing import List

import app_constants
import mariadb_connector

CREATE_DATABASE_STATEMENTS: List[str] = [
  """CREATE DATABASE IF NOT EXISTS time_table_app 
   CHARACTER SET = 'utf8mb4' COLLATE = 'utf8mb4_polish_ci'""",
  """CREATE TABLE IF NOT EXISTS time_table_app.Institutions (
  InstitutionId integer PRIMARY KEY AUTO_INCREMENT,
  InstitutionName text NOT NULL,
  StartingHour varchar(5) NOT NULL,
  EndingHour varchar(5) NOT NULL,
  HasBreaks BOOLEAN,
  NormalBreakLength integer,
  NormalLessonLength integer
  );
""",
"""CREATE TABLE IF NOT EXISTS time_table_app.Breaks (
  BreakId integer PRIMARY KEY AUTO_INCREMENT,
  InstitutionId integer,
  BreakStartingHour varchar(5) NOT NULL,
  BreakEndingHour varchar(5) NOT NULL,
  CONSTRAINT  FK_INST FOREIGN KEY (InstitutionId) REFERENCES time_table_app.Institutions (InstitutionId)
);
""",
"""CREATE TABLE IF NOT EXISTS time_table_app.Teachers (
  TeacherId integer PRIMARY KEY AUTO_INCREMENT,
  FirstName text NOT NULL,
  LastName text NOT NULL,
  IsAvailable BOOLEAN,
  EmployedIn integer,
  CONSTRAINT FK_EMPLOYED_IN  FOREIGN KEY (EmployedIn) REFERENCES time_table_app.Institutions (InstitutionId)
);
""",
"""CREATE TABLE IF NOT EXISTS time_table_app.Subjects (
  SubjectId integer PRIMARY KEY AUTO_INCREMENT,
  SubjectName text NOT NULL,
  TaughtIn integer,
  CONSTRAINT FK_TAUGHT_IN FOREIGN KEY (TaughtIn) REFERENCES time_table_app.Institutions (InstitutionId)
);
""",
"""CREATE TABLE IF NOT EXISTS time_table_app.Classes (
  ClassId integer PRIMARY KEY AUTO_INCREMENT,
  ClassIdentifier text,
  ClassInInstitution integer,
  CONSTRAINT FK_CLASS_IN_INST FOREIGN KEY (ClassInInstitution) REFERENCES time_table_app.Institutions (InstitutionId)
);
""",
"""CREATE TABLE IF NOT EXISTS time_table_app.ClassRooms (
  ClassRoomId integer PRIMARY KEY   AUTO_INCREMENT,
  ClassRoomIdentifier text,
  IsIn integer,
  PrimaryCourse integer,
  CONSTRAINT FK_CLASS_IN FOREIGN KEY (IsIn) REFERENCES time_table_app.Institutions (InstitutionId),
  CONSTRAINT FK_CLASS_COURSE_IN FOREIGN KEY (PrimaryCourse) REFERENCES time_table_app.Classes(ClassId)
);
""",
"""CREATE TABLE IF NOT EXISTS time_table_app.TeachersToSubjects(
  TeacherToSubjectId integer PRIMARY KEY AUTO_INCREMENT,
  TeacherId integer,
  SubjectId integer,
  CONSTRAINT  FK_TEACHER_IN_SUBJECT_MAPPING FOREIGN KEY (TeacherId) REFERENCES time_table_app.Teachers(TeacherId),
  CONSTRAINT  FK_SUBJECT_IN_TO_TEACHER_MAPPING FOREIGN KEY (SubjectId) REFERENCES time_table_app.Subjects(SubjectId)
)
""",
"""CREATE TABLE IF NOT EXISTS time_table_app.Terms(
  TermId integer PRIMARY KEY AUTO_INCREMENT,
  StartDate DATE,
  EndDate DATE,
  TermName TEXT,
  TermInInst integer,
  CONSTRAINT FK_TERM_IN_INST FOREIGN KEY (TermInInst) REFERENCES time_table_app.Institutions (InstitutionId)
)
""",
"""CREATE TABLE IF NOT EXISTS time_table_app.TermPlan(
  TermPlanId integer PRIMARY KEY AUTO_INCREMENT,
  TermPlanName text,
  AppliesToTerm integer,
  CONSTRAINT FK_TERM_PLAN_IN_TERM FOREIGN KEY
  (AppliesToTerm) REFERENCES time_table_app.Terms(TermId)
)
""",
"""CREATE TABLE IF NOT EXISTS time_table_app.ClassToTermPlan(
  ClassToTermPlanId integer PRIMARY KEY AUTO_INCREMENT,
  ClassId integer,
  TermPlanId integer,
  CONSTRAINT FK_TERM_PLAN_FOR_CLASS FOREIGN KEY
  (ClassId) REFERENCES time_table_app.Classes(ClassId),
  CONSTRAINT FK_TERM_PLAN_ident FOREIGN KEY
  (TermPlanId) REFERENCES time_table_app.Terms(TermId)
)
""",
"""CREATE TABLE IF NOT EXISTS time_table_app.TermPlanDetails(
  TermPlanDetailId integer PRIMARY KEY AUTO_INCREMENT,
  TermPlanId integer,
  SubjectId integer,
  LessonsAmount integer,
  MinBlockSize integer,
  MaxBlockSize integer,
  PreferredDistanceInDays integer,
  PreferredDistanceInWeeks integer,
  CONSTRAINT FK_ENTRY_FOR_SUBJECT FOREIGN KEY
  (SubjectId) REFERENCES time_table_app.Subjects(SubjectId),
  CONSTRAINT FK_ENTRY_IN_TERM_PLAN FOREIGN KEY
  (TermPlanId) REFERENCES time_table_app.TermPlan(TermPlanId)
)
""",
"""CREATE TABLE IF NOT EXISTS time_table_app.Schedule (
  LessonId integer PRIMARY KEY AUTO_INCREMENT,
  InstitutionId integer,
  WeekDay integer,
  LessonStartingHour varchar(5),
  LessonEndingHour varchar(5),
  TeacherId integer,
  SubjectId integer,
  ClassId integer,
  ClassRoomId integer,
  CONSTRAINT FK_INST_IN_SCHED FOREIGN KEY (InstitutionId) REFERENCES time_table_app.Institutions (InstitutionId),
  CONSTRAINT  FK_TEACHER_IN_SCHED FOREIGN KEY (TeacherId) REFERENCES time_table_app.Teachers(TeacherId),
  CONSTRAINT  FK_SUBJECT_IN_SCHED FOREIGN KEY (SubjectId) REFERENCES time_table_app.Subjects(SubjectId),
  CONSTRAINT  FK_CLASS_ROOM_IN_SCHED FOREIGN KEY (ClassRoomId) REFERENCES time_table_app.ClassRooms(ClassRoomId),
  CONSTRAINT  FK_CLASS_IN_SCHED FOREIGN KEY (ClassId) REFERENCES time_table_app.Classes(ClassId)
);
""",
]


def createDbBStruct():
    o = mariadb_connector.MariadbConnector(
        host=app_constants.DB_HOST,
        port_number=app_constants.db_port,
        user_name=app_constants.db_user,
        password=app_constants.db_password
    )
    o.execute_statements(CREATE_DATABASE_STATEMENTS)


if __name__ == "__main__":
    createDbBStruct()
