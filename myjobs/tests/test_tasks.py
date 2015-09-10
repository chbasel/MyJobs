import datetime

from setup import MyJobsBase
from myjobs.models import STOP_SENDING, BAD_EMAIL, EmailLog, User
from myjobs.tests.factories import UserFactory
from tasks import process_batch_events


class TaskTests(MyJobsBase):
    @staticmethod
    def make_email_logs(email, event, received, processed, number):
        for _ in range(number):
            EmailLog.objects.create(
                email=email, event=event, received=received,
                processed=processed
            )

    def test_required_number_of_bad_events(self):
        now = datetime.datetime.now()
        event = BAD_EMAIL[0]
        u = UserFactory(is_verified=True, opt_in_myjobs=True)
        self.make_email_logs(u.email, event, now, False, 2)
        process_batch_events()

        u = User.objects.get(pk=u.pk)
        self.assertEqual(u.deactivate_type, 'none')

        self.make_email_logs(u.email, event, now, False, 3)
        process_batch_events()

        u = User.objects.get(pk=u.pk)
        self.assertEqual(u.deactivate_type, event)

    def test_bad_events_deactivate_user(self):
        now = datetime.datetime.now()
        for event in STOP_SENDING + BAD_EMAIL:
            u = UserFactory(is_verified=True, opt_in_myjobs=True)
            self.make_email_logs(u.email, event, now, False, 3)
            process_batch_events()

            u = User.objects.get(pk=u.pk)
            self.assertEqual(u.deactivate_type, event)
            # Users start this test case with is_verified=True
            # is_verified should only change if the modifying event
            # is a block or drop
            self.assertEqual(u.is_verified, event in STOP_SENDING)
            self.assertFalse(u.opt_in_myjobs)

            infos = u.messageinfo_set.all()
            self.assertEqual(len(infos), 1)
            message = infos[0].message

            if u.deactivate_type in STOP_SENDING:
                text = 'stop communications'
            else:
                text = 'Attempts to send messages to'
            self.assertTrue(text in message.body)

            EmailLog.objects.all().delete()
            u.delete()

    def test_event_with_no_user(self):
        EmailLog.objects.create(email='test@example.com', event=STOP_SENDING[0],
                                received=datetime.datetime.now(),
                                processed=False)

        process_batch_events()

        log = EmailLog.objects.get()
        self.assertTrue(log.processed)
