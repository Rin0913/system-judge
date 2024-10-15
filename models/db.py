from datetime import datetime
import mongoengine as me
from mongoengine.queryset.manager import QuerySetManager

class User(me.Document):
    objects: QuerySetManager

    id = me.SequenceField(primary_key=True)
    name = me.StringField(max_length=255, required=True)
    email = me.EmailField(max_length=255, required=True)
    role = me.StringField(max_length=255, default='user')

class Subtask(me.EmbeddedDocument):
    objects: QuerySetManager

    id = me.SequenceField(primary_key=True)
    task_name = me.StringField(max_length=255, required=True)
    points = me.IntField(required=True)
    scripts = me.StringField()

class Playbook(me.EmbeddedDocument):
    objects: QuerySetManager

    id = me.SequenceField(primary_key=True)
    playbook_name = me.StringField(max_length=255, required=True)
    scripts = me.StringField()

class Problem(me.Document):
    objects: QuerySetManager

    id = me.SequenceField(primary_key=True)
    is_valid = me.BooleanField(default=True)
    allow_submission = me.BooleanField(default=False)
    problem_name = me.StringField(max_length=255, default="NewProblem")
    create_time = me.DateTimeField(default=datetime.utcnow)
    start_time = me.DateTimeField(default=None)
    deadline = me.DateTimeField(default=None)
    subtasks = me.ListField(me.EmbeddedDocumentField(Subtask))
    playbooks = me.ListField(me.EmbeddedDocumentField(Playbook))
