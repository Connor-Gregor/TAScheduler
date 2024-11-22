from argparse import ArgumentTypeError

#courseId and instructorId exist in the database
#instructorId corresponds to an active instructor
class CourseService:

    def __init__(self):
        pass

    def find_course(self, course_id):
        pass

    def find_instructor(self, instructor_id):
        pass

    def active_instructor(self, instructor_id):
        pass

    def assign_instructor(self, course_id, instructor_id):
        if not course_id:
            raise ArgumentTypeError("Course ID must be provided")
        if not instructor_id:
            raise ArgumentTypeError("Instructor ID must be provided")
        if not self.find_course(course_id):
            raise TypeError("Course does not exist")
        if not self.find_instructor(instructor_id):
            raise TypeError("Instructor does not exist")
        if not self.active_instructor(instructor_id):
            raise TypeError("Instructor is not active")
