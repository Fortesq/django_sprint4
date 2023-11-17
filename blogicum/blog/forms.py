from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, Post

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'time_field_name':
                forms.TimeInput(format='%H:%M:%S'),  # Если правильно понял
        }


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
