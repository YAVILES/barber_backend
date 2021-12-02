import uuid
from django.contrib.gis.db import models as geo_models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

# Create your models here.
from apps.core.models import ModelBase


class UserManager(BaseUserManager):
    def _create_user(self, username, name, last_name, password, database='default', **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username:
            raise ValueError(_('The Username must be set'))
        username = self.normalize_email(username)
        obj = User(username=username, name=name, last_name=last_name, **extra_fields)
        obj.set_password(password)
        obj.save(using=database)
        return obj

    def create_user(self, username, name=None, last_name=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, name, last_name, password, **extra_fields)

    def create_superuser(self, username, name, last_name, password, database='default', **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, name, last_name, password, database, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, ModelBase):
    INACTIVE = 0
    ACTIVE = 1
    SUSPEND = 2
    STATUS = (
        (ACTIVE, _('activo')),
        (INACTIVE, _('inactivo')),
        (SUSPEND, _('suspendo')),
    )
    username = models.CharField(max_length=255, verbose_name=_('username'), null=True, unique=True)
    email = models.EmailField(verbose_name=_('email'), unique=True)
    name = models.CharField(max_length=255, verbose_name=_('name'), null=True)
    last_name = models.CharField(max_length=50, verbose_name=_('last name'))
    password = models.CharField(max_length=128, verbose_name=_('password'))
    direction = models.CharField(null=True, max_length=255, verbose_name=_('direction'))
    about = models.CharField(null=True, max_length=255, verbose_name=_('about'))
    phone = models.CharField(null=True, max_length=20, verbose_name=_('phone'))
    point = geo_models.PointField(verbose_name=_('point'), null=True)
    current_photo = models.ForeignKey('security.PhotoUser', related_name="current_photo", verbose_name=_('photo'),
                              on_delete=models.CASCADE, null=True)
    status = models.SmallIntegerField(choices=STATUS, default=ACTIVE, verbose_name=_('status'))
    is_barber = models.BooleanField(null=True, verbose_name=_('is verified'), default=False)
    is_superuser = models.BooleanField(verbose_name=_('is superuser'), default=False)
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'last_name', 'phone']

    info = models.JSONField(default=dict)
    last_login = models.DateTimeField(blank=True, null=True, verbose_name=_('last login'))
    last_password_change = models.DateTimeField(blank=True, null=True, auto_now_add=True,
                                                verbose_name=_('last password change'))
    jwt_id = models.UUIDField(default=uuid.uuid4, blank=True, null=True)
    last_sync_date = models.DateTimeField(null=True, blank=True, verbose_name=_('last sync date'))
    objects = UserManager()

    @property
    def last_ip_address(self):
        try:
            return self.info['ip']
        except (ValueError, KeyError):
            return None

    def get_short_name(self):
        return self.name

    def __str__(self):
        return "{full_name}".format(full_name=self.get_full_name())

    def get_full_name(self):
        return "{name} {last_name}".format(name=self.name, last_name=self.last_name)

    @cached_property
    def full_name(self):
        return self.get_full_name()

    """
        Deletes an user
    """

    def delete(self, using=None, keep_parents=False):
        models.signals.pre_delete.send(sender=self.__class__,
                                       instance=self,
                                       using=using)

        self.status = User.INACTIVE
        self.save(update_fields=['status', ])
        models.signals.post_delete.send(sender=self.__class__,
                                        instance=self,
                                        using=using)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


class PhotoUser(ModelBase):
    user = models.ForeignKey(User, related_name="photos", verbose_name=_('user photo'), on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='photos/', null=True)
