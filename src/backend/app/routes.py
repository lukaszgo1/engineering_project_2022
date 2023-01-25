import csv
import datetime
import io

from flask import jsonify
from app import app, db
from .models import *
import flask
import icalendar

@app.route('/add_institution', methods=['POST'])
def add_institution():
    new_entry = flask.request.get_json()
    institution = Institutions(
        InstitutionName = new_entry['InstitutionName'], StartingHour = new_entry['StartingHour'], EndingHour = new_entry['EndingHour'],
        HasBreaks = new_entry['HasBreaks'], NormalBreakLength = new_entry['NormalBreakLength'], NormalLessonLength = new_entry['NormalLessonLength']
    )
    db.session.add(institution)
    db.session.commit()
    return str(institution.InstitutionId)

@app.route('/add_break', methods=['POST'])
def add_break():
    new_entry = flask.request.get_json()
    new_break = Breaks(
        InstitutionId = new_entry['InstitutionId'], BreakStartingHour = new_entry['BreakStartingHour'], BreakEndingHour = new_entry['BreakEndingHour']
    )
    db.session.add(new_break)
    db.session.commit()
    return str(new_break.BreakId)

@app.route('/add_class', methods=['POST'])
def add_class():
    new_entry = flask.request.get_json()
    new_class = Classes(
        ClassIdentifier = new_entry['ClassIdentifier'], ClassInInstitution = new_entry['ClassInInstitution']
    )
    db.session.add(new_class)
    db.session.commit()
    return str(new_class.ClassId)

@app.route('/add_classToTermPlan', methods=['POST'])
def add_classToTermPlan():
    new_entry = flask.request.get_json()
    classToTermPlan = ClassToTermPlan(
        ClassId = new_entry['ClassId'], TermPlanId = new_entry['TermPlanId']
    )
    db.session.add(classToTermPlan)
    db.session.commit()
    return str(classToTermPlan.ClassToTermPlanId)

@app.route('/add_subject', methods=['POST'])
def add_subject():
    new_entry = flask.request.get_json()
    subject = Subjects(
        SubjectName = new_entry['SubjectName'], TaughtIn = new_entry['TaughtIn']
    )
    db.session.add(subject)
    db.session.commit()
    return str(subject.SubjectId)

@app.route('/add_teacher', methods=['POST'])
def add_teacher():
    new_entry = flask.request.get_json()
    teacher = Teachers(
        FirstName = new_entry['FirstName'], LastName = new_entry['LastName'],
        EmployedIn = new_entry['EmployedIn'], IsAvailable = new_entry['IsAvailable']
    )
    db.session.add(teacher)
    db.session.commit()
    return str(teacher.TeacherId)

@app.route('/add_teacherToSubject', methods=['POST'])
def add_teacherToSubject():
    new_entry = flask.request.get_json()
    teacherToSubject = TeachersToSubjects(
        TeacherId = new_entry['TeacherId'], SubjectId = new_entry['SubjectId']
    )
    db.session.add(teacherToSubject)
    db.session.commit()
    return str(teacherToSubject.TeacherToSubjectId)

@app.route('/add_classRoom', methods=['POST'])
def add_classRoom():
    new_entry = flask.request.get_json()
    classRoom = ClassRooms(
        ClassRoomIdentifier = new_entry['ClassRoomIdentifier'], IsIn = new_entry['IsIn'], PrimaryCourse = new_entry['PrimaryCourse']
    )
    db.session.add(classRoom)
    db.session.commit()
    return str(classRoom.ClassRoomId)

@app.route('/add_term', methods=['POST'])
def add_term():
    new_entry = flask.request.get_json()
    term = Terms(
        TermInInst = new_entry['TermInInst'], TermName = new_entry['TermName'],
        StartDate = datetime.datetime.strptime(new_entry['StartDate'], '%Y-%m-%d'),
        EndDate = datetime.datetime.strptime(new_entry['EndDate'], '%Y-%m-%d')
    )
    db.session.add(term)
    db.session.commit()
    return str(term.TermId)

@app.route('/add_termPlan', methods=['POST'])
def add_termPlan():
    new_entry = flask.request.get_json()
    termPlan = TermPlan(
        AppliesToTerm = new_entry['AppliesToTerm'], TermName = new_entry['TermName']
    )
    db.session.add(termPlan)
    db.session.commit()
    return str(termPlan.TermPlanId)

