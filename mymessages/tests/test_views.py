from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

from myjobs.tests.setup import MyJobsBase
from myjobs.tests.factories import UserFactory
from myjobs.tests.test_views import TestClient
from mymessages.models import Message, MessageInfo
from mymessages.tests.factories import MessageInfoFactory


class MessageViewTests(MyJobsBase):
    def setUp(self):
        super(MessageViewTests, self).setUp()
        self.message = Message.objects.create(subject='subject',
                                              body='body',
                                              message_type='success')
        for group in Group.objects.all():
            self.message.group.add(group.pk)
        self.messageinfo = MessageInfo.objects.create(user=self.user,
                                                      message=self.message)
        self.client = TestClient()
        self.client.login_user(self.user)

    def test_user_post_mark_message_read(self):
        self.client.get(reverse('read'),
                        data={'name': 'message-read-'+str(self.message.id)
                                      + '-'+str(self.user.id)},
                        follow=True,
                        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        m = MessageInfo.objects.get(user=self.user, message=self.message)
        self.assertTrue(m.read)
        self.assertTrue(m.read_at)

    def test_delete_message(self):
        """
        Deleting a MessageInfo should instead mark it as deleted.
        """
        self.assertTrue(self.messageinfo.deleted_on is None)
        self.client.get(reverse('delete'),
                        data={'name': 'message-delete-'+str(self.message.id)
                                      + '-'+str(self.user.id)},
                        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.messageinfo = MessageInfo.objects.get(pk=self.messageinfo.pk)
        self.assertIsNotNone(self.messageinfo.deleted_on)

    def test_auto_page_inbox(self):
        """
        If a "message=%d" parameter is passed on an inbox view, we should
        detect which page that message appears on and select it.
        """
        infos = MessageInfoFactory.create_batch(11, user=self.user)
        request = self.client.get(reverse('inbox'))
        self.assertTrue('Page 1 of 2' in request.content)

        # Messages are displayed in reverse creation order, so the first item
        # in the list is the last item on the last page.
        request = self.client.get(reverse('inbox') +
                                  '?message=%s' % infos[0].message.pk)
        self.assertTrue('Page 2 of 2' in request.content)

    def test_system_message_as_alert(self):
        """
        Only system messages should show as alerts.
        """
        button_class = 'mymessage-read-{message}-{user}'.format(
            message=self.message.pk, user=self.user.pk)
        response = self.client.get(reverse('home'))
        self.assertNotIn(button_class, response.content)

        self.message.system = True
        self.message.save()
        response = self.client.get(reverse('home'))
        self.assertIn(button_class, response.content)
