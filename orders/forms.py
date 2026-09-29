from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    # Добавляем новое обязательное поле согласия по ФЗ-152 (вне класса Meta)
    agree_to_terms = forms.BooleanField(
        required=True,  # Делает галочку строго обязательной для отправки формы
        label='Я согласен на обработку персональных данных',
        widget=forms.CheckboxInput(attrs={
            'style': 'margin-right: 10px; transform: scale(1.2); cursor: pointer;'
        })
    )

    class Meta:
        model = Order
        # Обязательно добавляем новое поле в список fields
        fields = ['first_name', 'phone', 'agree_to_terms']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'style': 'width: 100%; padding: 12px; border-radius: 4px; border: 1px solid #eae6e1; font-size: 16px; margin-bottom: 20px;',
                'placeholder': 'Иванов Иван Иванович (полностью для ПВЗ)'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'phone-mask-input',  # Добавили класс, чтобы привязать маску +7 в HTML
                'style': 'width: 100%; padding: 12px; border-radius: 4px; border: 1px solid #eae6e1; font-size: 16px; margin-bottom: 20px;',
                'placeholder': '+7 (999) 000-00-00'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Меняем лейбл для имени на развернутый
        self.fields['first_name'].label = 'Ваше имя, фамилия и отчество полностью:'
