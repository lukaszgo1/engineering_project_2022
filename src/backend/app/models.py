from __future__ import annotations

from collections.abc import (
    Sequence,
)

from app import app, db


class Institutions(db.Model):
    __table__ = db.Model.metadata.tables['institutions']
    def institution_to_dict(self):
        data = {
            'InstitutionId': self.InstitutionId,
            'InstitutionName': self.InstitutionName,
            'StartingHour': self.StartingHour,
            'EndingHour': self.EndingHour,
            'HasBreaks': self.HasBreaks,
            'NormalBreakLength': self.NormalBreakLength,
            'NormalLessonLength': self.NormalLessonLength
        }
        return data

    @staticmethod
    def institutions_to_dict(institutions):
        data = {
            'item': [institution.institution_to_dict() for institution in institutions]
        }
        return data

class Breaks(db.Model):
    __table__ = db.Model.metadata.tables['breaks']
    def break_to_dict(self):
        data = {
            'BreakId': self.BreakId,
            'InstitutionId': self.InstitutionId,
            'BreakStartingHour': self.BreakStartingHour,
            'BreakEndingHour': self.BreakEndingHour
        }
        return data

    @staticmethod
    def breaks_to_dict(breaks):
        data = {
            'item': [b.break_to_dict() for b in breaks]
        }
        return data

class Teachers(db.Model):
    __table__ = db.Model.metadata.tables['teachers']
    def teacher_to_dict(self):
        data = {
            'TeacherId': self.TeacherId,
            'EmployedIn': self.EmployedIn,
            'FirstName': self.FirstName,
            'LastName': self.LastName,
            'IsAvailable': self.IsAvailable
        }
        return data

    @staticmethod
    def teachers_to_dict(teachers):
        data = {
            'item': [teacher.teacher_to_dict() for teacher in teachers]
        }
        return data

class Subjects(db.Model):
    __table__ = db.Model.metadata.tables['subjects']
    def subject_to_dict(self):
        data = {
            'SubjectId': self.SubjectId,
            'SubjectName': self.SubjectName,
            'TaughtIn': self.TaughtIn
        }
        return data

    @staticmethod
    def subjects_to_dict(subjects):
        data = {
            'item': [subject.subject_to_dict() for subject in subjects]
        }
        return data

class Classes(db.Model):
    __table__ = db.Model.metadata.tables['classes']
    def class_to_dict(self):
        data = {
            'ClassId': self.ClassId,
            'ClassInInstitution': self.ClassInInstitution,
            'ClassIdentifier': self.ClassIdentifier
        }
        return data

    @staticmethod
    def classes_to_dict(classes):
        data = {
            'item': [c.class_to_dict() for c in classes]
        }
        return data

class ClassRooms(db.Model):
    __table__ = db.Model.metadata.tables['classrooms']
    def classRoom_to_dict(self):
        data = {
            'ClassRoomId': self.ClassRoomId,
            'IsIn': self.IsIn,
            'ClassRoomIdentifier': self.ClassRoomIdentifier,
            'PrimaryCourse': self.PrimaryCourse
        }
        return data

    @staticmethod
    def classRooms_to_dict(classRooms):
        data = {
        'item': [classRoom.classRoom_to_dict() for classRoom in classRooms]
    }
        return data

class TeachersToSubjects(db.Model):
    __table__ = db.Model.metadata.tables['teacherstosubjects']

    def teacherToSubject_to_dict(self):
        data = {
            'TeacherToSubjectId': self.TeacherToSubjectId,
            'TeacherId': self.TeacherId,
            'SubjectId': self.SubjectId
        }
        return data

    @staticmethod
    def TeachersToSubjects_to_dict(teachersToSubjects):
        data = {
            'item': [teacherToSubject.teacherToSubject_to_dict() for teacherToSubject in teachersToSubjects]
        }
        return data


class Terms(db.Model):
    __table__ = db.Model.metadata.tables['terms']
    def term_to_dict(self):
        data = {
            'TermId': self.TermId,
            'TermInInst': self.TermInInst,
            'StartDate': self.StartDate,
            'EndDate': self.EndDate,
            'TermName': self.TermName
        }
        return data

    @staticmethod
    def terms_to_dict(terms):
        data = {
            'item': [term.term_to_dict() for term in terms]
        }
        return data

class TermPlan(db.Model):
    __table__ = db.Model.metadata.tables['termplan']
    def termPlan_to_dict(self):
        data = {
            'TermPlanId': self.TermPlanId,
            'AppliesToTerm': self.AppliesToTerm,
            'TermPlanName': self.TermPlanName
        }
        return data

    @staticmethod
    def termPlans_to_dict(termPlans):
        data = {
            'item': [termPlan.termPlan_to_dict() for termPlan in termPlans]
        }
        return data

class ClassToTermPlan(db.Model):
    __table__ = db.Model.metadata.tables['classtotermplan']

    def classToTermPlan_to_dict(self):
        data = {
            'ClassToTermPlanId': self.ClassToTermPlanId,
            'ClassId': self.ClassId,
            'TermPlanId': self.TermPlanId
        }
        return data


class TermPlanDetails(db.Model):
    __table__ = db.Model.metadata.tables['termplandetails']
    def termPlanDetail_to_dict(self):
        data = {
            'TermPlanDetailId': self.TermPlanDetailId,
            'TermPlanId': self.TermPlanId,
            'LessonsAmount': self.LessonsAmount,
            'LessonsWeekly': self.LessonsWeekly,
            'MinBlockSize': self.MinBlockSize,
            'MaxBlockSize': self.MaxBlockSize,
            'PreferredDistanceInDays': self.PreferredDistanceInDays,
            'PreferredDistanceInWeeks': self.PreferredDistanceInWeeks,
            'SubjectId': self.SubjectId
        }
        return data

    @staticmethod
    def TermPlanDetails_to_dict(termPlanDetails):
        data = {
            'item': [termPlanDetail.termPlanDetail_to_dict() for termPlanDetail in termPlanDetails]
        }
        return data

class Schedule(db.Model):
    __table__ = db.Model.metadata.tables['schedule']

    def schedule_to_dict(self):
        return {
            "LessonId": self.LessonId,
            "InstitutionId": self.InstitutionId,
            "WeekDay": self.WeekDay,
            "LessonStartingHour": self.LessonStartingHour,
            "LessonEndingHour": self.LessonEndingHour,
            "TeacherId": self.TeacherId,
            "SubjectId": self.SubjectId,
            "ClassId": self.ClassId,
            "ClassRoomId": self.ClassRoomId,
#            "LessonDate": self.LessonDate,
            "InTerm": self.InTerm,
        }

    @staticmethod
    def schedule_entries_to_dict(Schedule_entries: Sequence[Schedule]):
        return {
            "item": [_.schedule_to_dict() for _ in Schedule_entries]
        }
