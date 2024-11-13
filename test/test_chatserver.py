from src.chatserver import accept_wrapper
from unittest import mock
from unittest.mock import MagicMock
import types
import selectors

mock_socket = MagicMock()
mock_socket.accept.return_value = (mock_socket, ('127.0.0.1', 12345))
data = types.SimplesNamespace(addr=('127.0.0.1', 12345), inb=b"", outb=b"")
mock_selector = MagicMock()

accept_wrapper(mock_socket)
mock_selector.register.assert_called_once_with(mock_socket, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data)
