"""Social auth models"""
import warnings

from django.db import models
from django.conf import settings

# If User class is overrided, it must provide the following fields,
# or it won't be playing nicely with auth module:
#
#   username   = CharField()
#   last_login = DateTimeField()
#   is_active  = BooleanField()
#
# and methods:
#
#   def is_authenticated():
#       ...
RECOMMENDED_FIELDS = ('username', 'last_login', 'is_active')
RECOMMENDED_METHODS = ('is_authenticated',)

if getattr(settings, 'SOCIAL_AUTH_USER_MODEL', None):
    User = models.get_model(*settings.SOCIAL_AUTH_USER_MODEL.split('.'))
    missing = list(set(RECOMMENDED_FIELDS) -
                   set(User._meta.get_all_field_names())) + \
              [name for name in RECOMMENDED_METHODS
                      if not callable(getattr(User, name, None))]
    if missing:
        warnings.warn('Missing recommended attributes or methods '\
                      'in custom User model: "%s"' % ', '.join(missing))
else:
    from django.contrib.auth.models import User


class UserSocialAuth(models.Model):
    """Social Auth association model"""
    user = models.ForeignKey(User, related_name='social_auth')
    provider = models.CharField(max_length=32)
    uid = models.CharField(max_length=255)
    extra_data = models.TextField(default='', blank=True)

    class Meta:
        """Meta data"""
        unique_together = ('provider', 'uid')

    def __unicode__(self):
        """Return associated user unicode representation"""
        return unicode(self.user)


class Nonce(models.Model):
    """One use numbers"""
    server_url = models.TextField()
    timestamp = models.IntegerField()
    salt = models.CharField(max_length=40)

    def __unicode__(self):
        """Unicode representation"""
        return self.server_url


class Association(models.Model):
    """OpenId account association"""
    server_url = models.TextField()
    handle = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)  # Stored base64 encoded
    issued = models.IntegerField()
    lifetime = models.IntegerField()
    assoc_type = models.CharField(max_length=64)

    def __unicode__(self):
        """Unicode representation"""
        return '%s %s' % (self.handle, self.issued)