@app.route('/add_termPlanDetail', methods=['POST'])
def add_termPlanDetail():
    new_entry = flask.request.get_json()
    termPlanDetail = TermPlanDetails(
        TermPlanId = new_entry['TermPlanId'], SubjectId = new_entry['SubjectId'],
        LessonsAmount = new_entry['LessonsAmount'], LessonsWeekly = new_entry['LessonsWeekly'],
        MinBlockSize = new_entry['MinBlockSize'], MaxBlockSize = new_entry['MaxBlockSize'],
        PreferredDistanceInDays = new_entry['PreferredDistanceInDays'], PreferredDistanceInWeeks = new_entry['PreferredDistanceInWeeks']
    )
    db.session.add(termPlanDetail)
    db.session.commit()
    return str(termPlanDetail.TermPlanDetailId)

@app.route('/add_schedule', methods=['POST'])
def add_schedule():
    new_entry = flask.request.get_json()
    schedule = Schedule(
        InstitutionId = new_entry['InstitutionId'], InTerm = new_entry['InTerm'], WeekDay = new_entry['WeekDay'],
        LessonStartingHour = new_entry['LessonStartingHour'], LessonEndingHour = new_entry['LessonEndingHour'], TeacherId = new_entry['TeacherId'],
        SubjectId = new_entry['SubjectId'], ClassId = new_entry['ClassId'], ClassRoomId = new_entry['ClassRoomId']
    )
    db.session.add(schedule)
    db.session.commit()
    return str(schedule.ScheduleId)

@app.route('/delete_institution', methods=['DELETE'])
def delete_institution():
    institution = Institutions.query.filter_by(InstitutionId = flask.request.get_json()['InstitutionId']).first()
    db.session.delete(institution)
    db.session.commit()
    return ''

@app.route('/delete_class', methods=['DELETE'])
def delete_class():
    deleted_class = Classes.query.filter_by(ClassId = flask.request.get_json()['ClassId']).first()
    db.session.delete(deleted_class)
    db.session.commit()
    return ''

@app.route('/delete_classToTermPlan', methods=['DELETE'])
def delete_classtoTermPlan():
    classToTermPlan = ClassToTermPlan.query.filter_by(ClassToTermPlanId = flask.request.get_json()['ClassToTermPlanId']).first()
    db.session.delete(classToTermPlan)
    db.session.commit()
    return ''

@app.route('/delete_subject', methods=['DELETE'])
def delete_subject():
    subject = Subjects.query.filter_by(SubjectId = flask.request.get_json()['SubjectId']).first()
    db.session.delete(subject)
    db.session.commit()
    return ''

@app.route('/delete_teacher', methods=['DELETE'])
def delete_teacher():
    teacher = Teachers.query.filter_by(TeacherId = flask.request.get_json()['TeacherId']).first()
    db.session.delete(teacher)
    db.session.commit()
    return ''

@app.route('/delete_teacherToSubject', methods=['DELETE'])
def delete_teacherToSubject():
    teachertoSubject = TeachersToSubjects.query.filter_by(TeachertosubjectId = flask.request.get_json()['TeacherToSubjectId']).first()
    db.session.delete(teachertoSubject)
    db.session.commit()
    return ''

@app.route('/delete_classRoom', methods=['DELETE'])
def delete_classRoom():
    classRoom = ClassRooms.query.filter_by(ClassRoomId = flask.request.get_json()['ClassRoomId']).first()
    db.session.delete(classRoom)
    db.session.commit()
    return ''

@app.route('/delete_term', methods=['DELETE'])
def delete_term():
    term = Terms.query.filter_by(TermId = flask.request.get_json()['TermId']).first()
    db.session.delete(term)
    db.session.commit()
    return ''

@app.route('/delete_termPlan', methods=['DELETE'])
def delete_termPlan():
    termPlan = TermPlan.query.filter_by(TermPlanId = flask.request.get_json()['TermPlanId']).first()
    db.session.delete(termPlan)
    db.session.commit()
    return ''

