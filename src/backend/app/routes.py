import datetime

from flask import jsonify
from app import app, db
from .models import *
import flask


@app.route('/get_institutions')
def get_institutions():
    institutions =Institutions.query.all()
    return jsonify(Institutions.institutions_to_dict(institutions))

@app.route('/get_subjects/<taught_in>')
def get_subjects(taught_in):
    subjects = Subjects.query.filter_by(TaughtIn=taught_in).all()
    return jsonify(Subjects.subjects_to_dict(subjects))

@app.route('/get_teachers/<employed_in>')
def get_teachers(employed_in):
    teachers = Teachers.query.filter_by(EmployedIn=employed_in).all()
    return jsonify(Teachers.teachers_to_dict(teachers))

@app.route('/get_classRooms/<is_in>')
def get_classRooms(is_in):
    classRooms = ClassRooms.query.filter_by(IsIn=is_in).all()
    return jsonify(ClassRooms.classRooms_to_dict(classRooms))

@app.route('/get_terms/<term_in_inst>')
def get_terms(term_in_inst):
    terms = Terms.query.filter_by(TermInInst=term_in_inst).all()
    return jsonify(Terms.terms_to_dict(terms))

@app.route('/get_class/<class_in_institution>')
def get_class(class_in_institution):
   classes = Classes.query.filter_by(ClassInInstitution=class_in_institution).all()
   return jsonify(Classes.classes_to_dict(classes))

@app.route('/get_breaks/<institution_id>')
def get_breaks(institution_id):
    breaks = Breaks.query.filter_by(InstitutionId=institution_id).all()
    return jsonify(Breaks.breaks_to_dict(breaks))

@app.route('/get_termPlans/<applies_to_term>')
def get_termPlans(applies_to_term):
    termPlans = TermPlan.query.filter_by(AppliesToTerm=applies_to_term)
    return jsonify(TermPlan.termPlans_to_dict(termPlans))

@app.route('/get_termPlanDetails/<TermPlanId>')
def get_termPlanDetails(TermPlanId):
    termPlanDetails = TermPlanDetails.query.filter_by(TermPlanId=TermPlanId)
    return jsonify(TermPlanDetails.TermPlanDetails_to_dict(termPlanDetails))

@app.route('/get_classesToTermPlan/<term_id>')
def get_classesToTermPlan(term_id):
    classes = Classes.query.join(ClassToTermPlan).join(TermPlan).filter(TermPlan.AppliesToTerm==term_id).all()
    return jsonify(Classes.classes_to_dict(classes))

@app.route('/get_subjectsForClass/<class_id>')
def get_subjectsForClass(class_id):
    subjects = Subjects.query.join(TermPlanDetails).join(TermPlan).join(ClassToTermPlan).filter(ClassToTermPlan.ClassId==class_id).all()
    return jsonify(Subjects.subjects_to_dict(subjects))

@app.route('/get_TeachersForSubject/<subject_id>')
def get_TeachersForSubject(subject_id):
    teachers = Teachers.query.join(TeachersToSubjects).filter(TeachersToSubjects.SubjectId==subject_id).filter(Teachers.IsAvailable==True).all()
    return jsonify(Teachers.teachers_to_dict(teachers))

@app.route('/get_ClassRoomsForSubject/<subject_id>')
def get_ClassRoomsForSubject(subject_id):
        preferedClassRooms = ClassRooms.query.filter(ClassRooms.PrimaryCourse==subject_id).all()
        possibleClassRooms = ClassRooms.query.filter(ClassRooms.PrimaryCourse==None).all()
        return jsonify(ClassRooms.classRooms_to_dict(preferedClassRooms+possibleClassRooms))


def _lessons_in_inst(inst_id: int):
        inst =Institutions.query.filter_by(InstitutionId=inst_id).first()
        if inst is None:
            return {}
        default_date = "2000-01-02 "
        normal_break = inst.NormalBreakLength
        lesson_len = inst.NormalLessonLength
        existing_breaks = Breaks.query.filter_by(InstitutionId=inst.InstitutionId).order_by("BreakStartingHour").all()
        break_starts = [
            datetime.datetime.fromisoformat(
                f"{default_date}{b.BreakStartingHour}"
            ) for b in existing_breaks
        ]
        break_ends = [
            datetime.datetime.fromisoformat(
                f"{default_date}{b.BreakEndingHour}"
            ) for b in existing_breaks
        ]
        starting_hour = inst.StartingHour
        ending_hour = inst.EndingHour
        start_obj = datetime.datetime.fromisoformat(
            f"{default_date}{starting_hour}"
        )
        end_obj = datetime.datetime.fromisoformat(
            f"{default_date}{ending_hour}"
        )
        normal_break_td = datetime.timedelta(minutes=normal_break)
        lesson_td = datetime.timedelta(minutes=lesson_len)
        res = []
        lesson_start = start_obj 
        while lesson_start < end_obj:
            res.append(lesson_start)
            lesson_start = lesson_start + lesson_td
            possible_break_start = lesson_start
            if possible_break_start in break_starts:
                curr_break_index = break_starts.index(possible_break_start)
                long_break_duration = break_ends[curr_break_index] - break_starts[curr_break_index]
                lesson_start = lesson_start + long_break_duration
            else:
                lesson_start = lesson_start + normal_break_td
            if lesson_start >= end_obj:
                break
        return res


