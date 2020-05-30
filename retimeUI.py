import pymel.core as pm
import pymel.api as pma
import traceback
from PySide2 import QtWidgets
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from shiboken2 import getCppPointer
from dsRetimingTool import retimeFn


class Dialog(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    WINDOW_TITLE = "dsRetiming Tool"
    UI_NAME = "dsRetimingDialog"
    UI_SCRIPT = "from dsRetimingTool import retimeUI\nretimeUI.Dialog.display()"
    UI_INSTANCE = None
    ABSOLUTE_BUTTON_WIDTH = 50
    RELATIVE_BUTTON_WIDTH = 64
    RETIMING_PROPERTY_NAME = "retiming_data"

    @classmethod
    def display(cls):
        if not cls.UI_INSTANCE:
            cls.UI_INSTANCE = Dialog()

        if cls.UI_INSTANCE.isHidden():
            cls.UI_INSTANCE.show(dockable=1, uiScript=cls.UI_SCRIPT)
        else:
            cls.UI_INSTANCE.raise_()
            cls.UI_INSTANCE.activateWindow()

    def __init__(self):
        super(Dialog, self).__init__()

        self.__class__.UI_INSTANCE = self
        self.setObjectName(self.__class__.UI_NAME)

        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(330, 100)

        workspaceControlName = "{0}WorkspaceControl".format(self.UI_NAME)
        if pm.workspaceControl(workspaceControlName, q=1, ex=1):
            workspaceControlPtr = long(pma.MQtUtil.findControl(workspaceControlName))
            widgetPtr = long(getCppPointer(self)[0])

            pma.MQtUtil.addWidgetToMayaLayout(widgetPtr, workspaceControlPtr)

        self.createWidgets()
        self.createLayouts()
        self.createConnections()

    def createWidgets(self):
        self.absoluteButtons = []
        for i in range(1, 7):
            btn = QtWidgets.QPushButton("{0}f".format(i))
            btn.setFixedWidth(self.ABSOLUTE_BUTTON_WIDTH)
            btn.setProperty(self.RETIMING_PROPERTY_NAME, [i, False])
            self.absoluteButtons.append(btn)

        self.relativeButtons = []
        for i in [-2, -1, 1, 2]:
            btn = QtWidgets.QPushButton("{0}f".format(i))
            btn.setFixedWidth(self.RELATIVE_BUTTON_WIDTH)
            btn.setProperty(self.RETIMING_PROPERTY_NAME, [i, True])
            self.relativeButtons.append(btn)

        self.moveToNextCheckBox = QtWidgets.QCheckBox("Move to next frame")
        self.moveToNextCheckBox.setChecked(False)

    def createLayouts(self):
        absoluteRetimeLayout = QtWidgets.QHBoxLayout()
        absoluteRetimeLayout.setSpacing(2)
        for btn in self.absoluteButtons:
            absoluteRetimeLayout.addWidget(btn)

        relativeRetimeLayout = QtWidgets.QHBoxLayout()
        relativeRetimeLayout.setSpacing(2)
        for btn in self.relativeButtons:
            relativeRetimeLayout.addWidget(btn)
            if relativeRetimeLayout.count() == 2:
                relativeRetimeLayout.addStretch()

        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setContentsMargins(2, 2, 2, 2)
        mainLayout.setSpacing(2)
        mainLayout.addLayout(absoluteRetimeLayout)
        mainLayout.addLayout(relativeRetimeLayout)
        mainLayout.addWidget(self.moveToNextCheckBox)

    def createConnections(self):
        for btn in self.absoluteButtons:
            btn.clicked.connect(self.retime)

        for btn in self.relativeButtons:
            btn.clicked.connect(self.retime)

    def retime(self):
        btn = self.sender()
        if btn:
            retimingData = btn.property(self.RETIMING_PROPERTY_NAME)
            moveToNext = self.moveToNextCheckBox.isChecked()

            # Group undos
            pm.undoInfo(openChunk=1)
            try:
                retimeFn.RetimeUtils.retimeKeys(retimingData[0], retimingData[1], moveToNext)
            except Exception:
                traceback.print_exc()
                pma.MGlobal.displayError("Retime error occured. See script editor for details.")
            pm.undoInfo(closeChunk=1)


if __name__ == "__main__":
    try:
        if dsRetimer and dsRetimer.parent():
            workspaceControlName = dsRetimer.parent().objectName()

            if pm.window(workspaceControlName, ex=1, q=1):
                pm.deleteUI(workspaceControlName)
    except Exception:
        pass

    dsRetimer = Dialog()
    dsRetimer.show(dockable=1, uiScript=dsRetimer.UI_SCRIPT)
