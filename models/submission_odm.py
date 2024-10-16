from datetime import datetime
import mongoengine as me
from mongoengine.queryset.manager import QuerySetManager


class SubtaskResult(me.EmbeddedDocument):
    objects: QuerySetManager

    task_name = me.StringField(required=True)
    point = me.IntField(required=True)
    log = me.StringField(default="No output.")

class Submission(me.Document):
    objects: QuerySetManager

    id = me.SequenceField(primary_key=True)
    status = me.StringField(max_length=16, default="pending")
    user_id = me.IntField(required=True)
    problem_id = me.IntField(required=True)
    subtask_results = me.ListField(me.EmbeddedDocumentField(SubtaskResult))
    point = me.IntField()
    creation_time = me.DateTimeField(default=datetime.utcnow)
