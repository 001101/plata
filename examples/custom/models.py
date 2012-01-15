import sys

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from plata.product.models import ProductBase
from plata.reporting.notifications import ConsoleHandler
from plata.shop.models import Price, PriceManager


handler = ConsoleHandler.register(stream=sys.stderr)


class Product(ProductBase):
    """(Nearly) the simplest product model ever"""

    is_active = models.BooleanField(_('is active'), default=True)
    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), unique=True)
    ordering = models.PositiveIntegerField(_('ordering'), default=0)

    description = models.TextField(_('description'), blank=True)

    class Meta:
        app_label = 'product'
        ordering = ['ordering', 'name']
        verbose_name = _('product')
        verbose_name_plural = _('products')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('plata_product_detail', (), {'object_id': self.pk})


class ProductPrice(Price):
    product = models.ForeignKey(Product, verbose_name=_('product'),
        related_name='prices')

    class Meta:
        app_label = 'product'
        get_latest_by = 'id'
        ordering = ['-valid_from']
        verbose_name = _('price')
        verbose_name_plural = _('prices')

    objects = PriceManager()


class ContactManager(models.Manager):
    def create_from_order(self, order, user):
        contact = self.model(user=user)

        for field in self.model.ADDRESS_FIELDS:
            f = 'billing_' + field
            setattr(contact, field, getattr(order, f))

        contact.save()
        return contact


class Contact(models.Model):
    ADDRESS_FIELDS = ['company', 'first_name', 'last_name', 'address',
        'zip_code', 'city', 'country']

    user = models.OneToOneField(User, verbose_name=_('user'),
        related_name='contactuser')
    #currency = CurrencyField(help_text=_('Preferred currency.'))

    company = models.CharField(_('company'), max_length=100, blank=True)
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    address = models.TextField(_('address'))
    zip_code = models.CharField(_('ZIP code'), max_length=50)
    city = models.CharField(_('city'), max_length=100)
    country = models.CharField(_('country'), max_length=3, blank=True)

    objects = ContactManager()

    def __unicode__(self):
        return unicode(self.user)
