from TASchedulerApp.models import MyCourse

class CourseService:
    @staticmethod
    def edit_course(course_id, new_data):
        course = MyCourse.objects.get(id=course_id)
        if 'new_name' in new_data:
            course.name = new_data['new_name']
        if 'new_instructor' in new_data:
            course.instructor = new_data['new_instructor']
        if 'new_room' in new_data:
            course.room = new_data['new_room']
        if 'new_time' in new_data:
            course.time = new_data['new_time']
        course.save()