@app.route('/delete_termPlanDetail', methods=['DELETE'])
def delete_termPlanDetail():
    termPlanDetail = TermPlanDetails.query.filter_by(TermPlanDetailId = flask.request.get_json()['TermPlanDetailId']).first()
    db.session.delete(termPlanDetail)
    db.session.commit()
    return ''

@app.route('/delete_schedule', methods=['DELETE'])
def delete_schedule():
    schedule = Schedule.query.filter_by(ScheduleId = flask.request.get_json()['ScheduleId']).first()
    db.session.delete(schedule)
    db.session.commit()
    return ''

@app.route('/edit_institution/<institution_id>', methods=['PUT'])
def edit_institution(institution_id):
    new_entry = flask.request.get_json()
    Institutions.query.filter_by(InstitutionId = institution_id).update({
        Institutions.InstitutionName: new_entry['InstitutionName'], Institutions.HasBreaks: new_entry['HasBreaks'],
        Institutions.StartingHour: new_entry['StartingHour'], Institutions.EndingHour: new_entry['EndingHour'],
        Institutions.NormalBreakLength: new_entry['NormalBreakLength'], Institutions.NormalLessonLength: new_entry['NormalLessonLength']
    })
    db.session.commit()
    return ''

@app.route('/edit_class/<class_id>', methods=['PUT'])
def edit_class(class_id):
    new_entry = flask.request.get_json()
    Classes.query.filter_by(ClassId = class_id).update({
        Classes.ClassIdentifier: new_entry['ClassIdentifier']
    })
    db.session.commit()
    return ''

@app.route('/edit_subject/<subject_id>', methods=['PUT'])
def edit_subject(subject_id):
    new_entry = flask.request.get_json()
    Subjects.query.filter_by(SubjectId = subject_id).update({
        Subjects.SubjectName: new_entry['SubjectName']
    })
    db.session.commit()
    return ''

@app.route('/edit_teacher/<teacher_id>', methods=['PUT'])
def edit_teacher(teacher_id):
    new_entry = flask.request.get_json()
    Teachers.query.filter_by(TeacherId = teacher_id).update({
        Teachers.FirstName: new_entry['FirstName'], Teachers.LastName: new_entry['LastName'], Teachers.IsAvailable: new_entry['IsAvailable']
    })
    db.session.commit()
    return ''

@app.route('/edit_classRoom/<class_room_id>', methods=['PUT'])
def edit_classRoom(class_room_id):
    new_entry = flask.request.get_json()
    ClassRooms.query.filter_by(ClassRoomId = class_room_id).update({
        ClassRooms.ClassRoomIdentifier: new_entry['ClassRoomIdentifier'], ClassRooms.PrimaryCourse: new_entry['PrimaryCourse']
    })
    db.session.commit()
    return ''

@app.route('/edit_term/<term_id>', methods=['PUT'])
def edit_term(term_id):
    new_entry = flask.request.get_json()
    Terms.query.filter_by(TermId = term_id).update({
        Terms.TermName: new_entry['TermName'], Terms.StartDate: datetime.datetime.strptime(new_entry['StartDate'], '%Y-%m-%d'),
        Terms.EndDate: datetime.datetime.strptime(new_entry['EndDate'], '%Y-%m-%d')
    })
    db.session.commit()
    return ''

@app.route('/edit_termPlan/<term_plan_id>', methods=['PUT'])
def edit_termPlan(term_plan_id):
    new_entry = flask.request.get_json()
    TermPlan.query.filter_by(TermPlanId = term_plan_id).update({
        TermPlan.TermName: new_entry['TermName']
    })
    db.session.commit()
    return ''

@app.route('/edit_termPlanDetail/<term_plan_detail_id>', methods=['PUT'])
def edit_termPlanDetail(term_plan_detail_id):
    new_entry = flask.request.get_json()
    TermPlanDetails.query.filter_by(TermPlanDetailId = term_plan_detail_id).update({
        TermPlanDetails.SubjectId: new_entry['SubjectId'],
        TermPlanDetails.LessonsAmount: new_entry['LessonsAmount'], TermPlanDetails.LessonsWeekly: new_entry['LessonsWeekly'],
        TermPlanDetails.MinBlockSize: new_entry['MinBlockSize'], TermPlanDetails.MaxBlockSize: new_entry['MaxBlockSize'],
        TermPlanDetails.PreferredDistanceInDays: new_entry['PreferredDistanceInDays'], TermPlanDetails.PreferredDistanceInWeeks: new_entry['PreferredDistanceInWeeks']
    })
    db.session.commit()
    return ''

