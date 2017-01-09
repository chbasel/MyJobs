from datetime import date
from datetime import datetime
from datetime import timedelta
from djcelery.models import TaskState
from freezegun import freeze_time
from mock import patch
from random import choice

from setup import DirectSEOBase
import tasks


class TasksTestCase(DirectSEOBase):
    @freeze_time("2016-10-01 10:00:00")
    def setUp(self):
        super(TasksTestCase, self).setUp()
        self.midnight = datetime.combine(date.today(), datetime.min.time())
        self.five_pm = self.midnight - timedelta(hours=7)

        self.default_min_expected_throughput = tasks.MIN_EXPECTED_THROUGHPUT
        tasks.MIN_EXPECTED_THROUGHPUT = 5

    def tearDown(self):
        # Prevent this change from impacting any other tests.
        tasks.MIN_EXPECTED_THROUGHPUT = self.default_min_expected_throughput

    @patch('tasks.send_mail')
    def test_check_total_throughput_under(self, mock_send_mail):
        """
        An email should be sent when the minimum total throughput is
        not exceeded.

        """
        for i in range(1, tasks.MIN_EXPECTED_THROUGHPUT):

            TaskState.objects.create(
                task_id=i,
                tstamp=self.midnight,
                name=choice(tasks.SOLR_TASKS),
                state='SUCCESS',
            )
        tasks.check_total_throughput()
        self.assertEqual(mock_send_mail.call_count, 1)

    @patch('tasks.send_mail')
    def test_check_total_throughput_exceeded(self, mock_send_mail):
        """
        No email should be sent when the minimum total throughput is
        exceeded.

        """
        for i in range(1, tasks.MIN_EXPECTED_THROUGHPUT + 2):

            TaskState.objects.create(
                task_id=i,
                tstamp=self.midnight,
                name=choice(tasks.SOLR_TASKS),
                state='SUCCESS',
            )
        tasks.check_total_throughput()
        mock_send_mail.assert_not_called()

