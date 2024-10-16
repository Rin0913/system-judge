from datetime import datetime
import mongoengine as me
from mongoengine.queryset.manager import QuerySetManager


class WGConf(me.EmbeddedDocument):
    objects: QuerySetManager

    id = me.IntField(required=True)
    user_conf = me.StringField(required=True)
    judge_conf = me.StringField(required=True)
    creation_time = me.DateTimeField(default=datetime.utcnow)

class User(me.Document):
    objects: QuerySetManager

    id = me.SequenceField(primary_key=True)
    name = me.StringField(max_length=255, required=True)
    wireguard_conf = me.EmbeddedDocumentField(WGConf)
    credential = me.StringField(max_length=1024)
