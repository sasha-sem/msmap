from django.db import models
from django.contrib.gis.db import models as geomodels
from django.core.validators import MaxValueValidator, MinValueValidator


class SurfaceType(models.Model):
    RATING_COUNT_CHOICES = ((i, i) for i in range(1, 11))
    name = models.CharField(max_length=256, verbose_name='Название', blank=False, null=True)
    rating = models.PositiveSmallIntegerField(blank=False, null=True,
                                              help_text='Чем выше оценка, тем удобнее ездить по данному покрытиию',
                                              verbose_name='Оценка',
                                              validators=[MinValueValidator(1), MaxValueValidator(10)],
                                              choices=RATING_COUNT_CHOICES, default=1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Типы покрытий'
        verbose_name = 'Тип покрытия'


class StreetType(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название', blank=False, null=True)
    cars_allowed = models.BooleanField(verbose_name='Разрешен проезд машинам', blank=False, null=True, default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Типы улиц'
        verbose_name = 'Тип улицы'


class Street(models.Model):
    street_type = models.ForeignKey(StreetType, blank=True, null=True, on_delete=models.CASCADE,
                                    verbose_name='Тип улицы',
                                    related_name='street_type')
    street_surface = models.ForeignKey(SurfaceType, blank=True, null=True, on_delete=models.CASCADE,
                                       verbose_name='Тип покрытия',
                                       related_name='street_surface')
    user_score = models.IntegerField(verbose_name='Польовательский рейтинг', blank=True, null=True, default=0)
    source = models.IntegerField(blank=True, null=True, )
    target = models.IntegerField(blank=True, null=True, )
    x1 = models.FloatField(blank=True, null=True, )
    y1 = models.FloatField(blank=True, null=True, )
    x2 = models.FloatField(blank=True, null=True, )
    y2 = models.FloatField(blank=True, null=True, )
    geom = geomodels.MultiLineStringField(blank=False, null=True, verbose_name='Геометрия')

    def __str__(self):
        return str(self.id)

    @property
    def surface_rating(self):
        return self.street_surface.rating

    class Meta:
        verbose_name_plural = 'Улицы'
        verbose_name = 'Улица'
