from datetime import datetime
import mongoengine as me
from mongoengine.queryset.manager import QuerySetManager

class WGConf(me.EmbeddedDocument):
    objects: QuerySetManager

    id = me.IntField(default=20000)
    user_conf = me.StringField(required=True)
    judge_conf = me.StringField(required=True)

class User(me.Document):
    objects: QuerySetManager

    id = me.SequenceField(primary_key=True)
    name = me.StringField(max_length=255, required=True)
    wireguard_conf = me.EmbeddedDocumentField(WGConf)

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

    image_name = me.StringField(max_length=1024)
    order = me.ListField(me.StringField(max_length=255))
