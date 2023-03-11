# from django.shortcuts import render
from django.http import JsonResponse
from .tasks import *
from .tasks import detection
import json
from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Task, Loop, TaskResult
from .forms import TaskForm, LoopForm
from rest_framework.decorators import api_view
from rest_framework.response import Response


def dashboard(request):
    tasks = Task.objects.all()
    return render(request, 'task/Dashboard.html', {'tasks': tasks})


def new_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save()
            return redirect(reverse("main:dashboard"))
    else:
        form = TaskForm()
    return render(request, 'task/NewTask.html', {'form': form})


def edit_task(request, task_id):
    task = get_object_or_404(Task, task_id=task_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect(reverse("main:dashboard"))
    else:
        form = TaskForm(instance=task)
    return render(request, 'task/EditTask.html', {'form': form})


def new_loop(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == 'POST':
        form = LoopForm(request.POST)
        if form.is_valid():
            loop = form.save(commit=False)
            loop.head_task = task
            loop.save()
            # return redirect('app1/LoopDashboard.html', args=(task_id))
            return redirect(reverse("main:loop_dashboard", args=(task_id,)))
    else:
        form = LoopForm(initial={'head_task': task})
    return render(request, 'loop/NewLoop.html', {'form': form, 'task_id': task_id})


def edit_loop(request, loop_id):
    loop = get_object_or_404(Loop, pk=loop_id)
    if request.method == 'POST':
        form = LoopForm(request.POST, instance=loop)
        if form.is_valid():
            form.save()
            return redirect(reverse("main:loop_dashboard", args=(loop.head_task.pk,)))
    else:
        form = LoopForm(instance=loop)
    return render(request, 'loop/EditLoop.html', {'form': form, 'task_id': loop.head_task.pk})


def loop_dashboard(request, task_id):
    loops = Loop.objects.filter(head_task__pk=task_id)
    return render(request, 'loop/LoopDashboard.html', {'loops': loops, 'task_id': task_id})


def call_detect(request, task_id):
    # serializer = MySerializer(data=request.data)
    # if serializer.is_valid():
    #     serializer.save()
    #     return Response(serializer.data, status=201)
    # return Response(serializer.errors, status=400)
    task = Task.objects.get(pk=task_id)

    # Serialize the object to JSON
    serialized_object = serializers.serialize('json', [task])

    # Convert the JSON string to a Python dictionary
    data = json.loads(serialized_object)

    json_data = json.dumps(data)
    json_d = {
        "task_id": task_id,
        "pk": task.pk
    }

    task_result = detection.apply_async(
        args=[json_d], kwargs={}, result_backend='django-db')
    task_result_obj = TaskResult.objects.create(
        task_id_celery=task_result.task_id,
        status=task_result.status,
        result=task_result.result
    )
    task.task_result = task_result_obj
    # if (task_id.is_valid()):
    #     task.task_id_celery = task_id_celery
    return HttpResponse(json_data, content_type='application/json')


# def predict(request):
#     data = request.POST.dict()
#     result = detection.delay(data)
#     return JsonResponse({'task_id': result.id})


# def task_status(request, task_id_celery):
#     status = get_task_status(task_id_celery)
#     return JsonResponse({'task_id_celery': task_id_celery, 'status': status})


# def task_result(request, task_id):
#     result = get_task_result(task_id)
#     return JsonResponse({'result': result})
