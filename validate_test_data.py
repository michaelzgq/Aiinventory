#!/usr/bin/env python3
"""
测试数据验证脚本
验证生成的测试数据格式是否正确
"""

import csv
import os
from typing import List, Dict, Any

def validate_csv_file(file_path: str, required_fields: List[str]) -> Dict[str, Any]:
    """验证 CSV 文件"""
    result = {
        'file': file_path,
        'valid': False,
        'record_count': 0,
        'errors': [],
        'warnings': []
    }
    
    try:
        if not os.path.exists(file_path):
            result['errors'].append(f"文件不存在: {file_path}")
            return result
        
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # 检查必需字段
            missing_fields = [field for field in required_fields if field not in reader.fieldnames]
            if missing_fields:
                result['errors'].append(f"缺少必需字段: {missing_fields}")
                return result
            
            # 验证数据
            records = list(reader)
            result['record_count'] = len(records)
            
            if result['record_count'] == 0:
                result['warnings'].append("文件为空")
            else:
                result['valid'] = True
                
                # 检查数据质量
                for i, record in enumerate(records, 1):
                    for field in required_fields:
                        if field not in record or not record[field]:
                            result['warnings'].append(f"第 {i} 行 {field} 字段为空")
                
                # 特定字段验证
                if 'orders.csv' in file_path:
                    validate_orders_data(records, result)
                elif 'bins.csv' in file_path:
                    validate_bins_data(records, result)
                elif 'allocations.csv' in file_path:
                    validate_allocations_data(records, result)
                elif 'snapshots.csv' in file_path:
                    validate_snapshots_data(records, result)
    
    except Exception as e:
        result['errors'].append(f"验证异常: {str(e)}")
    
    return result

def validate_orders_data(records: List[Dict[str, Any]], result: Dict[str, Any]):
    """验证订单数据"""
    for i, record in enumerate(records, 1):
        # 检查订单ID格式
        if not record['order_id'].startswith('SO-'):
            result['warnings'].append(f"第 {i} 行订单ID格式不正确: {record['order_id']}")
        
        # 检查数量
        try:
            qty = int(record['qty'])
            if qty <= 0:
                result['warnings'].append(f"第 {i} 行数量不正确: {qty}")
        except ValueError:
            result['warnings'].append(f"第 {i} 行数量不是有效数字: {record['qty']}")

def validate_bins_data(records: List[Dict[str, Any]], result: Dict[str, Any]):
    """验证库位数据"""
    zones = set()
    for i, record in enumerate(records, 1):
        zones.add(record['zone'])
        
        # 检查库位ID格式
        bin_id = record['bin_id']
        if not (bin_id.startswith(('A', 'B', 'C', 'D', 'S-', 'R-', 'Q-'))):
            result['warnings'].append(f"第 {i} 行库位ID格式不正确: {bin_id}")
    
    result['info'] = f"包含区域: {', '.join(sorted(zones))}"

def validate_allocations_data(records: List[Dict[str, Any]], result: Dict[str, Any]):
    """验证分配数据"""
    statuses = set()
    for i, record in enumerate(records, 1):
        statuses.add(record['status'])
        
        # 检查商品ID格式
        if not record['item_id'].startswith('PALT-'):
            result['warnings'].append(f"第 {i} 行商品ID格式不正确: {record['item_id']}")
    
    result['info'] = f"包含状态: {', '.join(sorted(statuses))}"

def validate_snapshots_data(records: List[Dict[str, Any]], result: Dict[str, Any]):
    """验证快照数据"""
    for i, record in enumerate(records, 1):
        # 检查置信度
        try:
            conf = float(record['conf'])
            if not (0 <= conf <= 1):
                result['warnings'].append(f"第 {i} 行置信度超出范围: {conf}")
        except ValueError:
            result['warnings'].append(f"第 {i} 行置信度不是有效数字: {record['conf']}")

def main():
    """主函数"""
    print("🔍 测试数据验证")
    print("="*50)
    
    # 定义验证规则
    validation_rules = {
        'sample_data/orders.csv': ['order_id', 'ship_date', 'sku', 'qty', 'item_ids', 'status'],
        'sample_data/bins.csv': ['bin_id', 'zone', 'coords'],
        'sample_data/allocations.csv': ['item_id', 'bin_id', 'status'],
        'sample_data/snapshots.csv': ['snapshot_id', 'ts', 'bin_id', 'item_ids', 'photo_ref', 'conf', 'notes']
    }
    
    all_valid = True
    total_records = 0
    
    for file_path, required_fields in validation_rules.items():
        print(f"\n📁 验证文件: {file_path}")
        result = validate_csv_file(file_path, required_fields)
        
        if result['valid']:
            print(f"  ✅ 验证通过 - {result['record_count']} 条记录")
            total_records += result['record_count']
            
            if 'info' in result and result['info']:
                print(f"  ℹ️  {result['info']}")
        else:
            print(f"  ❌ 验证失败")
            all_valid = False
        
        if result['warnings']:
            print(f"  ⚠️  警告:")
            for warning in result['warnings']:
                print(f"    • {warning}")
        
        if result['errors']:
            print(f"  🚨 错误:")
            for error in result['errors']:
                print(f"    • {error}")
    
    print(f"\n{'='*50}")
    print("📊 验证结果汇总")
    print(f"{'='*50}")
    print(f"总体状态: {'✅ 全部通过' if all_valid else '❌ 存在问题'}")
    print(f"总记录数: {total_records}")
    
    if all_valid:
        print("\n🎉 所有测试数据验证通过！")
        print("💡 现在可以将数据导入到 Render 进行功能测试了。")
    else:
        print("\n⚠️ 部分数据存在问题，请检查上述错误和警告。")

if __name__ == "__main__":
    main()
