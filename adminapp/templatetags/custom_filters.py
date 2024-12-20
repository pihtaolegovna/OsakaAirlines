from django import template
from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.db.models import ForeignKey, OneToOneField, ManyToManyField

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Возвращает значение из словаря по ключу.
    Если ключ не найден, возвращается пустой список.
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, [])
    return []


@register.filter
def has_id(obj):
    """
    Проверить, есть ли у объекта атрибут 'id'.
    """
    return hasattr(obj, 'id') and getattr(obj, 'id', None) is not None


@register.filter
def dict_get(d, key):
    """
    Возвращает значение из словаря по ключу.
    """
    if isinstance(d, dict):
        return d.get(key)
    return None


@register.filter
def getattr_field(obj, field_name):
    """
    Получить значение атрибута объекта по имени поля в шаблоне.
    """
    try:
        return getattr(obj, field_name, None)
    except AttributeError:
        return None


@register.filter
def get_field_verbose_name(model_class, field_name):
    """
    Получает verbose_name поля модели по имени поля.
    """
    try:
        field = model_class._meta.get_field(field_name)
        return field.verbose_name
    except FieldDoesNotExist:
        return field_name  # Если поле не найдено, возвращаем имя поля


@register.filter
def get_model_verbose_name(model_name):
    """
    Получает verbose_name модели по её имени.
    """
    try:
        model = apps.get_model('api', model_name)
        return model._meta.verbose_name
    except LookupError:
        return model_name  # Если модель не найдена, возвращаем имя модели


@register.filter
def has_related_name(obj, field_name):
    """
    Проверить, есть ли у поля объекта related_name (для ForeignKey, OneToOneField, ManyToManyField).
    """
    try:
        field = obj._meta.get_field(field_name)
        if isinstance(field, (ForeignKey, OneToOneField, ManyToManyField)):
            return True
    except FieldDoesNotExist:
        pass
    return False
