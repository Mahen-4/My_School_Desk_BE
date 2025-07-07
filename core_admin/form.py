from django import forms

class ExcelUploadForm(forms.Form):
    fichier = forms.FileField(label="Fichier Excel")