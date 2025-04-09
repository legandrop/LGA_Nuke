from typing import Any, Optional, List, Union

class Qt:
    LeftButton = 1
    NoModifier = 0

class QEvent:
    MouseButtonPress = 2
    MouseButtonRelease = 3

class QPoint:
    def __init__(self, x: int, y: int) -> None: ...

class QMouseEvent:
    def __init__(self, type: int, pos: QPoint, button: int, buttons: int, modifiers: int) -> None: ...

class QApplication:
    @staticmethod
    def widgetAt(pos: QPoint) -> Optional[Any]: ...
    @staticmethod
    def sendEvent(receiver: Any, event: QEvent) -> bool: ...

class QCursor:
    @staticmethod
    def pos() -> QPoint: ...

class QWidget:
    def mapFromGlobal(self, pos: QPoint) -> QPoint: ... 