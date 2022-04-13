from django import forms


class RecipeIngredientForm(forms.models.BaseInlineFormSet):
    def clean(self):
        for form in self.forms:
            if not form.cleaned_data:
                raise forms.ValidationError('Нужно выбрать ингредиенты!')
