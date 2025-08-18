from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import re
from datetime import datetime, date
import logging
from ..models import Snapshot, Item, Anomaly, Allocation
from ..utils.storage import storage_manager

logger = logging.getLogger(__name__)


class NaturalLanguageQueryService:
	def __init__(self, db: Session):
		self.db = db
	
	def process_query(self, query_text: str) -> Dict[str, Any]:
		"""Process natural language query and return response"""
		try:
			query_text = query_text.strip().lower()
			
			# Identify intent and extract entities
			intent, entities = self._parse_intent(query_text)
			
			if intent == "check_bin":
				return self._handle_bin_query(entities.get("bin_id"))
			
			elif intent == "find_sku":
				return self._handle_sku_query(entities.get("sku"))
			
			elif intent == "find_item":
				return self._handle_item_query(entities.get("item_id"))
			
			elif intent == "export_report":
				return self._handle_export_request(entities.get("date"))
			
			elif intent == "anomaly_stats":
				return self._handle_anomaly_stats(entities.get("date"))
			
			elif intent == "inventory_summary":
				return self._handle_inventory_summary()
			
			else:
				return {
					"answer": "I didn't understand that request. Try asking about bin contents, SKU locations, or today's anomalies.",
					"data": None
				}
		
		except Exception as e:
			logger.error(f"Error processing NLQ: {e}")
			return {
				"answer": "Sorry, I encountered an error processing your request.",
				"data": None
			}
	
	def _parse_intent(self, query_text: str) -> tuple[str, Dict[str, Any]]:
		"""Parse query text to identify intent and extract entities"""
		entities = {}
		
		# Check bin patterns (A54, 库位A54, 看看A54)
		bin_patterns = [
			# 英文/中文短语 + bin id
			r'(?:bin\s+|库位\s*|看看\s*|查\s*)([A-Z]\d{1,3}|S-\d{1,2})',
			# bin id + 描述
			r'([A-Z]\d{1,3}|S-\d{1,2})(?:\s*现在有什么|.*有什么|.*内容)',
			# 英文问句
			r'what.+in\s+([A-Z]\d{1,3}|S-\d{1,2})',
			r'check\s+([A-Z]\d{1,3}|S-\d{1,2})'
		]
		for pattern in bin_patterns:
			match = re.search(pattern, query_text, re.IGNORECASE)
			if match:
				entities["bin_id"] = match.group(1).upper()
				return "check_bin", entities
		
		# Check SKU patterns — 确保捕获完整 token 如 SKU-5566
		sku_patterns = [
			r'(?:sku\s*|找\s*)(SKU-[A-Z0-9]+)',
			r'find.+sku.+(SKU-[A-Z0-9]+)',
			r'where.+(SKU-[A-Z0-9]+)'
		]
		for pattern in sku_patterns:
			match = re.search(pattern, query_text, re.IGNORECASE)
			if match:
				entities["sku"] = match.group(1).upper()
				return "find_sku", entities
		
		# Check item ID patterns — 确保捕获 PALT-0001 等
		item_patterns = [
			r'(?:item\s+|托盘\s*|找\s*)(PALT-\d+|ITEM-\d+|[A-Z]+-\d+)',
			r'where\s+is\s+(PALT-\d+|ITEM-\d+|[A-Z]+-\d+)[\?\.!]?',
			r'(PALT-\d+|ITEM-\d+|[A-Z]+-\d+).*在哪'
		]
		for pattern in item_patterns:
			match = re.search(pattern, query_text, re.IGNORECASE)
			if match:
				entities["item_id"] = match.group(1).upper()
				return "find_item", entities
		
		# Check export/report patterns
		export_patterns = [
			r'(?:导出|下载|export|download).+(?:报告|report)',
			r'(?:差异|异常|anomal).+(?:报告|report)',
			r'generate.+report'
		]
		for pattern in export_patterns:
			if re.search(pattern, query_text, re.IGNORECASE):
				# Look for date
				if "今天" in query_text or "today" in query_text:
					entities["date"] = date.today()
				elif "昨天" in query_text or "yesterday" in query_text:
					from datetime import timedelta
					entities["date"] = date.today() - timedelta(days=1)
				else:
					entities["date"] = date.today()
				return "export_report", entities
		
		# Check anomaly stats patterns
		anomaly_patterns = [
			r'(?:今天|today).+(?:异常|anomal|差异)',
			r'(?:异常|anomal).+(?:数量|count|统计)',
			r'how many.+(?:异常|anomal)'
		]
		for pattern in anomaly_patterns:
			if re.search(pattern, query_text, re.IGNORECASE):
				entities["date"] = date.today()
				return "anomaly_stats", entities
		
		# Check inventory summary patterns — 覆盖中文“库存总览”
		summary_patterns = [
			r'(?:库存\s*总览|库存\s*概览|inventory\s*summary|库存总览|库存概览)',
			r'current.+inventory',
			r'总共有多少'
		]
		for pattern in summary_patterns:
			if re.search(pattern, query_text, re.IGNORECASE):
				return "inventory_summary", entities
		
		return "unknown", entities
	
	def _handle_bin_query(self, bin_id: str) -> Dict[str, Any]:
		"""Handle bin content query"""
		if not bin_id:
			return {"answer": "Please specify a bin ID (like A54 or S-01).", "data": None}
		
		try:
			# Get latest snapshot for this bin
			latest_snapshot = (
				self.db.query(Snapshot)
				.filter(Snapshot.bin_id == bin_id)
				.order_by(Snapshot.ts.desc())
				.first()
			)
			
			if not latest_snapshot:
				return {
					"answer": f"No recent snapshots found for bin {bin_id}. The bin may not have been scanned recently.",
					"data": {"bin_id": bin_id, "items": []}
				}
			
			item_ids = latest_snapshot.item_ids or []
			photo_url = storage_manager.get_file_url(latest_snapshot.photo_ref) if latest_snapshot.photo_ref else None
			
			# 兼容 ts 可能为字符串的情况（测试里使用字符串）
			try:
				last_scanned_human = latest_snapshot.ts.strftime('%Y-%m-%d %H:%M')
			except Exception:
				last_scanned_human = str(latest_snapshot.ts)
			
			if not item_ids:
				answer = f"Bin {bin_id} appears to be empty (last scanned: {last_scanned_human})."
			else:
				answer = f"Bin {bin_id} contains {len(item_ids)} items: {', '.join(item_ids[:5])}{'...' if len(item_ids) > 5 else ''} (last scanned: {last_scanned_human})."
			
			return {
				"answer": answer,
				"data": {
					"bin_id": bin_id,
					"items": item_ids,
					"last_scanned": latest_snapshot.ts if isinstance(latest_snapshot.ts, str) else latest_snapshot.ts.isoformat(),
					"photo_url": photo_url,
					"confidence": latest_snapshot.conf
				}
			}
		
		except Exception as e:
			logger.error(f"Error handling bin query: {e}")
			return {"answer": f"Error retrieving data for bin {bin_id}.", "data": None}
	
	def _handle_sku_query(self, sku: str) -> Dict[str, Any]:
		"""Handle SKU location query"""
		if not sku:
			return {"answer": "Please specify a SKU to search for.", "data": None}
		
		try:
			# Find items with this SKU
			items = self.db.query(Item).filter(Item.sku == sku).all()
			
			if not items:
				return {
					"answer": f"No items found for SKU {sku}.",
					"data": {"sku": sku, "locations": []}
				}
			
			# Get locations from allocations and snapshots
			locations = []
			for item in items:
				# Check allocation
				allocation = self.db.query(Allocation).filter(Allocation.item_id == item.item_id).first()
				expected_bin = allocation.bin_id if allocation else None
				
				# Check latest snapshot
				snapshot = (
					self.db.query(Snapshot)
					.filter(Snapshot.item_ids.contains([item.item_id]))
					.order_by(Snapshot.ts.desc())
					.first()
				)
				
				actual_bin = snapshot.bin_id if snapshot else None
				last_seen = snapshot.ts if snapshot else None
				
				location_info = {
					"item_id": item.item_id,
					"expected_bin": expected_bin,
					"actual_bin": actual_bin,
					"last_seen": last_seen.isoformat() if last_seen else None,
					"status": "found" if actual_bin else "missing"
				}
				locations.append(location_info)
			
			found_count = sum(1 for loc in locations if loc["status"] == "found")
			answer = f"Found {len(items)} items for SKU {sku}. {found_count} are currently visible in the warehouse."
			
			return {
				"answer": answer,
				"data": {
					"sku": sku,
					"total_items": len(items),
					"found_items": found_count,
					"locations": locations
				}
			}
		
		except Exception as e:
			logger.error(f"Error handling SKU query: {e}")
			return {"answer": f"Error searching for SKU {sku}.", "data": None}
	
	def _handle_item_query(self, item_id: str) -> Dict[str, Any]:
		"""Handle specific item location query"""
		if not item_id:
			return {"answer": "Please specify an item ID to search for.", "data": None}
		
		try:
			# Get item info
			item = self.db.query(Item).filter(Item.item_id == item_id).first()
			
			if not item:
				return {
					"answer": f"Item {item_id} not found in the system.",
					"data": None
				}
			
			# Get allocation
			allocation = self.db.query(Allocation).filter(Allocation.item_id == item_id).first()
			expected_bin = allocation.bin_id if allocation else None
			
			# Get latest snapshot
			snapshot = (
				self.db.query(Snapshot)
				.filter(Snapshot.item_ids.contains([item_id]))
				.order_by(Snapshot.ts.desc())
				.first()
			)
			
			if snapshot:
				answer = f"Item {item_id} (SKU: {item.sku}) was last seen in bin {snapshot.bin_id} at {snapshot.ts.strftime('%Y-%m-%d %H:%M')}."
				photo_url = storage_manager.get_file_url(snapshot.photo_ref) if snapshot.photo_ref else None
			else:
				answer = f"Item {item_id} (SKU: {item.sku}) has not been seen in recent snapshots."
				photo_url = None
			
			if expected_bin and snapshot and snapshot.bin_id != expected_bin:
				answer += f" (Expected in {expected_bin})"
			
			return {
				"answer": answer,
				"data": {
					"item_id": item_id,
					"sku": item.sku,
					"expected_bin": expected_bin,
					"actual_bin": snapshot.bin_id if snapshot else None,
					"last_seen": snapshot.ts.isoformat() if snapshot else None,
					"photo_url": photo_url
				}
			}
		
		except Exception as e:
			logger.error(f"Error handling item query: {e}")
			return {"answer": f"Error searching for item {item_id}.", "data": None}
	
	def _handle_export_request(self, target_date: date) -> Dict[str, Any]:
		"""Handle export report request"""
		try:
			date_str = target_date.strftime('%Y-%m-%d')
			answer = f"Reconciliation report for {date_str} can be generated via the reconcile API endpoint."
			
			return {
				"answer": answer,
				"data": {
					"date": date_str,
					"endpoint": f"/api/reconcile/run?date={date_str}",
					"suggestion": "Use the reconcile page or API to generate the report."
				}
			}
		
		except Exception as e:
			logger.error(f"Error handling export request: {e}")
			return {"answer": "Error processing export request.", "data": None}
	
	def _handle_anomaly_stats(self, target_date: date) -> Dict[str, Any]:
		"""Handle anomaly statistics query"""
		try:
			from datetime import timedelta
			
			anomalies = (
				self.db.query(Anomaly)
				.filter(
					Anomaly.ts >= target_date,
					Anomaly.ts < target_date + timedelta(days=1)
				)
				.all()
			)
			
			total_count = len(anomalies)
			type_counts = {}
			severity_counts = {}
			
			for anomaly in anomalies:
				type_counts[anomaly.type] = type_counts.get(anomaly.type, 0) + 1
				severity_counts[anomaly.severity] = severity_counts.get(anomaly.severity, 0) + 1
			
			if total_count == 0:
				answer = f"No anomalies found for {target_date.strftime('%Y-%m-%d')}. All looks good!"
			else:
				answer = f"Found {total_count} anomalies for {target_date.strftime('%Y-%m-%d')}."
				if type_counts:
					type_summary = ", ".join([f"{count} {type_}" for type_, count in type_counts.items()])
					answer += f" Types: {type_summary}."
			
			return {
				"answer": answer,
				"data": {
					"date": target_date.strftime('%Y-%m-%d'),
					"total_anomalies": total_count,
					"by_type": type_counts,
					"by_severity": severity_counts
				}
			}
		
		except Exception as e:
			logger.error(f"Error handling anomaly stats: {e}")
			return {"answer": "Error retrieving anomaly statistics.", "data": None}
	
	def _handle_inventory_summary(self) -> Dict[str, Any]:
		"""Handle inventory summary query"""
		try:
			# Get counts
			total_items = self.db.query(Item).count()
			total_bins = self.db.query(Snapshot.bin_id).distinct().count()
			
			# Get recent snapshot count
			from datetime import timedelta
			recent_snapshots = (
				self.db.query(Snapshot)
				.filter(Snapshot.ts >= datetime.now() - timedelta(hours=24))
				.count()
			)
			
			answer = f"Inventory summary: {total_items} total items, {total_bins} bins with activity, {recent_snapshots} snapshots in last 24 hours."
			
			return {
				"answer": answer,
				"data": {
					"total_items": total_items,
					"active_bins": total_bins,
					"recent_snapshots": recent_snapshots,
					"last_updated": datetime.now().isoformat()
				}
			}
		
		except Exception as e:
			logger.error(f"Error handling inventory summary: {e}")
			return {"answer": "Error retrieving inventory summary.", "data": None}


def create_nlq_service(db: Session) -> NaturalLanguageQueryService:
	"""Factory function to create NLQ service"""
	return NaturalLanguageQueryService(db)