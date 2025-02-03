from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Thread import Thread
from .Loom import Loom


class Message(BaseWithTimeZoneModel):
    message_id = CharField(null=True)
    thread = ForeignKeyField(Thread, backref='threads', null=True)
    text = TextField()
    sender = CharField()
    type = CharField()
    state = CharField(default='seen')

    messageable_id = CharField()
    messageable_type = CharField()


    def update_state(self, state):
        self.state = state
        self.save()

    def get_messageable(self):
        model_class = self.get_model_from_type()

        return model_class.get_by_id(self.messageable_id) if model_class else None

    def get_model_from_type(self):

        # This method should return the model class based on the messageable_type
        type_mapping = {
            'App\\Models\\Loom': Loom,
        }

        return type_mapping.get(self.messageable_type)

    class Meta:
        table_name = 'messages'
