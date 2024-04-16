import pyqtgraph as pg
from PySide6.QtWidgets import QApplication

# Create a PyQtGraph application instance
app = QApplication([])

# Create a plot widget
plot_widget = pg.plot(title="Example Plot")

# Generate some sample data
x = [1, 2, 3, 4, 5]
y = [10, 20, 15, 30, 25]

# Plot the data
plot = plot_widget.plot(x, y, pen='b')

# Get the axis item for the bottom axis
bottom_axis = plot_widget.getAxis('bottom')

# Move the tick labels to a custom position
bottom_axis.setPos(0.5)

# Show the plot
plot_widget.show()

# Start the event loop
app.exec_()