def calculate_dates(start_date, end_date, week_day):
    lesson_dates = []
    first_day = start_date.weekday()
    last_day = end_date.weekday()
    if week_day > first_day:
        lesson_date = start_date + datetime.timedelta(days = week_day - first_day)
    elif week_day < first_day:
        lesson_date = start_date + datetime.timedelta(days = week_day + 7 - first_day)
    else:
        lesson_date = start_date + datetime.timedelta(days = week_day)
    while lesson_date <= end_date:
        lesson_dates.append(''.join(lesson_date.__str__().split('-')))
        lesson_date += datetime.timedelta(days = 7)
    return lesson_dates


@app.route('/export_to_calendar', methods=['POST'])
def export_to_calendar():
    cal = icalendar.Calendar()
    cal.add('prodid', '-//My calendar product//mxm.dk//')
    cal.add('version', '2.0')
    for id in flask.request.get_json()['lesson_ids']:
        schedule = Schedule.query.join(Subjects, Schedule.SubjectId == Subjects.SubjectId)\
        .join(Terms, Schedule.InTerm == Terms.TermId).filter(Schedule.LessonId == id).with_entities(
        Schedule.WeekDay, Schedule.LessonStartingHour, Schedule.LessonEndingHour, Subjects.SubjectName, Terms.StartDate, Terms.EndDate
        ).first()
        lesson_dates = calculate_dates(schedule.StartDate, schedule.EndDate, schedule.WeekDay)
        for date in lesson_dates:
            event = icalendar.Event()
            event['dtstart'] = ''.join((date, 'T', ''.join(schedule.LessonStartingHour.split(':')), '00'))
            event['dtend'] = ''.join((date, 'T', ''.join(schedule.LessonEndingHour.split(':')), '00'))
            event['summary'] = schedule.SubjectName
            cal.add_component(event)
    in_memory_file = io.BytesIO()
    in_memory_file.write(cal.to_ical())
    content = in_memory_file.getvalue()
    return content


@app.route('/move_from_term', methods=['POST'])
def move_from_term():
    term = Terms.query.filter_by(TermId=flask.request.get_json()['new_term']).first()
    schedules = Schedule.query.filter_by(InTerm=flask.request.get_json()['orig_term']).all()
    for sched in schedules:
        movedSchedule = Schedule(
            InstitutionId=sched.InstitutionId, WeekDay=sched.WeekDay,
            LessonStartingHour=sched.LessonStartingHour, LessonEndingHour=sched.LessonEndingHour,
            TeacherId=sched.TeacherId, SubjectId=sched.SubjectId,
            ClassId=sched.ClassId, ClassRoomId=sched.ClassRoomId,
            InTerm=flask.request.get_json()['new_term']
        )
        db.session.add(movedSchedule)
        db.session.commit()
    termPlans = TermPlan.query.filter_by(AppliesToTerm=flask.request.get_json()['orig_term']).all()
    for orig_term_plan in termPlans:
        movedTermPlan = TermPlan(TermPlanName=f"{orig_term_plan.TermPlanName}_{term.TermName}")
        movedTermPlan.AppliesToTerm = flask.request.get_json()['new_term']
        db.session.add(movedTermPlan)
        db.session.commit()
        origTermPlanDetails = TermPlanDetails.query.filter_by(TermPlanId=orig_term_plan.TermPlanId).all()
        for detail in origTermPlanDetails:
            movedTermPlanDetail = TermPlanDetails(
                TermPlanId=movedTermPlan.TermPlanId, SubjectId=detail.SubjectId,
                LessonsAmount=detail.LessonsAmount, LessonsWeekly=detail.LessonsWeekly,
                MinBlockSize=detail.MinBlockSize, MaxBlockSize=detail.MaxBlockSize,
                PreferredDistanceInDays=detail.PreferredDistanceInDays,
                PreferredDistanceInWeeks=detail.PreferredDistanceInWeeks
            )
            db.session.add(movedTermPlanDetail)
            db.session.commit()
    return ''


