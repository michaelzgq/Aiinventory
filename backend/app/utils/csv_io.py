import csv
import json
from io import StringIO
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


def parse_orders_csv(csv_content: str) -> List[Dict[str, Any]]:
	"""Parse orders CSV content and return list of order dictionaries"""
	try:
		reader = csv.DictReader(StringIO(csv_content))
		orders = []
		
		for row in reader:
			# Parse item_ids from JSON or semicolon-separated string
			item_ids_str = row.get('item_ids', '').strip()
			item_ids = None
			
			if item_ids_str:
				try:
					# Try parsing as JSON first
					item_ids = json.loads(item_ids_str)
				except json.JSONDecodeError:
					# Fall back to semicolon-separated
					item_ids = [id.strip() for id in item_ids_str.split(';') if id.strip()]
			
			# Parse ship_date
			ship_date_str = row.get('ship_date', '').strip()
			ship_date = None
			if ship_date_str:
				try:
					ship_date = datetime.strptime(ship_date_str, '%Y-%m-%d').date()
				except ValueError:
					logger.warning(f"Invalid ship_date format: {ship_date_str}")
			
			order = {
				'order_id': row.get('order_id', '').strip(),
				'ship_date': ship_date,
				'sku': row.get('sku', '').strip(),
				'qty': int(row.get('qty', 0)),
				'item_ids': item_ids,
				'status': row.get('status', 'pending').strip()
			}
			
			if order['order_id'] and order['sku']:
				orders.append(order)
		
		return orders
	
	except Exception as e:
		logger.error(f"Error parsing orders CSV: {e}")
		raise ValueError(f"Invalid CSV format: {e}")


def parse_allocations_csv(csv_content: str) -> List[Dict[str, Any]]:
	"""Parse allocations CSV content and return list of allocation dictionaries"""
	try:
		reader = csv.DictReader(StringIO(csv_content))
		allocations = []
		
		for row in reader:
			allocation = {
				'item_id': row.get('item_id', '').strip(),
				'bin_id': row.get('bin_id', '').strip(),
				'status': row.get('status', 'allocated').strip()
			}
			
			if allocation['item_id'] and allocation['bin_id']:
				allocations.append(allocation)
		
		return allocations
	
	except Exception as e:
		logger.error(f"Error parsing allocations CSV: {e}")
		raise ValueError(f"Invalid CSV format: {e}")


def parse_bins_csv(csv_content: str) -> List[Dict[str, Any]]:
	"""Parse bins CSV content and return list of bin dictionaries"""
	try:
		# 使用 csv.reader 以便处理 coords 中包含逗号的情况
		reader = csv.reader(StringIO(csv_content))
		rows = list(reader)
		if not rows:
			return []
		# 头部
		header = [h.strip() for h in rows[0]]
		# 标准列顺序: bin_id, zone, coords
		bins = []
		for row in rows[1:]:
			if not row:
				continue
			# 填充缺省列
			# 允许 coords 包含逗号：将第3列及以后合并
			bin_id = (row[0].strip() if len(row) > 0 else '')
			zone = (row[1].strip() if len(row) > 1 else '')
			coords = ''
			if len(row) >= 3:
				coords = ','.join([c.strip() for c in row[2:]]).strip()
			
			bin_data = {
				'bin_id': bin_id,
				'zone': zone or None,
				'coords': coords or None
			}
			if bin_data['bin_id']:
				bins.append(bin_data)
		return bins
	
	except Exception as e:
		logger.error(f"Error parsing bins CSV: {e}")
		raise ValueError(f"Invalid CSV format: {e}")


def generate_anomalies_csv(anomalies: List[Dict[str, Any]]) -> str:
	"""Generate CSV content from anomalies data"""
	try:
		output = StringIO()
		
		if not anomalies:
			return "No anomalies found"
		
		fieldnames = ['id', 'ts', 'type', 'bin_id', 'item_id', 'order_id', 'severity', 'detail', 'status']
		writer = csv.DictWriter(output, fieldnames=fieldnames)
		
		writer.writeheader()
		for anomaly in anomalies:
			# Format timestamp
			ts = anomaly.get('ts')
			if isinstance(ts, datetime):
				ts_str = ts.strftime('%Y-%m-%d %H:%M:%S')
			else:
				ts_str = str(ts) if ts else ''
			
			row = {
				'id': anomaly.get('id', ''),
				'ts': ts_str,
				'type': anomaly.get('type', ''),
				'bin_id': anomaly.get('bin_id', ''),
				'item_id': anomaly.get('item_id', ''),
				'order_id': anomaly.get('order_id', ''),
				'severity': anomaly.get('severity', ''),
				'detail': anomaly.get('detail', ''),
				'status': anomaly.get('status', '')
			}
			writer.writerow(row)
		
		return output.getvalue()
	
	except Exception as e:
		logger.error(f"Error generating anomalies CSV: {e}")
		raise


def generate_inventory_csv(inventory_data: List[Dict[str, Any]]) -> str:
	"""Generate CSV content from current inventory data"""
	try:
		output = StringIO()
		
		if not inventory_data:
			return "No inventory data found"
		
		fieldnames = ['bin_id', 'item_ids', 'last_seen', 'photo_ref']
		writer = csv.DictWriter(output, fieldnames=fieldnames)
		
		writer.writeheader()
		for item in inventory_data:
			# Format item_ids as JSON string
			item_ids = item.get('item_ids', [])
			item_ids_str = json.dumps(item_ids) if item_ids else ''
			
			# Format timestamp
			last_seen = item.get('last_seen')
			if isinstance(last_seen, datetime):
				last_seen_str = last_seen.strftime('%Y-%m-%d %H:%M:%S')
			else:
				last_seen_str = str(last_seen) if last_seen else ''
			
			row = {
				'bin_id': item.get('bin_id', ''),
				'item_ids': item_ids_str,
				'last_seen': last_seen_str,
				'photo_ref': item.get('photo_ref', '')
			}
			writer.writerow(row)
		
		return output.getvalue()
	
	except Exception as e:
		logger.error(f"Error generating inventory CSV: {e}")
		raise


def validate_csv_structure(csv_content: str, required_columns: List[str]) -> bool:
	"""Validate that CSV has required columns"""
	try:
		reader = csv.DictReader(StringIO(csv_content))
		headers = reader.fieldnames or []
		
		missing_columns = [col for col in required_columns if col not in headers]
		if missing_columns:
			raise ValueError(f"Missing required columns: {missing_columns}")
		
		return True
	
	except Exception as e:
		logger.error(f"CSV validation error: {e}")
		return False