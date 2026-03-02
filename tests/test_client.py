"""Tests for the main OpenDOSM client."""

import pytest

from opendosm import OpenDOSM
from opendosm.api.data_catalogue import DataCatalogueAPI
from opendosm.api.opendosm import OpenDOSMAPI


class TestClientSetup:
    def test_has_opendosm_api(self):
        client = OpenDOSM()
        assert isinstance(client.opendosm, OpenDOSMAPI)
        client.close()

    def test_has_data_catalogue_api(self):
        client = OpenDOSM()
        assert isinstance(client.data_catalogue, DataCatalogueAPI)
        client.close()

    def test_repr(self):
        client = OpenDOSM()
        assert "api.data.gov.my" in repr(client)
        client.close()

    def test_custom_base_url_in_repr(self):
        client = OpenDOSM(base_url="https://custom.api.dev")
        assert "custom.api.dev" in repr(client)
        client.close()


class TestClientLifecycle:
    def test_close(self):
        client = OpenDOSM()
        client.close()
        # Should not raise on double close
        client.close()

    def test_context_manager(self):
        with OpenDOSM() as client:
            assert isinstance(client, OpenDOSM)
            assert isinstance(client.opendosm, OpenDOSMAPI)
        # Client is closed after exiting the block

    def test_to_dataframe_delegates(self):
        pytest.importorskip("pandas")
        client = OpenDOSM()
        data = [{"date": "2023-01-01", "value": 42}]
        df = client.to_dataframe(data)
        assert len(df) == 1
        assert "value" in df.columns
        client.close()
