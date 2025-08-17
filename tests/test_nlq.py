import pytest
from unittest.mock import Mock, patch
from backend.app.services.nlq import NaturalLanguageQueryService


class TestNaturalLanguageQueryService:
    def setup_method(self):
        self.mock_db = Mock()
        self.nlq_service = NaturalLanguageQueryService(self.mock_db)
    
    @pytest.mark.parametrize("query,expected_intent,expected_entities", [
        ("A54现在有什么？", "check_bin", {"bin_id": "A54"}),
        ("What's in bin A54?", "check_bin", {"bin_id": "A54"}),
        ("看看S-01", "check_bin", {"bin_id": "S-01"}),
        ("找 SKU-5566", "find_sku", {"sku": "SKU-5566"}),
        ("Where is SKU-5566?", "find_sku", {"sku": "SKU-5566"}),
        ("PALT-0001 在哪", "find_item", {"item_id": "PALT-0001"}),
        ("Where is PALT-0001?", "find_item", {"item_id": "PALT-0001"}),
        ("导出今天的差异报告", "export_report", {}),
        ("Export today's report", "export_report", {}),
        ("今天有多少异常", "anomaly_stats", {}),
        ("How many anomalies today?", "anomaly_stats", {}),
        ("库存总览", "inventory_summary", {}),
        ("Inventory summary", "inventory_summary", {}),
        ("random text", "unknown", {}),
    ])
    def test_parse_intent(self, query, expected_intent, expected_entities):
        """Test intent parsing for various queries"""
        intent, entities = self.nlq_service._parse_intent(query.lower())
        
        assert intent == expected_intent
        for key, value in expected_entities.items():
            assert entities.get(key) == value
    
    def test_handle_bin_query_no_bin_id(self):
        """Test bin query without bin ID"""
        result = self.nlq_service._handle_bin_query(None)
        
        assert "Please specify a bin ID" in result["answer"]
        assert result["data"] is None
    
    def test_handle_bin_query_not_found(self):
        """Test bin query for non-existent bin"""
        # Mock database query to return None
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None
        
        result = self.nlq_service._handle_bin_query("A99")
        
        assert "No recent snapshots found" in result["answer"]
        assert result["data"]["bin_id"] == "A99"
        assert result["data"]["items"] == []
    
    def test_handle_bin_query_empty_bin(self):
        """Test bin query for empty bin"""
        from datetime import datetime
        
        # Mock snapshot with no items
        mock_snapshot = Mock()
        mock_snapshot.item_ids = []
        mock_snapshot.ts = datetime(2025, 8, 17, 10, 30, 0)
        mock_snapshot.photo_ref = "test_photo.jpg"
        mock_snapshot.conf = 0.95
        
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_snapshot
        
        with patch('backend.app.services.nlq.storage_manager') as mock_storage:
            mock_storage.get_file_url.return_value = "http://example.com/photo.jpg"
            
            result = self.nlq_service._handle_bin_query("A54")
        
        assert "appears to be empty" in result["answer"]
        assert result["data"]["bin_id"] == "A54"
        assert result["data"]["items"] == []
    
    def test_handle_bin_query_with_items(self):
        """Test bin query for bin with items"""
        from datetime import datetime
        
        # Mock snapshot with items
        mock_snapshot = Mock()
        mock_snapshot.item_ids = ["PALT-0001", "PALT-0002"]
        mock_snapshot.ts = datetime(2025, 8, 17, 10, 30, 0)
        mock_snapshot.photo_ref = "test_photo.jpg"
        mock_snapshot.conf = 0.95
        
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_snapshot
        
        with patch('backend.app.services.nlq.storage_manager') as mock_storage:
            mock_storage.get_file_url.return_value = "http://example.com/photo.jpg"
            
            result = self.nlq_service._handle_bin_query("A54")
        
        assert "contains 2 items" in result["answer"]
        assert result["data"]["bin_id"] == "A54"
        assert result["data"]["items"] == ["PALT-0001", "PALT-0002"]
        assert result["data"]["photo_url"] == "http://example.com/photo.jpg"
    
    def test_handle_sku_query_no_sku(self):
        """Test SKU query without SKU"""
        result = self.nlq_service._handle_sku_query(None)
        
        assert "Please specify a SKU" in result["answer"]
        assert result["data"] is None
    
    def test_handle_sku_query_not_found(self):
        """Test SKU query for non-existent SKU"""
        # Mock database query to return empty list
        self.mock_db.query.return_value.filter.return_value.all.return_value = []
        
        result = self.nlq_service._handle_sku_query("SKU-NOTFOUND")
        
        assert "No items found" in result["answer"]
        assert result["data"]["sku"] == "SKU-NOTFOUND"
        assert result["data"]["locations"] == []
    
    def test_handle_item_query_not_found(self):
        """Test item query for non-existent item"""
        # Mock database query to return None
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.nlq_service._handle_item_query("PALT-NOTFOUND")
        
        assert "not found in the system" in result["answer"]
        assert result["data"] is None
    
    def test_handle_anomaly_stats(self):
        """Test anomaly statistics query"""
        from datetime import date
        
        # Mock anomalies
        mock_anomaly1 = Mock()
        mock_anomaly1.type = "missing"
        mock_anomaly1.severity = "high"
        
        mock_anomaly2 = Mock()
        mock_anomaly2.type = "misplaced"
        mock_anomaly2.severity = "med"
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = [mock_anomaly1, mock_anomaly2]
        
        result = self.nlq_service._handle_anomaly_stats(date.today())
        
        assert "Found 2 anomalies" in result["answer"]
        assert result["data"]["total_anomalies"] == 2
        assert result["data"]["by_type"] == {"missing": 1, "misplaced": 1}
        assert result["data"]["by_severity"] == {"high": 1, "med": 1}
    
    def test_handle_anomaly_stats_no_anomalies(self):
        """Test anomaly statistics query with no anomalies"""
        from datetime import date
        
        # Mock empty anomalies list
        self.mock_db.query.return_value.filter.return_value.all.return_value = []
        
        result = self.nlq_service._handle_anomaly_stats(date.today())
        
        assert "No anomalies found" in result["answer"]
        assert "All looks good!" in result["answer"]
        assert result["data"]["total_anomalies"] == 0
    
    def test_handle_inventory_summary(self):
        """Test inventory summary query"""
        # Mock database counts
        self.mock_db.query.return_value.count.return_value = 100  # total items
        self.mock_db.query.return_value.distinct.return_value.count.return_value = 25  # total bins
        
        # Mock recent snapshots
        self.mock_db.query.return_value.filter.return_value.count.return_value = 15
        
        result = self.nlq_service._handle_inventory_summary()
        
        assert "100 total items" in result["answer"]
        assert "25 bins with activity" in result["answer"]
        assert "15 snapshots in last 24 hours" in result["answer"]
        assert result["data"]["total_items"] == 100
        assert result["data"]["active_bins"] == 25
        assert result["data"]["recent_snapshots"] == 15
    
    @pytest.mark.asyncio
    async def test_process_query_integration(self):
        """Test full query processing integration"""
        # Mock a simple bin query
        mock_snapshot = Mock()
        mock_snapshot.item_ids = ["PALT-0001"]
        mock_snapshot.ts = "2025-08-17T10:30:00"
        mock_snapshot.photo_ref = "test.jpg"
        mock_snapshot.conf = 0.9
        
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_snapshot
        
        with patch('backend.app.services.nlq.storage_manager') as mock_storage:
            mock_storage.get_file_url.return_value = "http://example.com/photo.jpg"
            
            result = self.nlq_service.process_query("What's in bin A54?")
        
        assert "answer" in result
        assert "data" in result
        assert result["data"]["bin_id"] == "A54"
        assert result["data"]["items"] == ["PALT-0001"]