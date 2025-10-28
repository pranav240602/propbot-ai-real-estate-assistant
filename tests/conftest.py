"""
Pytest configuration and fixtures for PropBot tests
"""
import pytest
import pandas as pd
from pathlib import Path
import tempfile

@pytest.fixture
def sample_property_data():
    """Sample property data for testing"""
    return pd.DataFrame({
        'property_id': ['P001', 'P002', 'P003'],
        'address': ['123 Main St, Boston, MA', '456 Oak Ave, Boston, MA', '789 Pine Rd, Boston, MA'],
        'price': [500000, 750000, 600000],
        'bedrooms': [3, 4, 3],
        'bathrooms': [2.0, 3.0, 2.5],
        'sqft': [2000, 2500, 2200],
        'lat': [42.3601, 42.3555, 42.3499],
        'long': [-71.0589, -71.0640, -71.0826]
    })

@pytest.fixture
def sample_crime_data():
    """Sample crime data for testing"""
    return pd.DataFrame({
        'incident_number': ['C001', 'C002', 'C003'],
        'offense_code': ['3301', '3302', '3303'],
        'offense_description': ['ROBBERY', 'LARCENY', 'ASSAULT'],
        'district': ['B2', 'C11', 'D4'],
        'occurred_on_date': ['2024-01-15', '2024-01-16', '2024-01-17'],
        'lat': [42.3601, 42.3555, 42.3499],
        'long': [-71.0589, -71.0640, -71.0826]
    })

@pytest.fixture
def test_data_dir():
    """Create temporary data directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        (data_dir / "raw").mkdir()
        (data_dir / "processed").mkdir()
        (data_dir / "validation_reports").mkdir()
        (data_dir / "statistics").mkdir()
        yield data_dir

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "test_propbot")
    monkeypatch.setenv("POSTGRES_USER", "test_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test_pass")
