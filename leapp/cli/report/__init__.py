import os

from leapp.exceptions import CommandError
from leapp.utils.audit import get_connection
from leapp.utils.clicmd import command, command_opt
from leapp.cli.upgrade import fetch_last_upgrade_context


def fetch_upgrade_report_messages(context_id):
    """
    :return: All upgrade messages of type "LeappReport" withing the given context
    """
    with get_connection(None) as db:
        cursor = db.execute(
            "SELECT message_data_hash FROM message WHERE type = 'CheckResult' and context = '%s'" % context_id)
        reports = cursor.fetchall()
        report_msg_ids = [report[0] for report in reports]
        cursor = db.execute(
            "SELECT data FROM message_data WHERE hash in (%s)" % ','.join('?'*len(report_msg_ids)), report_msg_ids)
        cursor.row_factory = lambda cursor, row: row[0]
        report_msgs = cursor.fetchall()
        if report_msgs:
            return report_msgs
    return None


@command('report', help='Create report for last execution (default) or specific execution id using --id ID')
@command_opt('id')
def report(args):
    if os.getuid():
        raise CommandError('This command has to be run under the root user.')

    id = args.id or fetch_last_upgrade_context()[0]

    if not id:
        raise CommandError('No previous Leapp run of the requested context {} found'.format(id))

    messages = fetch_upgrade_report_messages(id)
    if not messages:
        raise CommandError('No upgrade report messages found for context {}'.format(id))
    print(messages)


@command('list-runs', help='List previous Leapp upgrade executions')
def report(args):
    ctx_id, details = fetch_last_upgrade_context()
    print('Context ID: {} - details: {}'.format(ctx_id, details))
