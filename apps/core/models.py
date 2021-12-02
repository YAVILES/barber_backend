import uuid
from django.db import models, IntegrityError
from django.utils.translation import ugettext_lazy as _

MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

DAYS = (
    (MONDAY, _('Lunes')),
    (TUESDAY, _('Martes')),
    (WEDNESDAY, _('Miercoles')),
    (THURSDAY, _('Jueves')),
    (FRIDAY, _('Viernes')),
    (SATURDAY, _('Sábado')),
    (SUNDAY, _('Domingo')),
)


class ModelBase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_('updated'), auto_now=True)

    class Meta:
        abstract = True


class HairCut(ModelBase):
    code = models.CharField(max_length=20, verbose_name=_('code'), blank=True, db_index=True, unique=True)
    description = models.CharField(max_length=255, verbose_name=_('description'), null=True, unique=True)
    price = models.DecimalField(max_digits=22, default=0.00, decimal_places=2, verbose_name=_('price'))
    minutes = models.PositiveIntegerField(verbose_name='minutes', default=10)
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)

    class Meta:
        verbose_name = _('haircut')
        verbose_name_plural = _('haircuts')


def haircut_images_path(haircut_image: 'HairCutImage', file_name):
    return 'img/haircut/{0}/{1}'.format(haircut_image.haircut.code, file_name)


class HairCutImage(ModelBase):
    haircut = models.ForeignKey('core.HairCut', related_name='images', verbose_name=_('haircut'),
                                on_delete=models.CASCADE)
    image = models.ImageField(verbose_name=_('image'), upload_to=haircut_images_path, null=True)
    default = models.BooleanField(default=False)
