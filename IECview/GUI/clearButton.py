from silx.gui import qt
from silx.gui.plot import PlotWindow
from silx.gui.plot.actions import PlotAction


class ClearButton(PlotAction):
    """QAction clearing a plot
    :param plot: :class:`.PlotWidget` instance on which to operate
    :param parent: See :class:`QAction`
    """
    def __init__(self, plot, parent=None):
        PlotAction.__init__(self,
                            plot,
                            icon='shape-circle',
                            text='CLEAR',
                            tooltip='Clear Canvas',
                            triggered=self.clear,
                            parent=parent)

    def clear(self):
        """Remove all curves"""
        # By inheriting from PlotAction, we get access to attribute self.plot
        # which is a reference to the PlotWindow
        self.plot.clear()