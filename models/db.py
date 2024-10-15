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
    point = me.IntField(required=True)
    script = me.StringField()

class Playbook(me.EmbeddedDocument):
    objects: QuerySetManager

    id = me.SequenceField(primary_key=True)
    playbook_name = me.StringField(max_length=255, required=True)
    script = me.StringField()

class Dependency(me.EmbeddedDocument):
    objects: QuerySetManager

    id = me.SequenceField(primary_key=True)
    prerequisite = me.StringField(max_length=255, required=True)
    task = me.StringField(max_length=255, required=True)

class Problem(me.Document):
    objects: QuerySetManager

    id = me.SequenceField(primary_key=True)
    is_valid = me.BooleanField(default=True)
    allow_submission = me.BooleanField(default=False)
    problem_name = me.StringField(max_length=255, default="NewProblem")
    create_time = me.DateTimeField(default=datetime.utcnow)
    start_time = me.DateTimeField(default=datetime.utcnow)
    deadline = me.DateTimeField(default=datetime.utcnow)
    subtasks = me.ListField(me.EmbeddedDocumentField(Subtask))
    playbooks = me.ListField(me.EmbeddedDocumentField(Playbook))
    dependencies = me.ListField(me.EmbeddedDocumentField(Dependency))
    image_name = me.StringField(max_length=1024)
