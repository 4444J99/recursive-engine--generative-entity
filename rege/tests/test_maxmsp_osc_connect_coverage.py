"""
Focused coverage for the real-``pythonosc`` connection paths in
``rege/bridges/maxmsp.py``.

These branches never execute in the default test environment because
``pythonosc`` is not installed, so ``connect()`` always falls through to the
``ImportError`` mock-mode handler. By injecting a fake ``pythonosc`` package
into ``sys.modules`` we drive the genuine OSC-client code paths:

- Lines 73-80: successful ``SimpleUDPClient`` creation + test message → CONNECTED
- Lines 93-96: a non-``ImportError`` exception during connect → error + False

Also covers the ``register_maxmsp_bridge`` helper.
"""

import sys
import types
from unittest.mock import MagicMock

import pytest

from rege.bridges.base import BridgeStatus
from rege.bridges.maxmsp import MaxMSPBridge, register_maxmsp_bridge


@pytest.fixture
def fake_pythonosc(monkeypatch):
    """
    Install a fake ``pythonosc`` package exposing ``udp_client.SimpleUDPClient``.

    Yields the ``SimpleUDPClient`` mock so individual tests can configure its
    behaviour (return value, side effects) before triggering ``connect()``.
    """
    udp_client_module = types.ModuleType("pythonosc.udp_client")
    simple_client_cls = MagicMock(name="SimpleUDPClient")
    udp_client_module.SimpleUDPClient = simple_client_cls

    pythonosc_pkg = types.ModuleType("pythonosc")
    pythonosc_pkg.udp_client = udp_client_module

    monkeypatch.setitem(sys.modules, "pythonosc", pythonosc_pkg)
    monkeypatch.setitem(sys.modules, "pythonosc.udp_client", udp_client_module)

    yield simple_client_cls


class TestMaxMSPRealOSCConnect:
    """Cover lines 73-80: the genuine pythonosc connection path."""

    def test_connect_creates_real_osc_client(self, fake_pythonosc):
        """Lines 73-80: SimpleUDPClient built, test message sent, CONNECTED."""
        instance = MagicMock(name="osc_client_instance")
        fake_pythonosc.return_value = instance

        bridge = MaxMSPBridge(config={"host": "127.0.0.1", "port": 9001})
        result = bridge.connect()

        assert result is True
        assert bridge.current_status == BridgeStatus.CONNECTED
        assert bridge.is_connected is True
        # Line 73: client created with configured host/port
        fake_pythonosc.assert_called_once_with("127.0.0.1", 9001)
        # The real client (not None) means this is NOT mock mode
        assert bridge._osc_client is instance
        # Line 76: a test connect message was sent on the real client
        instance.send_message.assert_any_call("/rege/connect", [1])

    def test_connected_real_client_is_not_mock_mode(self, fake_pythonosc):
        """receive() reports mock_mode False when a real OSC client exists."""
        fake_pythonosc.return_value = MagicMock()

        bridge = MaxMSPBridge()
        bridge.connect()
        state = bridge.receive()

        assert state is not None
        assert state["mock_mode"] is False
        assert state["connected"] is True


class TestMaxMSPConnectException:
    """Cover lines 93-96: a non-ImportError failure during connect."""

    def test_connect_osc_failure_sets_error(self, fake_pythonosc):
        """Lines 93-96: SimpleUDPClient raising → error status, return False."""
        fake_pythonosc.side_effect = OSError("socket unavailable")

        bridge = MaxMSPBridge()
        result = bridge.connect()

        assert result is False
        assert bridge.current_status == BridgeStatus.ERROR
        assert bridge.is_connected is False

    def test_connect_send_message_failure_sets_error(self, fake_pythonosc):
        """Lines 93-96: the test message raising also routes to the error branch."""
        instance = MagicMock()
        instance.send_message.side_effect = RuntimeError("send failed")
        fake_pythonosc.return_value = instance

        bridge = MaxMSPBridge()
        result = bridge.connect()

        assert result is False
        assert bridge.current_status == BridgeStatus.ERROR


class TestMaxMSPRealClientSend:
    """Exercise send() end-to-end over a real (faked) OSC client."""

    def test_send_fragment_over_real_client(self, fake_pythonosc):
        """A connected real client sends fragment data successfully."""
        instance = MagicMock()
        fake_pythonosc.return_value = instance

        bridge = MaxMSPBridge()
        bridge.connect()
        instance.send_message.reset_mock()

        result = bridge.send_fragment(
            {"id": "F1", "name": "spark", "charge": 88, "tags": ["CANON+"]}
        )

        assert result["status"] == "sent"
        assert result["address"] == "/rege/fragment"
        # The real client was used to transmit the fragment
        instance.send_message.assert_called_once()
        address, args = instance.send_message.call_args.args
        assert address == "/rege/fragment"
        assert "F1" in args


class TestRegisterMaxMSPBridge:
    """Cover register_maxmsp_bridge(): the bridge type lands in the registry."""

    def test_register_adds_maxmsp_type(self):
        from rege.bridges.registry import get_bridge_registry

        register_maxmsp_bridge()
        registry = get_bridge_registry()

        bridge = registry.create_bridge("maxmsp", "via-registry")
        assert isinstance(bridge, MaxMSPBridge)
        assert bridge.name == "via-registry"