def _lessons_ends_in_inst(inst_id: int):
        inst =Institutions.query.filter_by(InstitutionId=inst_id).first()
        if inst is None:
            return {}
        default_date = "2000-01-02 "
        normal_break = inst.NormalBreakLength
        lesson_len = inst.NormalLessonLength
        existing_breaks = Breaks.query.filter_by(InstitutionId=inst.InstitutionId).order_by("BreakStartingHour").all()
        break_starts = [
            datetime.datetime.fromisoformat(
                f"{default_date}{b.BreakStartingHour}"
            ) for b in existing_breaks
        ]
        break_ends = [
            datetime.datetime.fromisoformat(
                f"{default_date}{b.BreakEndingHour}"
            ) for b in existing_breaks
        ]
        starting_hour = inst.StartingHour
        ending_hour = inst.EndingHour
        start_obj = datetime.datetime.fromisoformat(
            f"{default_date}{starting_hour}"
        )
        end_obj = datetime.datetime.fromisoformat(
            f"{default_date}{ending_hour}"
        )
        normal_break_td = datetime.timedelta(minutes=normal_break)
        lesson_td = datetime.timedelta(minutes=lesson_len)
        res = []
        lesson_start = start_obj 
        while lesson_start < end_obj:
            lesson_start = lesson_start + lesson_td
            res.append(lesson_start)
            possible_break_start = lesson_start
            if possible_break_start in break_starts:
                curr_break_index = break_starts.index(possible_break_start)
                long_break_duration = break_ends[curr_break_index] - break_starts[curr_break_index]
                lesson_start = lesson_start + long_break_duration
            else:
                lesson_start = lesson_start + normal_break_td
            if lesson_start >= end_obj:
                break
        return res


@app.route("/get_institutions_lessons")
def get_institutions_lessons():
        class_id = flask.request.args["class_id"]
        term_id = flask.request.args["term_id"]
        subject_id = flask.request.args["subject_id"]
        inst_id = int(flask.request.args["institution_id"])
        week_day = flask.request.args["week_day"]
        teacher_id = flask.request.args["teacher_id"]
        class_room_id = flask.request.args["class_room_id"]
        all_lessons_in_day = (
            Schedule.query
            .filter(
                ((Schedule.InTerm == term_id)
                & (Schedule.WeekDay == week_day))
                & ((Schedule.ClassId == class_id) | (Schedule.TeacherId == teacher_id) | (Schedule.ClassRoomId == class_room_id))
            )
            .order_by(Schedule.LessonStartingHour)
            .all()
        )
        possible_beginnings = [
            f"{str(_.hour).zfill(2)}:{str(_.minute).zfill(2)}"
            for _ in _lessons_in_inst(inst_id)
        ]
        possible_ends = [
            f"{str(_.hour).zfill(2)}:{str(_.minute).zfill(2)}"
            for _ in _lessons_ends_in_inst(inst_id)
        ]
        # TODO: Remove at some point when debugging is done
        # http://localhost:5000/get_institutions_lessons?class_id=1&term_id=1&subject_id=2&institution_id=2&week_day=0&teacher_id=1&class_room_id=2
        for sched_entry in all_lessons_in_day:
            begin_time = sched_entry.LessonStartingHour
            end_time = sched_entry.LessonEndingHour
            begin_index = possible_beginnings.index(begin_time)
            end_index = possible_ends.index(end_time)
            del possible_beginnings[begin_index:end_index + 1]
        return jsonify({"lessons": possible_beginnings})


@app.route("/get_lessons_end_hours")
def end_hour_for_lesson():
        class_id = flask.request.args["class_id"]
        term_id = flask.request.args["term_id"]
        subject_id = flask.request.args["subject_id"]
        chosen_lesson_start = flask.request.args["chosen_lesson_start"]
        inst = (
            Institutions.query.join(Terms)
            .filter(Terms.TermId == term_id)
            .first()
            )
        lessons_starts = [
            datetime.time(_.hour, _.minute)
            for _ in _lessons_in_inst(inst.InstitutionId)
        ]
        chosen_lesson_index = lessons_starts.index(
            datetime.time.fromisoformat(chosen_lesson_start)
        )
        lessons_ends = _lessons_ends_in_inst(inst.InstitutionId)
        tpd = (
            TermPlanDetails.query.join(TermPlan)
            .join(ClassToTermPlan)
            .join(Terms)
            .filter(Terms.TermId == term_id)
            .filter(TermPlan.AppliesToTerm == term_id)
            .filter(ClassToTermPlan.ClassId == class_id)
            .filter(TermPlanDetails.SubjectId == subject_id)
            .first()
        )
        res = []
        for possible_ends in range(
            chosen_lesson_index,
            (chosen_lesson_index + tpd.MaxBlockSize)
        ):
            res.append(lessons_ends[possible_ends].strftime("%H:%M"))
        return jsonify({"lesson_ends": res})


@app.route("/get_lesson_preferred_week_day")
def get_lesson_preferred_week_day():
        class_id = flask.request.args["class_id"]
        term_id = flask.request.args["term_id"]
        subject_id = flask.request.args["subject_id"]
        tpd = (
            TermPlanDetails.query.join(TermPlan)
            .join(ClassToTermPlan)
            .join(Terms)
            .filter(Terms.TermId == term_id)
            .filter(TermPlan.AppliesToTerm == term_id)
            .filter(ClassToTermPlan.ClassId == class_id)
            .filter(TermPlanDetails.SubjectId == subject_id)
            .first()
        )
        preferred_distance_in_days = tpd.PreferredDistanceInDays
        last_entry = (
            Schedule.query
            .filter(
                (Schedule.ClassId == class_id)
                & (Schedule.SubjectId == subject_id)
                & (Schedule.InTerm == term_id)
            )
            .order_by(Schedule.WeekDay.desc())
            .first()
        )
        if last_entry is not None:
            res = last_entry.WeekDay + preferred_distance_in_days
        else:
            res = 0  # Monday
        return flask.jsonify({"Preferred_day": res})
