from django import forms
from .models import Task,Loop

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['date_time', 'location', 'description', 'status', 'video_file', 'time']

class LoopForm(forms.ModelForm):

    class Meta:
        model = Loop
        fields = ('height', 'width', 'loop_name', 'coordinates_x', 'coordinates_y')