from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime, date, timedelta
import io
import logging
from ..models import Anomaly, Snapshot, Order
from ..utils.csv_io import generate_anomalies_csv, generate_inventory_csv
from ..utils.storage import storage_manager

logger = logging.getLogger(__name__)


class ReportService:
    def __init__(self, db: Session):
        self.db = db
    
    def generate_reconciliation_report(self, target_date: date) -> Dict[str, str]:
        """Generate reconciliation report in CSV and PDF formats"""
        try:
            # Get anomalies for the date
            anomalies = self._get_anomalies_for_date(target_date)
            snapshots = self._get_snapshots_for_date(target_date)
            orders = self._get_orders_for_date(target_date)
            
            # Generate CSV report
            csv_content = self._generate_csv_report(anomalies, snapshots, orders, target_date)
            csv_filename = f"reconciliation_{target_date.strftime('%Y%m%d')}.csv"
            csv_ref = storage_manager.save_report(csv_content.encode('utf-8'), csv_filename, "text/csv")
            
            # Generate PDF report
            pdf_content = self._generate_pdf_report(anomalies, snapshots, orders, target_date)
            pdf_filename = f"reconciliation_{target_date.strftime('%Y%m%d')}.pdf"
            pdf_ref = storage_manager.save_report(pdf_content, pdf_filename, "application/pdf")
            
            return {
                "csv_url": storage_manager.get_file_url(csv_ref),
                "pdf_url": storage_manager.get_file_url(pdf_ref),
                "csv_ref": csv_ref,
                "pdf_ref": pdf_ref
            }
        
        except Exception as e:
            logger.error(f"Error generating reconciliation report: {e}")
            raise
    
    def generate_inventory_report(self) -> Dict[str, str]:
        """Generate current inventory report"""
        try:
            # Get current inventory data
            inventory_data = self._get_current_inventory()
            
            # Generate CSV
            csv_content = generate_inventory_csv(inventory_data)
            csv_filename = f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            csv_ref = storage_manager.save_report(csv_content.encode('utf-8'), csv_filename, "text/csv")
            
            return {
                "csv_url": storage_manager.get_file_url(csv_ref),
                "csv_ref": csv_ref,
                "record_count": len(inventory_data)
            }
        
        except Exception as e:
            logger.error(f"Error generating inventory report: {e}")
            raise
    
    def _get_anomalies_for_date(self, target_date: date) -> List[Dict[str, Any]]:
        """Get anomalies for specific date"""
        anomalies = (
            self.db.query(Anomaly)
            .filter(
                Anomaly.ts >= target_date,
                Anomaly.ts < target_date + timedelta(days=1)
            )
            .order_by(Anomaly.severity.desc(), Anomaly.type, Anomaly.ts)
            .all()
        )
        
        return [
            {
                "id": a.id,
                "ts": a.ts,
                "type": a.type,
                "bin_id": a.bin_id,
                "item_id": a.item_id,
                "order_id": a.order_id,
                "severity": a.severity,
                "detail": a.detail,
                "status": a.status
            }
            for a in anomalies
        ]
    
    def _get_snapshots_for_date(self, target_date: date) -> List[Dict[str, Any]]:
        """Get snapshots for specific date"""
        snapshots = (
            self.db.query(Snapshot)
            .filter(
                Snapshot.ts >= target_date,
                Snapshot.ts < target_date + timedelta(days=1)
            )
            .order_by(Snapshot.ts.desc())
            .all()
        )
        
        return [
            {
                "id": s.id,
                "ts": s.ts,
                "bin_id": s.bin_id,
                "item_ids": s.item_ids or [],
                "conf": s.conf,
                "photo_ref": s.photo_ref
            }
            for s in snapshots
        ]
    
    def _get_orders_for_date(self, target_date: date) -> List[Dict[str, Any]]:
        """Get orders for specific date"""
        orders = (
            self.db.query(Order)
            .filter(Order.ship_date == target_date)
            .order_by(Order.order_id)
            .all()
        )
        
        return [
            {
                "id": o.id,
                "order_id": o.order_id,
                "ship_date": o.ship_date,
                "sku": o.sku,
                "qty": o.qty,
                "item_ids": o.item_ids or [],
                "status": o.status
            }
            for o in orders
        ]
    
    def _get_current_inventory(self) -> List[Dict[str, Any]]:
        """Get current inventory based on latest snapshots"""
        from sqlalchemy import func
        
        # Get latest snapshot per bin
        subquery = (
            self.db.query(
                Snapshot.bin_id,
                func.max(Snapshot.ts).label('max_ts')
            )
            .filter(Snapshot.bin_id.isnot(None))
            .group_by(Snapshot.bin_id)
            .subquery()
        )
        
        latest_snapshots = (
            self.db.query(Snapshot)
            .join(
                subquery,
                (Snapshot.bin_id == subquery.c.bin_id) & 
                (Snapshot.ts == subquery.c.max_ts)
            )
            .all()
        )
        
        return [
            {
                "bin_id": s.bin_id,
                "item_ids": s.item_ids or [],
                "last_seen": s.ts,
                "photo_ref": s.photo_ref
            }
            for s in latest_snapshots
        ]
    
    def _generate_csv_report(
        self, 
        anomalies: List[Dict[str, Any]], 
        snapshots: List[Dict[str, Any]], 
        orders: List[Dict[str, Any]], 
        target_date: date
    ) -> str:
        """Generate CSV report content"""
        try:
            # Generate anomalies CSV
            anomalies_csv = generate_anomalies_csv(anomalies)
            
            # Add summary header
            summary = f"Reconciliation Report for {target_date.strftime('%Y-%m-%d')}\n"
            summary += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            summary += f"Total Anomalies: {len(anomalies)}\n"
            summary += f"Total Snapshots: {len(snapshots)}\n"
            summary += f"Total Orders: {len(orders)}\n"
            summary += "\n"
            
            return summary + anomalies_csv
        
        except Exception as e:
            logger.error(f"Error generating CSV report: {e}")
            raise
    
    def _generate_pdf_report(
        self, 
        anomalies: List[Dict[str, Any]], 
        snapshots: List[Dict[str, Any]], 
        orders: List[Dict[str, Any]], 
        target_date: date
    ) -> bytes:
        """Generate PDF report content"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                textColor=colors.black,
                alignment=1  # Center
            )
            
            # Content
            story = []
            
            # Title
            title = Paragraph(f"Reconciliation Report - {target_date.strftime('%Y-%m-%d')}", title_style)
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Summary
            summary_data = [
                ['Metric', 'Count'],
                ['Total Anomalies', str(len(anomalies))],
                ['Total Snapshots', str(len(snapshots))],
                ['Total Orders', str(len(orders))],
                ['Report Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            ]
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Anomalies section
            if anomalies:
                story.append(Paragraph("Anomalies", styles['Heading2']))
                story.append(Spacer(1, 12))
                
                # Group anomalies by severity
                high_anomalies = [a for a in anomalies if a['severity'] == 'high']
                med_anomalies = [a for a in anomalies if a['severity'] == 'med']
                low_anomalies = [a for a in anomalies if a['severity'] == 'low']
                
                for severity, severity_anomalies in [('High', high_anomalies), ('Medium', med_anomalies), ('Low', low_anomalies)]:
                    if severity_anomalies:
                        story.append(Paragraph(f"{severity} Priority ({len(severity_anomalies)} items)", styles['Heading3']))
                        
                        anomaly_data = [['Type', 'Bin', 'Item', 'Detail']]
                        for anomaly in severity_anomalies[:10]:  # Limit to 10 per severity
                            anomaly_data.append([
                                anomaly['type'],
                                anomaly['bin_id'] or '',
                                anomaly['item_id'] or '',
                                anomaly['detail'][:50] + '...' if len(anomaly['detail']) > 50 else anomaly['detail']
                            ])
                        
                        anomaly_table = Table(anomaly_data, colWidths=[1*inch, 1*inch, 1.5*inch, 3*inch])
                        anomaly_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 8),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        
                        story.append(anomaly_table)
                        story.append(Spacer(1, 12))
            else:
                story.append(Paragraph("No anomalies found - all good!", styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            pdf_content = buffer.getvalue()
            buffer.close()
            
            return pdf_content
        
        except ImportError:
            logger.warning("ReportLab not available, generating simple text PDF")
            return self._generate_simple_text_pdf(anomalies, snapshots, orders, target_date)
        
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise
    
    def _generate_simple_text_pdf(
        self, 
        anomalies: List[Dict[str, Any]], 
        snapshots: List[Dict[str, Any]], 
        orders: List[Dict[str, Any]], 
        target_date: date
    ) -> bytes:
        """Generate simple text-based PDF when ReportLab is not available"""
        try:
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            
            # Title
            pdf.cell(0, 10, f'Reconciliation Report - {target_date.strftime("%Y-%m-%d")}', 0, 1, 'C')
            pdf.ln(10)
            
            # Summary
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Summary', 0, 1)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 8, f'Total Anomalies: {len(anomalies)}', 0, 1)
            pdf.cell(0, 8, f'Total Snapshots: {len(snapshots)}', 0, 1)
            pdf.cell(0, 8, f'Total Orders: {len(orders)}', 0, 1)
            pdf.cell(0, 8, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1)
            pdf.ln(10)
            
            # Anomalies
            if anomalies:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, 'Anomalies', 0, 1)
                pdf.set_font('Arial', '', 8)
                
                for anomaly in anomalies[:20]:  # Limit to 20 anomalies
                    pdf.cell(0, 6, f"{anomaly['type']} | {anomaly['bin_id'] or 'N/A'} | {anomaly['item_id'] or 'N/A'} | {anomaly['detail'][:60]}", 0, 1)
            
            return pdf.output(dest='S').encode('latin1')
        
        except ImportError:
            # Fallback to plain text
            logger.warning("PDF libraries not available, generating plain text")
            content = f"Reconciliation Report - {target_date.strftime('%Y-%m-%d')}\n"
            content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            content += f"Summary:\n"
            content += f"- Total Anomalies: {len(anomalies)}\n"
            content += f"- Total Snapshots: {len(snapshots)}\n"
            content += f"- Total Orders: {len(orders)}\n\n"
            
            if anomalies:
                content += "Anomalies:\n"
                for anomaly in anomalies:
                    content += f"- {anomaly['type']}: {anomaly['detail']}\n"
            
            return content.encode('utf-8')


def create_report_service(db: Session) -> ReportService:
    """Factory function to create report service"""
    return ReportService(db)