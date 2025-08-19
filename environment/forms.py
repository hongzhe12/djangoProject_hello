from django import forms
from .models import EnvironmentVariable

class EnvironmentVariableForm(forms.ModelForm):
    scope = forms.ChoiceField(
        choices=[
            ('global', '全局（所有用户）'),
            ('session', '当前会话'),
        ],
        initial='global',
        label='生效范围'
    )

    class Meta:
        model = EnvironmentVariable
        fields = ['key', 'value', 'description', 'scope']
        widgets = {
            'key': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean_key(self):
        key = self.cleaned_data['key']
        if not key.isidentifier():
            raise forms.ValidationError('变量名必须是有效的标识符（字母、数字、下划线，不以数字开头）')
        return key