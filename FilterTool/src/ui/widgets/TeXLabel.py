
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QLineEdit, QWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class TeXLabel(QWidget):
    def __init__(self, parent=None, text=''):
        super().__init__(parent)

        # Create widgets
        
        # Get window background color
        bg = self.palette().window().color()
        cl = (bg.redF(), bg.greenF(), bg.blueF())

        # Create figure, using window bg color
        self.fig = Figure(edgecolor=cl, facecolor=cl)

        # Add canvas
        self.canvas = FigureCanvasQTAgg(self.fig)

        # Clear figure
        self.fig.clear()

        # Set figure title
        self.fig.suptitle(text,
                        x=0.5, y=0.5, 
                        horizontalalignment='center',
                        verticalalignment='center')
        self.canvas.draw()

        #  Create layout
        label_layout = QHBoxLayout()

        label_layout.addWidget(self.canvas)

        # Assign Layout
        self.setLayout(label_layout)

    def setText(self, text='', size=18):

        self.fig.suptitle(text,
                x=0.5, y=0.5,   # Alineado en el centro
                horizontalalignment='center',
                verticalalignment='center', size=size)
        self.canvas.draw()




if __name__ == "__main__":

    import sys

    app = QApplication(sys.argv)
    w = TeXLabel()
    w.show()
    sys.exit(app.exec())