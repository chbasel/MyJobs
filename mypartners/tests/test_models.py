# -*- coding: utf-8 -*-
from os import path

from django.core.files import File
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from myjobs.tests.setup import MyJobsBase
from myjobs.models import User
from myjobs.tests.factories import UserFactory
from seo.tests.factories import CompanyFactory
from mypartners.tests.factories import (ContactFactory, ContactRecordFactory,
                                        LocationFactory, PartnerFactory,
                                        TagFactory, PRMAttachmentFactory)
from mypartners.models import (Contact, Location, Partner, PRMAttachment,
                               Status, OutreachEmailDomain, CommonEmailDomain,
                               ContactRecord)
from mysearches.models import PartnerSavedSearch
from mysearches.tests.factories import PartnerSavedSearchFactory


class MyPartnerTests(MyJobsBase):
    def setUp(self):
        super(MyPartnerTests, self).setUp()
        self.company = CompanyFactory()
        self.partner = PartnerFactory(owner=self.company)
        self.contact = ContactFactory(partner=self.partner)

    def test_contact_to_partner_relationship(self):
        """
        Tests adding a contact to partner's contacts list and tests
        primary_contact. Also tests if the contact gets deleted the partner
        stays and turns primary_contact to None.
        """
        self.assertEqual(Contact.objects.filter(partner=self.partner).count(),
                         1)

        self.partner.primary_contact = self.contact
        self.partner.save()
        self.assertIsNotNone(self.partner.primary_contact)

        # making sure contact is the contact obj vs a factory object.
        contact = Contact.objects.get(name=self.contact.name)
        contact.delete()

        partner = Partner.objects.get(name=self.partner.name)
        self.assertFalse(Contact.objects.filter(
            partner=partner, archived_on__isnull=True))
        self.assertIsNone(partner.primary_contact)

    def test_contact_user_relationship(self):
        """
        Tests adding a User to Contact. Then tests to make sure User cascading
        delete doesn't delete the Contact and instead turns Contact.user to
        None.
        """
        self.contact.user = UserFactory(email=self.contact.email)
        self.contact.save()

        self.assertIsNotNone(self.contact.user)
        self.assertEqual(self.contact.name, self.contact.__unicode__())

        user = User.objects.get(email=self.contact.email)
        user.delete()

        contact = Contact.objects.get(name=self.contact.name)
        self.assertIsNone(contact.user)

    def test_location_to_contact_relationship(self):
        """
        Tests adding a Location to Contact.
        """
        location = LocationFactory()

        # make sure that we can add a location to a contact
        self.contact.locations.add(location)
        self.contact.save()
        self.assertTrue(len(self.contact.locations.all()) > 0)

        # ensure that we can remove a location
        self.contact.locations.remove(location)
        self.assertTrue(len(self.contact.locations.all()) == 0)

        # make sure that removing a location from a contact doesn't delete that
        # location entirely
        self.assertIn(location, Location.objects.all())

    def test_bad_filename(self):
        """
        Confirms that non-alphanumeric or underscore characters are being
        stripped from file names.

        """
        actual_file = path.join(path.abspath(path.dirname(__file__)), 'data',
                                'test.txt')
        f = File(open(actual_file))
        filenames = [
            ('zz\\x80\\xff*file(copy)na.me.htm)_-)l',
             'zzx80xfffilecopyname.htm_l'),
            ('...', 'unnamed_file'),
            ('..', 'unnamed_file'),
            ('../../file.txt', 'file.txt'),
            ('../..', 'unnamed_file'),
            ('\.\./file.txt', 'file.txt'),
            ('fiяыle.txt', 'file.txt')
        ]

        for filename, expected_filename in filenames:
            f.name = filename
            prm_attachment = PRMAttachmentFactory(attachment=f)
            result = PRMAttachment.objects.get(
                attachment__contains=expected_filename)
            result.delete()

    def test_partner_saved_search_delete_contact(self):
        """
        When a contact gets deleted, we should log it and disable any partner
        saved searches for that contact
        """
        user = UserFactory(email='user@example.com')
        self.contact.user = user
        self.contact.save()
        self.contact = Contact.objects.get(pk=self.contact.pk)
        owner = UserFactory(email='owner@example.com')

        partner_saved_search = PartnerSavedSearchFactory(created_by=owner,
                                                         provider=self.company,
                                                         partner=self.partner,
                                                         user=user,
                                                         notes='')
        self.assertTrue(partner_saved_search.is_active)
        self.contact.delete()
        partner_saved_search = PartnerSavedSearch.objects.get(
            pk=partner_saved_search.pk)
        self.assertFalse(partner_saved_search.is_active)
        self.assertTrue(self.contact.name in partner_saved_search.notes)

    def test_tag_added_to_taggable_models(self):
        tag = TagFactory(company=self.company)
        tag.save()
        tag2 = TagFactory(name="bar", company=self.company)
        tag2.save()
        cr = ContactRecordFactory(partner=self.partner)

        # Add tag to models
        cr.tags.add(tag)
        self.partner.tags.add(tag)
        self.partner.save()
        self.contact.tags.add(tag)
        self.contact.save()

        # Check to make sure it was added
        self.assertEquals(1, len(cr.tags.all()))
        self.assertEquals(1, len(self.partner.tags.all()))
        self.assertEquals(1, len(self.contact.tags.all()))

        # Add a 2nd tag and check
        self.partner.tags.add(tag2)
        self.partner.save()
        self.assertEquals(2, len(self.partner.tags.all()))

    def test_contact_archived(self):
        """Test that attempting to delete a contact archives it instead."""

        self.assertFalse(self.contact.archived_on)
        self.contact.archive()
        self.assertEqual(Contact.objects.count(), 0)
        self.assertEqual(Contact.all_objects.count(), 1)
        self.assertTrue(self.contact.archived_on)

    def test_archived_manager_weirdness(self):
        """
        Demonstrates that archived instances are returned by the
        ArchivedModel.all_objects manager, not the standard
        ArchivedModel.objects.
        """
        self.partner.archive()
        # Try retrieving the archived partner using both managers. The "objects"
        # manager excludes archived instances so an exception is raised.
        self.assertRaises(Partner.DoesNotExist,
                          lambda: Partner.objects.get(pk=self.partner.pk))
        Partner.all_objects.get(pk=self.partner.pk)

        # This contact has not been archived (as we demonstrate in a few lines)
        # but is excluded by the "objects" manager as its partner has been
        # archived.
        self.assertRaises(Contact.DoesNotExist,
                          lambda: Contact.objects.get(pk=self.contact.pk))
        self.contact = Contact.all_objects.get(pk=self.contact.pk)
        self.assertFalse(self.contact.archived_on)

        # The manager used by related objects in this instance excludes
        # archived partners. As it's basically a Partner.objects.get(id=...),
        # this fails.
        self.assertRaises(Partner.DoesNotExist, lambda: self.contact.partner)
        self.assertEqual(self.contact.partner_id, self.partner.pk)

    def test_archive_primary_contacts(self):
        """
        Archiving a primary contact should clear that contact's status as the
        partner's primary contact. Doing otherwise raises exceptions.
        """
        self.partner.primary_contact = self.contact
        self.partner.save()
        self.partner.primary_contact.archive()
        self.partner = Partner.objects.get(pk=self.partner.pk)
        self.partner.primary_contact

    def test_models_approved(self):
        """
        By default, new partners, contacts, and contactrecords should be
        approved.
        """

        contactrecord = ContactRecordFactory(partner=self.partner)

        for instance in (self.contact, self.partner, contactrecord):
            self.assertEqual(instance.approval_status.code, Status.APPROVED)

    def test_contact_locations(self):
        """
        Test that `get_contact_locations` returns a properly formatted string.
        """
        ny = LocationFactory.create_batch(2, city="Albany", state="NY")
        il = LocationFactory.create(city="Chicago", state="IL")
        mo = LocationFactory.create(city="St. Louis", state="MO")

        contacts = ContactFactory.create_batch(4, partner=self.partner)
        for contact, location in zip(contacts, ny + [il, mo]):
            contact.locations.add(location)

        self.assertEqual("Chicago, IL; St. Louis, MO; Albany, NY",
                         "; ".join(self.partner.get_contact_locations()))

    def test_uncommon_outreach_email_domain(self):
        """
        Adding an uncommon email domain for outreach to a company should  work.
        """

        # data migrations aren't run during tests, so we populate manually
        CommonEmailDomain.objects.create(domain="gmail.com")

        with self.assertRaises(ValidationError):
            OutreachEmailDomain.objects.create(company=self.company,
                                               domain="gmail.com")

    def test_outreach_domain_unique_to_company(self):
        """
        Allowed domains should be unique within a company, but not necessarily
        across PRM.
        """

        OutreachEmailDomain.objects.create(company=self.company,
                                           domain="foo.bar")

        # duplicate domains allowed between companies
        company = CompanyFactory.create(name="A Whole New World")
        OutreachEmailDomain.objects.create(company=company,
                                           domain="foo.bar")

        # dupliate domains disallowed within the same company
        with self.assertRaises(IntegrityError):
            OutreachEmailDomain.objects.create(company=self.company,
                                               domain="foo.bar")

    def test_contact_record_counts_vs_list(self):
        """
        ContactRecord counts for Communication Records and Referals
        should match summed counts from contacts.
        """
        contacts = ContactFactory.create_batch(4)
        contacts[0].name = 'Other name'
        contacts[1].email = 'other@email.com'
        contacts[2].partner = PartnerFactory(name='Other Partner')
        for contact in contacts:
            ContactRecordFactory.create(contact_type="job",
                                        contact=contact,
                                        partner=contact.partner)
            ContactRecordFactory.create(contact_type = 'email',
                                        contact=contact,
                                        partner=contact.partner)

        contacts[0].email = 'changed@email.com'
        ContactRecordFactory.create(contact_type = 'email',
                                    contact=contacts[0],
                                    partner=contact.partner)


        queryset = ContactRecord.objects.all()
        self.assertEqual(queryset.count(), 9)

        contacts = list(queryset.contacts)
        sum_referrals = sum([contact['referrals'] for contact in contacts])
        sum_records = sum([contact['records'] for contact in contacts])
        self.assertEqual(sum_referrals, queryset.referrals)
        self.assertEqual(sum_records, queryset.communication_activity.count())


    def test_contact_record_report_numbers(self):
        """
        Contact records have properties which represent various aggregated
        values. This test ensures that given a number of contact records, those
        aggregated numbers are correct.
        """

        email_record = ContactRecordFactory(contact_type="email",
                                           partner=self.partner,
                                           contact=self.contact)

        job_record = ContactRecordFactory(contact_type="job",
                                           partner=self.partner,
                                           contact=self.contact,
                                           job_applications=10,
                                           job_interviews=6,
                                           job_hires=5)
        phone_record = ContactRecordFactory(contact_type="phone",
                                            partner=self.partner,
                                            contact=ContactFactory(name="Joe"))

        records = ContactRecord.objects.all()

        self.assertEqual(len(records), 3)
        self.assertEqual(len(records.contacts), 2)
        # job follow ups don't count as comm activity
        self.assertEqual(len(records.communication_activity), 2)
        # only job follow ups count as referrals
        self.assertEqual(records.referrals, 1)
        self.assertEqual(records.applications, 10)
        self.assertEqual(records.interviews, 6)
        self.assertEqual(records.hires, 5)
        self.assertEqual(records.emails, 1)
        self.assertEqual(records.calls, 1)

