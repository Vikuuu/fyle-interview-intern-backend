from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, AssignmentStateEnum
from core.models.teachers import Teacher
from core.libs.exceptions import FyleError

from .schema import AssignmentSchema, AssignmentGradeSchema, TeacherSchema

principal_assignments_resources = Blueprint(
    "principal_assignments_resources", __name__)


@principal_assignments_resources.route(
    "/assignments", methods=["GET"], strict_slashes=False
)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assigments."""
    principal_assignments = Assignment.query.filter(
        (Assignment.state == AssignmentStateEnum.SUBMITTED)
        | (Assignment.state == AssignmentStateEnum.GRADED)
    ).all()
    principal_assignments_dump = AssignmentSchema().dump(
        principal_assignments, many=True
    )
    return APIResponse.respond(data=principal_assignments_dump)


@principal_assignments_resources.route(
    "/teachers", methods=["GET"], strict_slashes=False
)
@decorators.authenticate_principal
def list_teachers(p):
    """Returns list of teachers."""
    teachers_list = Teacher.get_all_teachers()
    teachers_list_dump = TeacherSchema().dump(teachers_list, many=True)
    return APIResponse.respond(data=teachers_list_dump)


@principal_assignments_resources.route(
    "/assignments/grade", methods=["POST"], strict_slashes=False
)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    """Grade an assignment."""
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
    assignment_to_be_graded = Assignment.get_by_id(
        _id=grade_assignment_payload.id)

    if assignment_to_be_graded.state == AssignmentStateEnum.DRAFT:
        raise FyleError(400, "Draft assignment cannot be graded")

    graded_assignment = Assignment.mark_grade(
        _id=grade_assignment_payload.id,
        grade=grade_assignment_payload.grade,
        auth_principal=p,
    )
    db.session.commit()
    graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
    return APIResponse.respond(data=graded_assignment_dump)
