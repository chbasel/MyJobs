import datetime
import hashlib
import random
import re

from django.conf import settings
from django.db import models
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

try:
    from django.utils.timezone import now as datetime_now
except ImportError:
    datetime_now = datetime.datetime.now

SHA1_RE = re.compile('^[a-f0-9]{40}$')


class RegistrationManager(models.Manager):
    def activate_user(self, activation_key):
        """
        Searches for activation key in the database. If the key is found and not
        expired,

        Outputs:
        A boolean True and sets the key to 'ALREADY ACTIVATED'.
        Otherwise, returns False to signify theactivation failed.
        
        """
        if SHA1_RE.search(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not profile.activation_key_expired():
                user = profile.user
                from myprofile import signals
                signals.activated.send(sender=self,user=user,
                                       email=profile.email)
                profile.activation_key = self.model.ACTIVATED
                profile.save()
                return user
        return False

    def delete_expired_users(self):
        for profile in self.all():
            try:
                if profile.activation_key_expired():
                    user = profile.user
                    if not user.is_active:
                        user.delete()
                        profile.delete()
            except User.DoesNotExist:
                profile.delete()


class ActivationProfile(models.Model):
    user = models.ForeignKey('myjobs.User', verbose_name="user")
    activation_key = models.CharField(_('activation_key'), max_length=40)
    email = models.EmailField(max_length=255)
    
    
    ACTIVATED = "ALREADY ACTIVATED"
    objects = RegistrationManager()

    def __unicode__(self):
        return "Registration for %s" % self.user

    def activation_key_expired(self):
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == self.ACTIVATED or \
               (self.user.date_joined + expiration_date <= datetime_now())
    activation_key_expired.boolean = True

    def generate_key(self):        
        """
        Generates a random string that will be used as the activation key for a
        registered user.       
        """
        
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        email = self.email
        if isinstance(email, unicode):
            email = email.encode('utf-8')
        activation_key = hashlib.sha1(salt+email).hexdigest()
        return activation_key

    def send_activation_email(self):
        ctx_dict = {'activation_key': self.activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS}
        subject = render_to_string('registration/activation_email_subject.txt',
                                   ctx_dict)
        subject = ''.join(subject.splitlines())
        
        message = render_to_string('registration/activation_email.txt',
                                   ctx_dict)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])

    def save(self, *args, **kwargs):
        if not self.pk:
            self.activation_key = self.generate_key()
        super(ActivationProfile,self).save(*args,**kwargs)

