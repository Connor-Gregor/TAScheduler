from TASchedulerApp.models import MyCourse, MyUser

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

def assign_instructor_and_tas(course_id, instructor_id, ta_id):
    try:
        course = MyCourse.objects.get(id=course_id)

        if instructor_id:
            instructor = MyUser.objects.get(id=instructor_id, role='Instructor')
            course.instructor = instructor

        if ta_id:
            ta = MyUser.objects.get(id=ta_id, role='TA')
            course.tas.set([ta])

        course.save()

        return {"success": True, "message": "Assignments updated successfully."}
    except MyCourse.DoesNotExist:
        return {"success": False, "message": "Course not found."}
    except MyUser.DoesNotExist:
        return {"success": False, "message": "Instructor or TA not found."}
    except Exception as e:
        return {"success": False, "message": str(e)}
