from bs4 import BeautifulSoup
import re

from django.core import mail
from django.core.urlresolvers import reverse

from freezegun import freeze_time

from myjobs.tests.factories import UserFactory
from myjobs.tests.setup import MyJobsBase
from mypartners.tests.factories import PartnerFactory, ContactFactory
from mysearches.tests.factories import (
    SavedSearchFactory, SavedSearchDigestFactory, PartnerSavedSearchFactory)
from seo.tests.factories import CompanyFactory


@freeze_time("2016-10-01 10:00:00")
class UnsubscribingTests(MyJobsBase):
    def setUp(self):
        super(UnsubscribingTests, self).setUp()
        self.partner = PartnerFactory(owner=self.company)
        self.contact = ContactFactory(user=self.user, email=self.user.email,
                                      partner=self.partner)
        self.num_emails = len(mail.outbox)

    def assert_unsub_link(self, expected_num_links):
        """
        Grabs the unsubscribe link from the last entry in the outbox. Parses
        the page that it points to and searches for a number of links.
        """
        email_contents = BeautifulSoup(mail.outbox[-1].body)
        try:
            unsub_link = email_contents.find('a',
                                             text="Unsubscribe").attrs['href']
        except:
            # Link not found or link doesn't have an href
            self.assertTrue(False,
                            msg="Could not find unsubscribe link in email")

        # Grab the contents of the link we found and parse it
        response = self.client.get(unsub_link)
        contents = BeautifulSoup(response.content)

        # Magic! If this is a digest, we shouldn't have an unsub link for
        # single searches. If expected_num_links is 2, we'll exclude that.
        expected_link_types = set(["All MyJobs Communication", "All Searches",
                                   "This Search"][:expected_num_links])

        # All links start with the word "Unsubscribe". If that changes, this
        # will need modification as well.
        links = contents.findAll('a', text=re.compile("|".join(
            expected_link_types)))
        self.assertEqual(len(links), expected_num_links,
                         msg=("Expected {0} unsubscribe links, "
                              "found {1}").format(
                             expected_num_links, len(links)))
        found_link_types = {link.text.strip() for link in links}
        self.assertEqual(found_link_types, expected_link_types,
                         ("Expected to find links ({0}), "
                          "found ({1})").format(
                             ", ".join(expected_link_types),
                             ", ".join(found_link_types)))
        self.assertTrue(
            # contents.find returns None, which is falsy, if it can't find
            # what we're searching for.
            contents.find('a', text=re.compile("Cancel")),
            msg="""Didn't find a "Cancel" link""")

    def test_single_search_emails_have_unsubscription_options(self):
        """
        The scheduled, initial, and update emails sent by any type of saved
        search should have an unsubscribe link included. The page pointed to
        by that link should contain three specific unsubscribe links and one
        allowing the user to change their decision.
        """
        # Test both SavedSearch and PartnerSavedSearch.
        for Factory in [SavedSearchFactory, PartnerSavedSearchFactory]:
            search_kwargs = {
                'user': self.user,
            }
            if Factory is PartnerSavedSearchFactory:
                search_kwargs.update({
                    'created_by': self.user, 'provider': self.company,
                    'partner': self.partner
                })
            search = Factory(**search_kwargs)
            # Three methods send email. Test all three.
            for method in ['initial_email', 'send_email', 'send_update_email']:
                method_kwargs = {}
                if method == 'send_update_email':
                    # This method has a required argument.
                    method_kwargs['msg'] = "Update message goes here."

                # If you're reading this, you're probably debugging something.
                # Have fun.
                getattr(search, method)(**method_kwargs)
                self.num_emails += 1
                self.assertEqual(len(mail.outbox), self.num_emails,
                                 msg=("Model {model} did not send "
                                      "an email").format(
                                     model=Factory._meta.model))

                self.assert_unsub_link(expected_num_links=3)

            search.delete()

    def test_digest_email_has_unsubscription_options(self):
        """
        Tests the same basic functionality as the previous method but only
        includes two unsubscribe links.
        """
        digest = SavedSearchDigestFactory(user=self.user)
        SavedSearchFactory(user=self.user)
        digest.send_email()
        self.num_emails += 1
        self.assertEqual(len(mail.outbox), self.num_emails,
                         msg=("Model {model} did not send "
                              "an email").format(
                             model=SavedSearchDigestFactory._meta.model))

        self.assert_unsub_link(expected_num_links=2)

    def test_unsubscribe_with_no_id(self):
        """
        If someone messes with a url and removes the id parameter, we shouldn't
        show a 500 page.
        """
        response = self.client.get(reverse('unsubscribe_confirmation'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('unsubscribe'))
        self.assertEqual(response.status_code, 404)

    def test_unsubscribe_multiple_times(self):
        """
        We used to filter on active saved searches when unsubscribing. Removing
        that filter but only updating the database to toggle is_active to False
        if it isn't already enables users to unsubscribe from a single saved
        search multiple times.

        One example use case is if the user forgot that they unsubscribed from
        a given search already and clicks again. Previously, we would show a
        generic 404 page.
        """
        search = SavedSearchFactory(user=self.user)
        response = self.client.get(reverse('unsubscribe') +
                                   '?id={id_}'.format(id_=search.pk))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('unsubscribe') +
                                   '?id={id_}'.format(id_=search.pk))
        self.assertEqual(response.status_code, 200)
