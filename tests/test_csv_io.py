import pytest
from datetime import date
from backend.app.utils.csv_io import (
    parse_orders_csv, 
    parse_allocations_csv, 
    parse_bins_csv,
    validate_csv_structure,
    generate_anomalies_csv
)


class TestCSVParsing:
    def test_parse_orders_csv_valid(self):
        """Test parsing valid orders CSV"""
        csv_content = """order_id,ship_date,sku,qty,item_ids,status
SO-1001,2025-08-17,SKU-5566,2,"[""PALT-0001"",""PALT-0002""]",pending
SO-1002,2025-08-17,SKU-8899,1,,pending"""
        
        orders = parse_orders_csv(csv_content)
        
        assert len(orders) == 2
        assert orders[0]['order_id'] == 'SO-1001'
        assert orders[0]['ship_date'] == date(2025, 8, 17)
        assert orders[0]['qty'] == 2
        assert orders[0]['item_ids'] == ['PALT-0001', 'PALT-0002']
        assert orders[1]['item_ids'] is None
    
    def test_parse_orders_csv_semicolon_separated(self):
        """Test parsing orders CSV with semicolon-separated item IDs"""
        csv_content = """order_id,ship_date,sku,qty,item_ids
SO-1001,2025-08-17,SKU-5566,2,PALT-0001;PALT-0002"""
        
        orders = parse_orders_csv(csv_content)
        
        assert len(orders) == 1
        assert orders[0]['item_ids'] == ['PALT-0001', 'PALT-0002']
    
    def test_parse_orders_csv_invalid_date(self):
        """Test parsing orders CSV with invalid date format"""
        csv_content = """order_id,ship_date,sku,qty,item_ids
SO-1001,invalid-date,SKU-5566,2,"""
        
        orders = parse_orders_csv(csv_content)
        
        assert len(orders) == 1
        assert orders[0]['ship_date'] is None
    
    def test_parse_allocations_csv_valid(self):
        """Test parsing valid allocations CSV"""
        csv_content = """item_id,bin_id,status
PALT-0001,A54,allocated
PALT-0002,A52,picked"""
        
        allocations = parse_allocations_csv(csv_content)
        
        assert len(allocations) == 2
        assert allocations[0]['item_id'] == 'PALT-0001'
        assert allocations[0]['bin_id'] == 'A54'
        assert allocations[0]['status'] == 'allocated'
        assert allocations[1]['status'] == 'picked'
    
    def test_parse_bins_csv_valid(self):
        """Test parsing valid bins CSV"""
        csv_content = """bin_id,zone,coords
A54,Zone-A,10,20
S-01,Staging,"""
        
        bins = parse_bins_csv(csv_content)
        
        assert len(bins) == 2
        assert bins[0]['bin_id'] == 'A54'
        assert bins[0]['zone'] == 'Zone-A'
        assert bins[0]['coords'] == '10,20'
        assert bins[1]['zone'] == 'Staging'
        assert bins[1]['coords'] is None
    
    def test_parse_orders_csv_missing_required_fields(self):
        """Test parsing orders CSV with missing required fields"""
        csv_content = """order_id,ship_date,sku,qty
,2025-08-17,SKU-5566,2
SO-1002,2025-08-17,,1"""
        
        orders = parse_orders_csv(csv_content)
        
        # Should skip rows with missing required fields
        assert len(orders) == 0
    
    def test_validate_csv_structure_valid(self):
        """Test CSV structure validation with valid headers"""
        csv_content = """order_id,ship_date,sku,qty
SO-1001,2025-08-17,SKU-5566,2"""
        
        required_columns = ['order_id', 'sku', 'qty']
        result = validate_csv_structure(csv_content, required_columns)
        
        assert result is True
    
    def test_validate_csv_structure_missing_columns(self):
        """Test CSV structure validation with missing required columns"""
        csv_content = """order_id,sku
SO-1001,SKU-5566"""
        
        required_columns = ['order_id', 'sku', 'qty']
        result = validate_csv_structure(csv_content, required_columns)
        
        assert result is False


class TestCSVGeneration:
    def test_generate_anomalies_csv_empty(self):
        """Test generating CSV from empty anomalies list"""
        anomalies = []
        csv_content = generate_anomalies_csv(anomalies)
        
        assert csv_content == "No anomalies found"
    
    def test_generate_anomalies_csv_with_data(self):
        """Test generating CSV from anomalies data"""
        from datetime import datetime
        
        anomalies = [
            {
                'id': 1,
                'ts': datetime(2025, 8, 17, 10, 30, 0),
                'type': 'missing',
                'bin_id': 'A54',
                'item_id': 'PALT-0001',
                'order_id': 'SO-1001',
                'severity': 'high',
                'detail': 'Item not found in expected bin',
                'status': 'open'
            }
        ]
        
        csv_content = generate_anomalies_csv(anomalies)
        
        assert 'id,ts,type,bin_id,item_id,order_id,severity,detail,status' in csv_content
        assert '1,2025-08-17 10:30:00,missing,A54,PALT-0001,SO-1001,high,Item not found in expected bin,open' in csv_content
    
    def test_generate_inventory_csv(self):
        """Test generating inventory CSV"""
        from backend.app.utils.csv_io import generate_inventory_csv
        from datetime import datetime
        
        inventory_data = [
            {
                'bin_id': 'A54',
                'item_ids': ['PALT-0001', 'PALT-0002'],
                'last_seen': datetime(2025, 8, 17, 10, 30, 0),
                'photo_ref': 'local://photos/2025-08-17/A54_103000.jpg'
            }
        ]
        
        csv_content = generate_inventory_csv(inventory_data)
        
        assert 'bin_id,item_ids,last_seen,photo_ref' in csv_content
        assert 'A54' in csv_content
        assert 'PALT-0001' in csv_content