import pytest
import os
import sys
from unittest.mock import Mock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Add the backend directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.app.database import Base
from backend.app.main import app


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def test_db_session(test_engine):
    """Create a test database session"""
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def test_client():
    """Create a test client for the FastAPI app"""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_storage_manager():
    """Mock storage manager for testing"""
    mock = Mock()
    mock.save_photo.return_value = "test://photo/ref"
    mock.save_report.return_value = "test://report/ref"
    mock.get_file_url.return_value = "http://test.com/file.jpg"
    mock.get_file_path.return_value = "/test/path/file.jpg"
    return mock


@pytest.fixture
def sample_image_bytes():
    """Generate sample image bytes for testing"""
    import cv2
    import numpy as np
    
    # Create a simple test image
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[25:75, 25:75] = [255, 255, 255]  # White square
    
    # Encode as JPEG
    _, buffer = cv2.imencode('.jpg', image)
    return buffer.tobytes()


@pytest.fixture
def sample_orders_csv():
    """Sample orders CSV data for testing"""
    return """order_id,ship_date,sku,qty,item_ids,status
SO-1001,2025-08-17,SKU-5566,2,"[""PALT-0001"",""PALT-0002""]",pending
SO-1002,2025-08-17,SKU-8899,1,"[""PALT-0003""]",pending"""


@pytest.fixture
def sample_allocations_csv():
    """Sample allocations CSV data for testing"""
    return """item_id,bin_id,status
PALT-0001,A54,allocated
PALT-0002,A52,allocated
PALT-0003,A51,allocated"""


@pytest.fixture
def sample_bins_csv():
    """Sample bins CSV data for testing"""
    return """bin_id,zone,coords
A54,Zone-A,10,20
A52,Zone-A,30,20
A51,Zone-A,50,20
S-01,Staging,10,100"""


@pytest.fixture
def api_headers():
    """Standard API headers for testing"""
    return {"Authorization": "Bearer changeme-supersecret"}


@pytest.fixture
def sample_snapshot_data():
    """Sample snapshot data for testing"""
    from datetime import datetime
    return {
        "bin_id": "A54",
        "item_ids": ["PALT-0001", "PALT-0002"],
        "photo_ref": "test://photo/ref",
        "ocr_text": "A54",
        "conf": 0.95,
        "ts": datetime.now()
    }


@pytest.fixture
def sample_anomaly_data():
    """Sample anomaly data for testing"""
    from datetime import datetime
    return {
        "type": "missing",
        "bin_id": "A54",
        "item_id": "PALT-0001",
        "order_id": "SO-1001",
        "severity": "high",
        "detail": "Item not found in expected bin",
        "status": "open",
        "ts": datetime.now()
    }


@pytest.fixture
def mock_qr_detector():
    """Mock QR code detector for testing"""
    mock = Mock()
    mock.decode_qr_codes.return_value = ["PALT-0001", "PALT-0002"]
    mock.decode_with_preprocessing.return_value = ["PALT-0001"]
    return mock


@pytest.fixture
def mock_ocr_detector():
    """Mock OCR detector for testing"""
    mock = Mock()
    mock.extract_bin_id.return_value = ("A54", 0.9)
    return mock


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables"""
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("API_KEY", "test-api-key")
    monkeypatch.setenv("DB_URL", "sqlite:///:memory:")
    monkeypatch.setenv("USE_PADDLE_OCR", "false")
    monkeypatch.setenv("STORAGE_BACKEND", "local")
    monkeypatch.setenv("STORAGE_LOCAL_DIR", "./test_storage")


# Pytest markers for different test categories
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "requires_ocr: mark test as requiring OCR dependencies")
    config.addinivalue_line("markers", "requires_camera: mark test as requiring camera access")


# Skip tests that require optional dependencies
def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip tests based on available dependencies"""
    skip_ocr = pytest.mark.skip(reason="PaddleOCR not available")
    skip_camera = pytest.mark.skip(reason="Camera access not available in test environment")
    
    try:
        import paddleocr
        has_paddle_ocr = True
    except ImportError:
        has_paddle_ocr = False
    
    for item in items:
        if "requires_ocr" in item.keywords and not has_paddle_ocr:
            item.add_marker(skip_ocr)
        if "requires_camera" in item.keywords:
            item.add_marker(skip_camera)