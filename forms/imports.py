from flask.ext.wtf.file import FileRequired, FileAllowed, FileField
from flask_wtf import Form


class ImportForm(Form):
    atom_file = FileField('depuis un fichier Atom, une sauvegarde blogmarks.net', [FileRequired(), FileAllowed(['xml'], 'Fichier XML uniquement !')])
