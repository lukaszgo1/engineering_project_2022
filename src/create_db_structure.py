from typing import List
import os
import sqlite3


DB_FILE_PATH: os.PathLike = os.path.join(os.getenv("APPDATA"), "Ukladacz", "db.sqlite")


CREATE_DATABASE_STATEMENTS: List[str] = [
	"""CREATE TABLE IF NOT EXISTS Institutions (
		InstitutionId integer PRIMARY KEY,
		InstitutionName text NOT NULL,
		StartingHour text NOT NULL,
		EndingHour text NOT NULL,
		HasBreaks integer,
		NormalBreakLength integer,
		NormalLessonLength integer
		);
	""",
	"""CREATE TABLE IF NOT EXISTS Breaks (
  BreakId integer PRIMARY KEY,
  InstitutionId integer,
  BreakStartingHour text NOT NULL,
  BreakEndingHour text NOT NULL,
  FOREIGN KEY (InstitutionId) REFERENCES Institutions (InstitutionId)
);
""",
"""CREATE TABLE IF NOT EXISTS Teachers (
  TeacherId integer PRIMARY KEY,
  FirstName text NOT NULL,
  LastName text NOT NULL,
  IsAvailable integer,
  EmployedIn integer,
  FOREIGN KEY (EmployedIn) REFERENCES Institutions (InstitutionId)
);
""",
"""CREATE TABLE IF NOT EXISTS Subjects (
  SubjectId integer PRIMARY KEY,
  SubjectName text NOT NULL,
  TaughtIn integer,
  FOREIGN KEY (TaughtIn) REFERENCES Institutions (InstitutionId)
);
""",
"""CREATE TABLE IF NOT EXISTS ClassRooms (
  ClassRoomId integer PRIMARY KEY,
  ClassRoomIdentifier text,
  IsIn integer,
  PrimaryCourse integer,
  FOREIGN KEY (IsIn) REFERENCES Institutions (InstitutionId)
);
""",
"""CREATE TABLE IF NOT EXISTS Classes (
  ClassId integer PRIMARY KEY,
  ClassIdentifier text,
  ClassInInstitution integer,
  FOREIGN KEY (ClassInInstitution) REFERENCES Institutions (InstitutionId)
);
""",
"""CREATE TABLE IF NOT EXISTS Schedule (
  LessonId integer PRIMARY KEY,
  InstitutionId integer,
  WeekDay integer,
  LessonStartingHour text,
  LessonEndingHour text,
  TeacherId integer,
  SubjectId integer,
  ClassId integer,
  ClassRoomId integer,
  FOREIGN KEY (InstitutionId) REFERENCES Institutions (InstitutionId),
  FOREIGN KEY (TeacherId) REFERENCES Teachers(TeacherId),
  FOREIGN KEY (SubjectId) REFERENCES Subjects(SubjectId),
  FOREIGN KEY (ClassRoomId) REFERENCES ClassRooms(ClassRoomId),
  FOREIGN KEY (ClassId) REFERENCES Classes(ClassId)
);
""",
]


def createDbBStruct():
	os.makedirs(os.path.dirname(DB_FILE_PATH), exist_ok=True)
	if os.path.isfile(DB_FILE_PATH):
		return
	with sqlite3.connect(DB_FILE_PATH) as conn:
		cur = conn.cursor()
		for statement in CREATE_DATABASE_STATEMENTS:
			cur.execute(statement)
		cur.close()
