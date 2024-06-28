# app/models/journeys.py
from datetime import datetime
from mongoengine import Document, StringField, DateTimeField, UUIDField, EmbeddedDocument, EmbeddedDocumentField, ListField, BooleanField, DictField


class Role(EmbeddedDocument):
    name = StringField(required=True)
    permissions = DictField()
    editable = BooleanField(default=True)


class Companion(EmbeddedDocument):
    google_id = StringField(required=True)
    display_name = StringField()
    role = StringField(choices=['owner', 'collaborator', 'leader', 'companion', 'visitor'], required=True)


class Record(EmbeddedDocument):
    message = StringField(required=True)
    level = StringField(choices=['operation', 'design', 'reminder', 'warning'], required=True)
    timestamp = DateTimeField(default=datetime.utcnow)

# Journey Itinerary


class ItineraryItem(EmbeddedDocument):
    time = DateTimeField(required=True)
    location = StringField(required=True)
    description = StringField()
    transportation = StringField()
    additional_info = DictField()


class SubJourney(EmbeddedDocument):
    sub_journey_id = UUIDField(required=True)
    title = StringField(required=True, max_length=100)
    description = StringField()
    itinerary = ListField(EmbeddedDocumentField(ItineraryItem))


class Journeys(Document):
    journey_id = UUIDField(required=True, primary_key=True)
    title = StringField(required=True, max_length=50)
    description = StringField()

    companions = ListField(EmbeddedDocumentField(Companion))
    roles = ListField(EmbeddedDocumentField(Role))
    records = ListField(EmbeddedDocumentField(Record))
    sub_journeys = ListField(EmbeddedDocumentField(SubJourney))

    created_at = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'journeys'}

    def save(self, *args, **kwargs):
        if not self.roles:
            self.roles = [
                Role(name="owner", permissions={'manage_journey': True, 'assign_roles': True, 'edit_content': True}, editable=False),
                Role(name="collaborator", permissions={'manage_journey': True, 'edit_content': True}, editable=True),
                Role(name="leader", permissions={'edit_content': True}, editable=True),
                Role(name="companion", permissions={}, editable=True),
                Role(name="visitor", permissions={}, editable=False)
            ]
        super(Journeys, self).save(*args, **kwargs)