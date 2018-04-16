import os

from leapp.messaging import BaseMessaging
from leapp.utils.audit import Message, Audit, MessageData, get_messages


class InProcessMessaging(BaseMessaging):
    def __init__(self):
        super(InProcessMessaging, self).__init__()

    def load(self, consumes):
        names = [consume.__name__ for consume in consumes]
        self._data = get_messages(names)

    def produce(self, topic, message):
        message = super(InProcessMessaging, self).produce(topic, message)
        message['event'] = 'new-message'
        message_keys = ('stamp', 'topic', 'actor', 'phase', 'hostname', 'context', 'msg_type')
        audit_keys = ('event', 'stamp', 'data', 'actor', 'phase', 'hostname', 'context')
        message['msg_type'] = message.pop('type')
        payload = message.pop('message')
        msg = Message(**dict(((k, message[k]) for k in message_keys if k in message)))
        audit = Audit(**dict(((k, message[k]) for k in audit_keys if k in message)))
        audit.message = msg
        audit.message.data = MessageData(data=payload['data'], hash_id=payload['hash'])
        audit.store()
        return message

    def load(self, consumes):
        context = os.environ.get('LEAPP_EXECUTION_ID', 'TESTING-CONTEXT')
        self._data = get_messages([consume.__name__ for consume in consumes], context)