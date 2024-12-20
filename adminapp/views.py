from django.shortcuts import render, redirect
from django.http import Http404
from django.core.paginator import Paginator
from django.db.models import Q
import os
import shutil
from django.conf import settings
from django.http import JsonResponse
from django.core.management import call_command
from django.views.decorators.csrf import csrf_exempt
from django.db import models
import time
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ValidationError

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = settings.BACKUP_DIR

import os
import time
from django.core.management import call_command
from django.core.exceptions import SuspiciousFileOperation
from django.core.files import File
from django.conf import settings
import os
from django.core.files import File
from django.core.management import call_command
from django.core.exceptions import SuspiciousFileOperation



def get_field_verbose_names(model_class):
    verbose_names = {}
    for field in model_class._meta.fields:
        verbose_names[field.name] = field.verbose_name
    return verbose_names



def generic_dashboard(request, model_form_map, is_verbose=False):
    model_name = request.GET.get('model_name', list(model_form_map.keys())[0])
    if model_name not in model_form_map:
        raise Http404(f"Model '{model_name}' not found")
    current_model = model_form_map[model_name]['model']
    current_form = model_form_map[model_name]['form']

    if is_verbose:
        print(f"Working with model: {current_model.__name__}")

    objects = current_model.objects.all()

    filters = {}
    for field in current_model._meta.fields:
        if is_verbose:
            print(f"Processing field: {field.name} ({type(field).__name__})")
        if field.choices:
            filters[field.name] = [choice[0] for choice in field.choices]
        elif isinstance(field, (models.CharField, models.TextField)):
            filters[field.name] = current_model.objects.values_list(field.name, flat=True).distinct()
        elif isinstance(field, (models.ForeignKey, models.OneToOneField)):
            related_model = field.related_model
            if related_model:
                related_fields = [f.name for f in related_model._meta.fields if isinstance(f, (models.CharField, models.TextField))]
                display_field = related_fields[0] if related_fields else 'id'
                filters[field.name] = related_model.objects.values_list('id', display_field).distinct()
        elif isinstance(field, (models.IntegerField, models.DecimalField, models.FloatField)):
            filters[field.name] = current_model.objects.values_list(field.name, flat=True).distinct()

    filter_params = {key: value for key, value in request.GET.items() if key in filters and value}
    for field_name, field_value in filter_params.items():
        objects = objects.filter(**{field_name: field_value})

    search_query = request.GET.get('search', '')
    if search_query:
        search_filter = Q()
        for field in current_model._meta.fields:
            if isinstance(field, (models.CharField, models.TextField)):
                search_filter |= Q(**{f"{field.name}__icontains": search_query})
        objects = objects.filter(search_filter)

    sort_by = request.GET.get('sort', '')
    if sort_by:
        objects = objects.order_by(sort_by)

    paginator = Paginator(objects, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    field_verbose_names = get_field_verbose_names(current_model)

    if request.GET.get('export') == 'json':
        data = list(objects.values())
        response = HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="{model_name}_data.json"'
        return response
    
    if request.method == 'POST' and 'import_json' in request.POST:
        json_file = request.FILES.get('json_file')
        if not json_file:
            return HttpResponse('No file uploaded.', status=400)

        try:
            data = json.load(json_file)
            if not isinstance(data, list):
                raise ValidationError("Invalid data format: expected a list of objects.")
            
            for item in data:
                try:
                    instance = current_model(**item)
                    instance.save()
                except Exception as e:
                    if is_verbose:
                        print(f"Error saving item: {item}. Error: {str(e)}")

            return redirect(f'/dashboard?model_name={model_name}')

        except json.JSONDecodeError:
            return HttpResponse('Invalid JSON file.', status=400)
        except ValidationError as e:
            return HttpResponse(f'Validation error: {str(e)}', status=400)
        except Exception as e:
            return HttpResponse(f'Error while importing data: {str(e)}', status=500)

    form = current_form()

    if request.method == 'POST' and 'import_json' not in request.POST:
        action = request.POST.get('action')
        model_name_from_post = request.POST.get('model_name')

        current_model = model_form_map[model_name_from_post]['model']
        current_form = model_form_map[model_name_from_post]['form']


        if model_name_from_post in model_form_map:

            if is_verbose:
                print(f"Received POST action: {action} for model: {model_name_from_post}")

            if action == 'create':
                form = current_form(request.POST)
                if form.is_valid():
                    form.save()
                    if is_verbose:
                        print("Created new object successfully.")
                    return redirect(f'/dashboard?model_name={model_name_from_post}')

            elif action == 'update':
                obj_id = request.POST.get('id')
                try:
                    obj = current_model.objects.get(id=obj_id)
                    form = current_form(request.POST, instance=obj)
                    if form.is_valid():
                        form.save()
                        return redirect(f'/dashboard?model_name={model_name_from_post}')
                except current_model.DoesNotExist:
                    print(f"Object with ID {obj_id} does not exist.")

            elif action == 'delete':
                obj_id = request.POST.get('id')
                if obj_id:
                    try:
                        obj = current_model.objects.get(id=obj_id)
                        obj.delete()
                        if is_verbose:
                            print(f"Deleted object {obj_id} successfully.")
                        return redirect(f'/dashboard?model_name={model_name_from_post}')
                    except current_model.DoesNotExist:
                        if is_verbose:
                            print(f"Object with ID {obj_id} does not exist.")
                else:
                    print("No ID provided for deletion.")
                    return redirect('/dashboard')

    form = current_form()

    context = {
        'model_name': model_name,
        'current_model': current_model,
        'is_verbose': is_verbose,
        'page_obj': page_obj,
        'fields': [field.name for field in current_model._meta.fields],
        'filters': filters,
        'form': form,
        'models': list(model_form_map.keys()),
        'search_query': search_query,
        'filter_params': filter_params,
        'sort_by': sort_by,
        'field_verbose_names': field_verbose_names
    }

    return render(request, 'admin_dashboard.html', context)




def list_backups():
    """Returns a list of available backup files."""
    return sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.endswith('.sql')],
        reverse=True
    )



