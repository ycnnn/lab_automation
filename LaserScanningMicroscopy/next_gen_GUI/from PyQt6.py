from PySide6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()
    
    def initUI(self):
        layout = QGridLayout(self)
        
        # Add widgets to the layout
        label1 = QLabel("Row 1")
        label2 = QLabel("Row 2")
        label3 = QLabel("Row 3")
        label4 = QLabel("Row 4")
        label5 = QLabel("Row 5")
        label6 = QLabel("Row 6")
        
        layout.addWidget(label1, 0, 0)
        layout.addWidget(label2, 1, 0)
        layout.addWidget(label3, 2, 0)
        layout.addWidget(label4, 0, 1)
        layout.addWidget(label5, 1, 1)
        layout.addWidget(label6, 2, 1)
        
        # Set stretch factors for rows
        layout.setRowStretch(0, 3)  # First row occupies 30%
        layout.setRowStretch(1, 1)  # Second row
        layout.setRowStretch(2, 1)  # Third row
        
        self.setLayout(layout)

app = QApplication([])
window = MyWidget()
window.show()
app.exec()