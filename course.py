class Course:

    def __init__(self, default_config):
        self.collection = default_config['COURSES_COLLECTION']
        self._id = None
        self.name = None
        self.sn = None
        self.credit = None
        self.fee = None
        self.prop = None
        self.exam_method = None
        self.teacher_id = None
        self.teacher_name = None
        self.timetable = None
        self.response = {'error': None, 'data': None}
        self.debug_mode = default_config['DEBUG']

    def new_course(self, course_data):
        self.response['error'] = None
        if course_data:
            exist_course = self.collection.find_one({'id': course_data['id'], 'sn': course_data['sn']})
            if exist_course:
                self.response['error'] = 'Course already exists..'
                return self.response
            else:
                try:
                    self.collection.insert(course_data)
                    self.response['data'] = True
                except Exception, e:
                    self.print_debug_info(e, self.debug_mode)
                    self.response['error'] = 'Add course error..'
        else:
            self.response['error'] = 'Error..'
        return self.response

    def edit_course(self, course_data):
        self.response['error'] = None
        try:
            self.collection.update({
                '_id': course_data['_id'],
                'sn': course_data['sn']
            }, {'$set': course_data}, upsert=False)
        except Exception, e:
            self.print_debug_info(e, self.debug_mode)
            self.response['error'] = 'Course update error..'

        return self.response


    def get_course(self, cid, sn):
        self.response['error'] = None
        try:
            course = self.collection.find_one({'id': cid, 'sn': sn})
            self.response['data'] = course
        except Exception, e:
            self.print_debug_info(e, self.debug_mode)
            self.response['error'] = 'Course not found..'
        return self.response

    def get_courses(self, cid=None, sn=None, name=None, teacher_id=None, search=None):
        self.response['error'] = None
        cond = {}
        if cid is not None:
            cond['id'] = cid
        if sn is not None:
            cond['sn'] = sn
        if name is not None:
            cond['name'] = name
        if teacher_id is not None:
            cond['teacher_id'] = teacher_id
        if search is not None:
            cond = {'$or': [{'name': {'$regex': search, '$options': 'i'}}]}
        try:
            cursor = self.collection.find(cond)
            self.response['data'] = []
            for course in cursor:
                self.response['data'].append(course)
        except Exception, e:
            self.print_debug_info(e, self.debug_mode)
            self.response['error'] = 'Courses not found..'
        return self.response

    @staticmethod
    def print_debug_info(msg, show=False):
        if show:
            import sys
            import os

        error_color = '\033[32m'
        error_end = '\033[0m'

        error = {'type': sys.exc_info()[0].__name__,
                 'file': os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename),
                 'line': sys.exc_info()[2].tb_lineno,
                 'details': str(msg)}

        print error_color
        print '\n\n---\nError type: %s in file: %s on line: %s\nError details: %s\n---\n\n'\
              % (error['type'], error['file'], error['line'], error['details'])
        print error_end