def create_backup():
    backup_filename = f"{settings.DATABASES['default']['NAME'].name}_backup_{str(int(time.time()))}.sql"
    backup_filepath = backup_filename
    if not os.path.commonprefix([os.path.realpath(backup_filepath), os.path.realpath(settings.BASE_DIR)]) == os.path.realpath(settings.BASE_DIR):
        raise SuspiciousFileOperation(f"Detected path traversal attempt in {backup_filepath}")
    call_command('dbbackup', output_filename=backup_filepath)

    return backup_filename


def restore_backup(backup_filename):
    """Restores a backup to the database."""
    backup_filepath = os.path.join(BACKUP_DIR, backup_filename)
    real_backup_filepath = os.path.realpath(backup_filepath)
    if not os.path.commonprefix([real_backup_filepath, os.path.realpath(BACKUP_DIR)]) == os.path.realpath(BACKUP_DIR):
        raise SuspiciousFileOperation(f"Detected path traversal attempt in {backup_filepath}")
    
    print(f"Attempting to restore from: {real_backup_filepath}")
    if os.path.exists(real_backup_filepath):
        call_command('dbrestore', input_filename=real_backup_filepath)
        return True
    return False




@csrf_exempt
def manage_backups(request):
    """Handles creating and restoring backups."""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            backup_filename = create_backup()
            return redirect('adminapp:manage_backups')
        elif action == 'restore':
            backup_filename = request.POST.get('backup_filename')
            if restore_backup(backup_filename):
                return redirect('adminapp:manage_backups')
            else:
                return redirect('adminapp:manage_backups')
    backups = list_backups()
    context = {
        'backups': backups,
    }
    return render(request, 'manage_backups.html', context)
