import sys
from PySide6.QtWidgets import QApplication, QWidget

# Create the application object
app = QApplication(sys.argv)

# Create the first QWidget instance
widget = QWidget()
widget.setWindowTitle('Widget')
widget.setGeometry(100, 100, 200, 200)  # Set position and size
widget.show()

# Start the application event loop
sys.exit(app.exec())
