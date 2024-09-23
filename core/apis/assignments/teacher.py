from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, AssignmentStateEnum
from core.libs.exceptions import FyleError
from flask import request
import json

from .schema import AssignmentSchema, AssignmentGradeSchema

teacher_assignments_resources = Blueprint(
    "teacher_assignments_resources", __name__)


@teacher_assignments_resources.route(
    "/assignments", methods=["GET"], strict_slashes=False
)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assignments"""
    header = request.headers.get("X-Principal")
    header = json.loads(header)

    teacher_id = header.get("teacher_id")

    teachers_assignments = Assignment.get_assignments_by_teacher(
        teacher_id=int(teacher_id)
    )
    teachers_assignments_dump = AssignmentSchema().dump(
        teachers_assignments, many=True)
    return APIResponse.respond(data=teachers_assignments_dump)


@teacher_assignments_resources.route(
    "/assignments/grade", methods=["POST"], strict_slashes=False
)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    """Grade an assignment"""
    header = request.headers.get("X-Principal")
    header = json.loads(header)
    teacher_id = header.get("teacher_id")

    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
    assignment_to_be_graded = Assignment.get_by_id(
        _id=grade_assignment_payload.id)

    if not assignment_to_be_graded:
        raise FyleError(404, "Assignment does not exist")
    if assignment_to_be_graded.state == AssignmentStateEnum.DRAFT:
        raise FyleError(400, "Draft assignment cannot be graded")
    if teacher_id != assignment_to_be_graded.teacher_id:
        raise FyleError(
            400, "Assignment can be graded by teacher it is submitted to")

    graded_assignment = Assignment.mark_grade(
        _id=grade_assignment_payload.id,
        grade=grade_assignment_payload.grade,
        auth_principal=p,
    )
    db.session.commit()
    graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
    return APIResponse.respond(data=graded_assignment_dump)