@app.route('/export_to_csv', methods=['POST'])
def export_to_csv():
    weekDays = {
        0: 'Poniedziałek',
        1: 'Wtorek',
        2: 'środa',
        3: 'Czwartek',
        4: 'Piątek',
        5: 'Sobota',
        6: 'Niedziela'
    }
    header = [
        "Dzień tygodnia",
        "Godzina rozpoczęcia",
        "Godzina zakończenia",
        "Przedmiot",
        "Grupa",
        "Prowadzący",
        "Sala"
    ]
    rows = []
    for id in flask.request.json['lesson_ids']:
        lesson = Schedule.query.join(Subjects, Schedule.SubjectId == Subjects.SubjectId).join(Classes, Schedule.ClassId == Classes.ClassId)\
            .join(Teachers, Schedule.TeacherId == Teachers.TeacherId).join(ClassRooms, Schedule.ClassRoomId == ClassRooms.ClassRoomId).filter(Schedule.LessonId==id).with_entities(
            Schedule.WeekDay, Schedule.LessonStartingHour, Schedule.LessonEndingHour, Subjects.SubjectName,
            Classes.ClassIdentifier, Teachers.FirstName, Teachers.LastName, ClassRooms.ClassRoomIdentifier
        ).first()
        row = [
            weekDays[lesson.WeekDay],
            lesson.LessonStartingHour,
            lesson.LessonEndingHour,
            lesson.SubjectName,
            lesson.ClassIdentifier,
            ' '.join((lesson.FirstName, lesson.LastName)),
            lesson.ClassRoomIdentifier
        ]
        rows.append(row)
    if not rows:
        return ""
    in_memory_file = io.StringIO(newline="")
    writer = csv.writer(in_memory_file, delimiter="\t")
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    return in_memory_file.getvalue()


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


def _schedule_entries_for_teacher(term_id, teacher_id):
    return Schedule.query.filter(
        (Schedule.InTerm==term_id) & (Schedule.TeacherId==teacher_id)
    ).order_by(Schedule.WeekDay, Schedule.LessonStartingHour).all()


def _schedule_entries_for_class(term_id, class_id):
    return Schedule.query.filter(
        (Schedule.InTerm==term_id) & (Schedule.ClassId==class_id)
    ).order_by(Schedule.WeekDay, Schedule.LessonStartingHour).all()


def _schedule_entries_for_class_room(term_id, class_room_id):
    return Schedule.query.filter(
        (Schedule.InTerm==term_id) & (Schedule.ClassRoomId==class_room_id)
    ).order_by(Schedule.WeekDay, Schedule.LessonStartingHour).all()


@app.route("/get_teacher_lessons")
def get_teacher_lessons():
        teacher_id = flask.request.args["teacher_id"]
        term_id = flask.request.args["term_id"]
        res = _schedule_entries_for_teacher(term_id, teacher_id)
        return flask.jsonify(Schedule.schedule_entries_to_dict(res))


@app.route("/get_class_room_lessons")
def get_class_room_lessons():
        class_room_id = flask.request.args["class_room_id"]
        term_id = flask.request.args["term_id"]
        res = _schedule_entries_for_class_room(term_id, class_room_id)
        return flask.jsonify(Schedule.schedule_entries_to_dict(res))


@app.route("/get_class_lessons")
def get_class_lessons():
        class_id = flask.request.args["class_id"]
        term_id = flask.request.args["term_id"]
        res = _schedule_entries_for_class(term_id, class_id)
        return flask.jsonify(Schedule.schedule_entries_to_dict(res))


