from django import forms


# Форма для выбора количества товара
class CartAddProductForm(forms.Form):
    # Создаем список чисел от 1 до 20
    PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]

    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES,
        coerce=int,
        label='Количество',
        widget=forms.Select(attrs={
            'style': 'padding: 5px 10px; border-radius: 4px; border: 1px solid #eae6e1; background-color: #fff; font-family: inherit; cursor: pointer;'
        })
    )
    # Скрытое поле: True означает, что старое количество заменится на новое
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
