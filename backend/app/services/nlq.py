from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import re
from datetime import datetime, date, timedelta
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
		
		# 智能日期识别和订单查询
		if self._is_order_query(query_text):
			return self._handle_smart_order_query(query_text)
		
		# Basic pattern matching for demonstration
		if any(pattern in query_text for pattern in ['bin', '库位', 'A54', 'S-01']):
			return self._handle_bin_query_placeholder("A54")
		elif any(pattern in query_text for pattern in ['sku', 'SKU-', '找']):
			return self._handle_sku_query_placeholder("SKU-001")
		elif any(pattern in query_text for pattern in ['order', '订单', 'SO-', 'TEST-']):
			return self._handle_order_query_placeholder("TEST-001")
		else:
			return {
				"answer": "I didn't understand that request. Try asking about bin contents, SKU locations, orders, or today's anomalies.",
				"data": None
			}
	
	def _is_order_query(self, query_text: str) -> bool:
		"""Check if this is an order-related query"""
		order_keywords = ['订单', 'order', '今天', 'today', '昨天', 'yesterday']
		date_patterns = [r'\d{1,2}[\.\-]\d{1,2}', r'\d{1,2}/\d{1,2}']
		
		# 检查是否包含订单关键词
		if any(keyword in query_text for keyword in order_keywords):
			return True
		
		# 检查是否包含日期格式
		for pattern in date_patterns:
			if re.search(pattern, query_text):
				return True
		
		return False
	
	def _handle_smart_order_query(self, query_text: str) -> Dict[str, Any]:
		"""Smart order query handler with date recognition"""
		try:
			# 尝试从数据库获取真实订单数据
			from ..models import Order
			
			# 识别查询类型
			if '今天' in query_text or 'today' in query_text:
				# 查询今天的订单
				today = date.today()
				orders = self.db.query(Order).filter(Order.ship_date == today).all()
				return self._format_orders_response(orders, f"今天 ({today.strftime('%Y-%m-%d')})")
			
			elif '昨天' in query_text or 'yesterday' in query_text:
				# 查询昨天的订单
				yesterday = date.today() - timedelta(days=1)
				orders = self.db.query(Order).filter(Order.ship_date == yesterday).all()
				return self._format_orders_response(orders, f"昨天 ({yesterday.strftime('%Y-%m-%d')})")
			
			else:
				# 检查日期格式 (如 8.19, 8-19, 8/19)
				date_match = re.search(r'(\d{1,2})[\.\-/](\d{1,2})', query_text)
				if date_match:
					month = int(date_match.group(1))
					day = int(date_match.group(2))
					current_year = datetime.now().year
					search_date = f"{current_year}-{month:02d}-{day:02d}"
					
					# 查询指定日期的订单
					orders = self.db.query(Order).filter(Order.ship_date == search_date).all()
					return self._format_orders_response(orders, f"{month}.{day} ({search_date})")
			
			# 如果没有找到特定日期，返回所有订单
			all_orders = self.db.query(Order).all()
			return self._format_orders_response(all_orders, "所有订单")
			
		except Exception as e:
			logger.error(f"Error in smart order query: {e}")
			# 如果数据库查询失败，返回占位符数据
			return self._handle_date_query_placeholder("2025-08-19")
	
	def _format_orders_response(self, orders: List[Order], date_label: str) -> Dict[str, Any]:
		"""Format orders response"""
		if not orders:
			return {
				"answer": f"{date_label} 没有找到订单。",
				"data": {
					"date": date_label,
					"order_count": 0,
					"total_quantity": 0,
					"orders": []
				}
			}
		
		order_count = len(orders)
		total_qty = sum(order.qty for order in orders)
		
		# 按SKU分组统计
		sku_summary = {}
		for order in orders:
			sku_summary[order.sku] = sku_summary.get(order.sku, 0) + order.qty
		
		sku_list = ", ".join([f"{qty} {sku}" for sku, qty in sku_summary.items()])
		
		answer = f"{date_label} 找到 {order_count} 个订单: {sku_list} (总数量: {total_qty})"
		
		return {
			"answer": answer,
			"data": {
				"date": date_label,
				"order_count": order_count,
				"total_quantity": total_qty,
				"sku_summary": sku_summary,
				"orders": [
					{
						"order_id": order.order_id,
						"sku": order.sku,
						"qty": order.qty,
						"ship_date": order.ship_date.isoformat() if hasattr(order.ship_date, 'isoformat') else str(order.ship_date),
						"status": order.status,
						"item_ids": order.item_ids
					}
					for order in orders
				]
			}
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