def _possible_breaks(inst_id, length):
        inst =Institutions.query.filter_by(InstitutionId=inst_id).first()
        normal_break = inst.NormalBreakLength
        lesson_len = inst.NormalLessonLength
        existing_breaks = Breaks.query.filter_by(InstitutionId=inst_id).order_by("BreakStartingHour").all()
        if existing_breaks:
            starting_hour = existing_breaks[-1].BreakEndingHour
        else:
            starting_hour = inst.StartingHour
        ending_hour = inst.EndingHour
        default_date = "2000-01-02 "
        start_obj = datetime.datetime.fromisoformat(
            f"{default_date}{starting_hour}"
        )
        end_obj = datetime.datetime.fromisoformat(
            f"{default_date}{ending_hour}"
        )
        long_break_td = datetime.timedelta(minutes=length)
        normal_break_td = datetime.timedelta(minutes=normal_break)
        lesson_td = datetime.timedelta(minutes=lesson_len)
        res = []
        lesson_start = (start_obj + normal_break_td + lesson_td)
        while lesson_start < end_obj:
            lesson_start = lesson_start + lesson_td
            possible_break_start = lesson_start
            possible_end = (lesson_start + long_break_td)
            if possible_end >= end_obj:
                break
            lesson_start = lesson_start + normal_break_td
            if lesson_start >= end_obj:
                break
            res.append((possible_break_start, possible_end))
        return res[:-1]


@app.route("/get_possible_breaks")
def get_possible_breaks():
        inst_id = int(flask.request.args["inst_id"])
        break_length = int(flask.request.args["break_length"])
        return flask.jsonify(
            {"Breaks": _possible_breaks(inst_id,  break_length)}
        )


@app.route('/get_institution/<inst_id>')
def get_institution(inst_id):
    inst = Institutions.query.filter_by(InstitutionId=inst_id).first()
    if inst is not None:
        inst = inst.institution_to_dict()
    return jsonify({"item": inst})


@app.route('/get_term/<term_id>')
def get_term(term_id):
    term = Terms.query.filter_by(TermId=term_id).first()
    if term is not None:
        term = term.term_to_dict()
    return jsonify({"item": term})


@app.route('/get_subject/<subject_id>')
def get_subject(subject_id):
    subject = Subjects.query.filter_by(SubjectId=subject_id).first()
    if subject is not None:
        subject = subject.subject_to_dict()
    return jsonify({"item": subject})


@app.route('/get_teacher/<teacher_id>')
def get_teacher(teacher_id):
    teacher = Teachers.query.filter_by(TeacherId=teacher_id).first()
    if teacher is not None:
        teacher = teacher.teacher_to_dict()
    return jsonify({"item": teacher})


@app.route('/get_term_plan/<term_plan_id>')
def get_term_plan(term_plan_id):
    tp = TermPlan.query.filter_by(TermPlanId=term_plan_id).first()
    if tp is not None:
        tp = tp.termPlan_to_dict()
    return jsonify({"item": tp})


@app.route('/get_single_class/<class_id>')
def get_single_class(class_id):
    class_model = Classes.query.filter_by(ClassId=class_id).first()
    if class_model is not None:
        class_model = class_model.class_to_dict()
    return jsonify({"item": class_model})


@app.route('/get_class_to_term_plan/<class_id>')
def get_class_to_term_plan(class_id):
    cttp = ClassToTermPlan.query.filter_by(ClassId=class_id).first()
    if cttp is not None:
        cttp = cttp.classToTermPlan_to_dict()
    return jsonify({"item": cttp})


@app.route('/get_teachersToSubjects/<teacher_id>')
def get_teachersToSubjects(teacher_id):
    teachersToSubjects = TeachersToSubjects.query.filter_by(TeacherId=teacher_id).all()
    return jsonify(TeachersToSubjects.TeachersToSubjects_to_dict(teachersToSubjects))


@app.route('/get_Teachers_not_assigned_to/<teacher_id>')
def get_teachers_not_assigned_to(teacher_id):
    subjects = (
            Subjects.query.outerjoin(TeachersToSubjects)
            .outerjoin(Teachers)
            .filter(Subjects.SubjectId.not_in(TeachersToSubjects.query.with_entities(TeachersToSubjects.SubjectId).filter(TeachersToSubjects.TeacherId==teacher_id)))
            .filter(Subjects.TaughtIn.in_(Teachers.query.with_entities(Teachers.EmployedIn).filter(Teachers.TeacherId==teacher_id)))
            .all()
        )
    return jsonify(Subjects.subjects_to_dict(subjects))


@app.route('/get_single_class_room/<class_room_id>')
def get_single_class_room(class_room_id):
    cr = ClassRooms.query.filter_by(ClassRoomId=class_room_id).first()
    if cr is not None:
        cr = cr.classRoom_to_dict()
    return jsonify({"item": cr})
