import os
from functools import wraps
from flask import Flask, render_template, abort, url_for, request, flash, session, redirect
import user
import course

app = Flask('EAS')
app.config.from_object('config')


def login_required(role=None):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not session.get('user'):
                flash('You must be logged in..', 'error')
                return redirect(url_for('login'))
            if role == 'admin' and session.get('user').get('role') != 'admin':
                flash('You are not an administrator..', 'error')
                return redirect(url_for('index'))
            elif role == 'teacher' and session.get('user').get('role') != 'teacher':
                flash('You are not a teacher..', 'error')
                return redirect(url_for('index'))
            elif role == 'student' and session.get('user').get('role') != 'student':
                flash('You are not a student..', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return wrapped
    return wrapper


@app.route('/')
@login_required()
def index():
    return render_template('index.html', active_nav='index')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = False
    error_type = 'validate'
    if request.method == 'POST':
        username = request.form.get('login-username')
        password = request.form.get('login-password')
        if not username or not password:
            error = True
        else:
            user_data = userClass.login(username.lower().strip(), password)
            if user_data['error']:
                error = True
                error_type = 'login'
                flash(user_data['error'], 'error')
            else:
                userClass.start_session(user_data['data'])
                return redirect(url_for('index'))
    return render_template('login_and_register/login.html')


@app.route('/logout')
def logout():
    userClass.logout()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = False
    error_type = 'validate'
    if request.method == 'POST':
        username = request.form.get('reg-username')
        password = request.form.get('reg-password')
        name     = request.form.get('reg-name')
        role     = request.form.get('reg-role')
        if not username or not password or not name or not role:
            error = True
        else:
            post_data = {
                '_id': username.lower().strip(),
                'pass': password,
				'name': name,
				'role': role,
            }
            user = userClass.save_user(post_data)
            if user['error']:
                error = True
                flash(user_data['error'], 'error')
            else:
                flash('Inserted!', 'success')
    return render_template('login_and_register/register.html')


@app.route('/admin/course/new', methods=['GET', 'POST'])
@login_required('admin')
def new_course():
    if request.method == 'POST':
        cid           = request.form.get('course-id')
        name          = request.form.get('course-name')
        sn            = request.form.get('course-sn')
        credit        = request.form.get('course-credit')
        fee           = request.form.get('course-fee')
        capacity      = request.form.get('course-capacity')
        prop          = request.form.get('course-property')
        exam_method   = request.form.get('course-exam-method')
        teacher_id    = request.form.get('teacher-id')
        teacher_name  = request.form.get('teacher-name')
        timetable     = request.form.get('timetable')
        is_edit_model = request.form.get('is-edit-model')

        post_data = {
            'id': cid,
            'name': name,
            'sn': sn,
            'credit': float(credit),
            'fee': float(fee),
            'capacity': int(capacity),
            'rest': 0,
            'prop': prop,
            'exam_method': exam_method,
            'teacher_id': teacher_id,
            'teacher_name': teacher_name,
            'timetable': timetable,
        }

        if is_edit_model == 'yes':
            response = courseClass.edit_course(post_data)
            if response['error']:
                error = True
                flash(response['error'], 'error')
            else:
                flash('New course added!', 'success')
            return redirect(url_for('edit_course', course_id=cid, course_sn=sn))
        else:
            response = courseClass.new_course(post_data)
            if response['error']:
                error = True
                flash(response['error'], 'error')
            else:
                flash('New course added!', 'success')

    return render_template('login_and_register/new_course.html')


@app.route('/admin/course/edit/<course_id>/<course_sn>')
def edit_course(course_id, course_sn):
    course = courseClass.get_course(course_id, course_sn)
    if course['error']:
        flash(course['error'], 'error')
        return redirect(url_for('new_course'))

    return render_template('login_and_register/edit_course.html', course=course['data'])


@app.route('/personal')
@login_required()
def personal():
    return redirect(url_for('profile'))


@app.route('/personal/profile')
@login_required()
def profile():
    return render_template('personal/profile.html', active_nav='personal', active_tab='profile')


@app.route('/personal/profile-movement')
@login_required()
def profile_movement():
    return render_template('personal/profile_movement.html', active_nav='personal', active_tab='profile-movement')


@app.route('/personal/rewards-and-punishments')
@login_required()
def rewards_and_punishments():
    return render_template('personal/rewards_and_punishments.html', active_nav='personal', active_tab='rewards-and-punishments')


@app.route('/courses')
@login_required()
def courses():
    return redirect(url_for('subject_timetable'))


@app.route('/courses/subject-timetable')
@login_required()
def subject_timetable():
    return render_template('courses/subject-timetable.html', active_nav='courses', active_tab='subject-timetable')


@app.route('/courses/examination-results')
@login_required('student')
def examination_results_query():
    return render_template('courses/examination_results.html', active_nav='courses', active_tab='examination-results')


@app.route('/apply-for-courses')
@login_required('student')
def apply_for_courses():
    return redirect(url_for('select_scheme'))


@app.route('/apply-for-courses/select-scheme')
@login_required('student')
def select_scheme():
    return render_template('apply_for_courses/schemes_list.html', active_nav='apply-for-courses')


@app.route('/apply-for-courses/select-course-type')
@login_required('student')
def select_course_type():
    return render_template('apply_for_courses/types_list.html', active_nav='apply-for-courses')


@app.route('/apply-for-courses/select-course-id')
@login_required('student')
def select_course_id():
    cursor = list(courseClass.collection.aggregate([{'$group': {'_id': {'id': '$id', 'name': '$name', 'credit': '$credit', 'prop': '$prop', 'fee': '$fee', 'exam_method': '$exam_method'}}}]))
    courses = []
    for course in cursor:
        courses.append({
            'id': course['_id']['id'],
            'name': course['_id']['name'],
            'credit': course['_id']['credit'],
            'fee': course['_id']['fee'],
            'prop': course['_id']['prop'],
            'exam_method': course['_id']['exam_method'],
            })
    return render_template('apply_for_courses/courses_ids_list.html', active_nav='apply-for-courses', courses=courses)


@app.route('/apply-for-courses/select-course-sn/<course_id>')
@login_required('student')
def select_course_sn(course_id):
    response = courseClass.get_courses(cid=course_id)
    if response['error']:
        error = True
        flash(response['error'], 'error')
        abort(404)

    return render_template('apply_for_courses/course_sns_list.html', active_nav='apply-for-courses', courses=response['data'])


@app.route('/record-score')
@login_required('teacher')
def record_score():
    pass


@app.route('/messages')
@login_required()
def messages_list():
    return render_template('messages/messages_list.html', active_nav='messages')


@app.route('/messages/<message_id>')
@login_required()
def message_detail(message_id):
    return render_template('messages/message_detail.html', active_nav='messages')


userClass = user.User(app.config)
courseClass = course.Course(app.config)

if not app.config['DEBUG']:
    import logging
    from logging import FileHandler
    file_handler = FileHandler(app.config['LOG_FILE'])
    file_handler.setLevel(logging.WARNING)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)),
            debug=app.config['DEBUG'], threaded=True)
