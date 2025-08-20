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
		# 尝试加载核心实现，如果不存在则使用占位符
		self._load_core_implementation()
	
	def _load_core_implementation(self):
		"""Load core implementation if available, otherwise use placeholder"""
		try:
			# 尝试导入核心实现
			from .ai_core.core_impl import CoreNLQEngine
			self.core_engine = CoreNLQEngine(self.db)
			self.use_core = True
			logger.info("Core NLQ engine loaded successfully")
		except ImportError:
			# 使用占位符实现
			self.core_engine = None
			self.use_core = False
			logger.info("Using placeholder NLQ implementation")
	
	def process_query(self, query_text: str) -> Dict[str, Any]:
		"""Process natural language query and return response"""
		try:
			# 如果核心引擎可用，使用核心实现
			if self.use_core and self.core_engine:
				return self.core_engine.process_query(query_text)
			
			# 否则使用占位符实现
			return self._process_query_placeholder(query_text)
			
		except Exception as e:
			logger.error(f"Error processing NLQ: {e}")
			return {
				"answer": "Sorry, I encountered an error processing your request.",
				"data": None
			}
	
	def _process_query_placeholder(self, query_text: str) -> Dict[str, Any]:
		"""Placeholder implementation for demonstration purposes"""
		query_text = query_text.strip().lower()
		
		# Basic pattern matching for demonstration
		if any(pattern in query_text for pattern in ['bin', '库位', 'A54', 'S-01']):
			return self._handle_bin_query_placeholder("A54")
		elif any(pattern in query_text for pattern in ['sku', 'SKU-', '找']):
			return self._handle_sku_query_placeholder("SKU-001")
		elif any(pattern in query_text for pattern in ['order', '订单', 'SO-', 'TEST-']):
			return self._handle_order_query_placeholder("TEST-001")
		elif any(pattern in query_text for pattern in ['8.19', '8-19', '8/19']):
			return self._handle_date_query_placeholder("2025-08-19")
		else:
			return {
				"answer": "I didn't understand that request. Try asking about bin contents, SKU locations, orders, or today's anomalies.",
				"data": None
			}
	
	def _handle_bin_query_placeholder(self, bin_id: str) -> Dict[str, Any]:
		"""Placeholder bin query handler"""
		return {
			"answer": f"Bin {bin_id} contains 3 items: ITEM-001, ITEM-002, ITEM-003. (Placeholder data)",
			"data": {
				"bin_id": bin_id,
				"items": ["ITEM-001", "ITEM-002", "ITEM-003"],
				"items_count": 3,
				"confidence": 0.95
			}
		}
	
	def _handle_sku_query_placeholder(self, sku: str) -> Dict[str, Any]:
		"""Placeholder SKU query handler"""
		return {
			"answer": f"SKU {sku} is located in bin A54 with 2 items. (Placeholder data)",
			"data": {
				"sku": sku,
				"total_items": 2,
				"found_items": 2,
				"locations": [{"item_id": "ITEM-001", "bin": "A54", "status": "found"}]
			}
		}
	
	def _handle_order_query_placeholder(self, order_id: str) -> Dict[str, Any]:
		"""Placeholder order query handler"""
		return {
			"answer": f"Order {order_id}: SKU SKU-001, Quantity 2, Ship Date 2025-08-19, Status Active. (Placeholder data)",
			"data": {
				"order_id": order_id,
				"sku": "SKU-001",
				"qty": 2,
				"ship_date": "2025-08-19",
				"status": "Active"
			}
		}
	
	def _handle_date_query_placeholder(self, date_str: str) -> Dict[str, Any]:
		"""Placeholder date query handler"""
		return {
			"answer": f"Found 2 orders for {date_str}: 1 SKU-001, 1 SKU-002 (total quantity: 2). (Placeholder data)",
			"data": {
				"date": date_str,
				"order_count": 2,
				"total_quantity": 2,
				"orders": [
					{"order_id": "TEST-001", "sku": "SKU-001", "qty": 1},
					{"order_id": "TEST-002", "sku": "SKU-002", "qty": 1}
				]
			}
		}


def create_nlq_service(db: Session) -> NaturalLanguageQueryService:
    """Factory function to create NLQ service - 保持向后兼容"""
    return NaturalLanguageQueryService(db)