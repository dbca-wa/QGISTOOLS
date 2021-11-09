from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QFormLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QVBoxLayout

from ..tools import Tools


class DeptNamesDialog(QDialog):

    def __init__(self):
        QDialog.__init__(self, Tools.QGISApp)

        self.setWindowTitle("Department Names")

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        fields_layout = QFormLayout()
        main_layout.addLayout(fields_layout)

        self._long_name_field = QLineEdit(Tools.get_dept_long_name())
        field_width = int(self._long_name_field.width() * 0.55)
        self._long_name_field.setFixedWidth(field_width)
        fields_layout.addRow("Long Name:", self._long_name_field)

        self._acronym_field = QLineEdit(Tools.get_dept_acronym())
        self._acronym_field.setFixedWidth(field_width)

        fields_layout.addRow("Acronym:", self._acronym_field)

        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)

        ok_button = QPushButton("OK", self)
        buttons_layout.addWidget(ok_button)
        ok_button.setAutoDefault(True)
        ok_button.clicked.connect(self.accept)

        cancel_button = QPushButton("Cancel", self)
        buttons_layout.addWidget(cancel_button)
        cancel_button.clicked.connect(self.reject)

        self.exec_()

    def accept(self):
        long_name = self._long_name_field.text().strip()
        acronym = self._acronym_field.text().strip()

        if long_name == "" or acronym == "":
            Tools.alert("Invalid Input")
            return

        QDialog.accept(self)

        if long_name != Tools.get_dept_long_name() or acronym != Tools.get_dept_acronym():
            Tools.alert("Please restart QGIS to apply changes.")

        Tools.set_dept_long_name(long_name)
        Tools.set_dept_acronym(acronym)
