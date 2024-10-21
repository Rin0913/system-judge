from datetime import datetime
import mongoengine as me
from mongoengine.queryset.manager import QuerySetManager


class Subtask(me.EmbeddedDocument):
    objects: QuerySetManager

    id = me.SequenceField(primary_key=True)
    task_name = me.StringField(max_length=255, required=True)
    point = me.IntField(required=True)
    script = me.StringField()
    depends_on = me.ListField(me.StringField(max_length=255))

class Playbook(me.EmbeddedDocument):
    objects: QuerySetManager

    id = me.SequenceField(primary_key=True)
    playbook_name = me.StringField(max_length=255, required=True)
    script = me.StringField()

class Problem(me.Document):
    objects: QuerySetManager

    id = me.SequenceField(primary_key=True)

    allow_submission = me.BooleanField(default=False)
    problem_name = me.StringField(max_length=255, default="NewProblem")
    description = me.StringField(default="")
    deadline = me.DateTimeField(default=datetime.utcnow)

    max_cooldown_time = me.IntField(default=10)
    min_cooldown_time = me.IntField(default=0)

    creation_time = me.DateTimeField(default=datetime.utcnow)
    start_time = me.DateTimeField(default=datetime.utcnow)

    subtasks = me.ListField(me.EmbeddedDocumentField(Subtask))
    playbooks = me.ListField(me.EmbeddedDocumentField(Playbook))

    image_name = me.StringField(max_length=1024)
    order = me.ListField(me.StringField(max_length=255))
    is_valid = me.BooleanField(default=True)
