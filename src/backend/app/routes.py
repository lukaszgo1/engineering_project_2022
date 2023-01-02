from flask import jsonify
from app import app, db
from .models import *

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
