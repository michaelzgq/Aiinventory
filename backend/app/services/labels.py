from typing import List, Optional, Dict, Any
import io
import logging
from datetime import datetime
from ..utils.storage import storage_manager

logger = logging.getLogger(__name__)


class LabelService:
    def __init__(self):
        self.page_width = 8.5 * 72  # 8.5 inches in points
        self.page_height = 11 * 72  # 11 inches in points
        self.labels_per_row = 2
        self.labels_per_col = 5
        self.labels_per_page = self.labels_per_row * self.labels_per_col
    
    def generate_labels_pdf(
        self, 
        item_ids: Optional[List[str]] = None, 
        count: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate QR code labels PDF"""
        try:
            # Determine what labels to generate
            if item_ids:
                labels_data = [{"item_id": item_id, "type": "item"} for item_id in item_ids]
            elif count:
                # Generate sequential item IDs
                timestamp = datetime.now().strftime("%Y%m%d%H%M")
                labels_data = [
                    {"item_id": f"PALT-{timestamp}-{i+1:03d}", "type": "generated"} 
                    for i in range(count)
                ]
            else:
                raise ValueError("Either item_ids or count must be specified")
            
            # Generate PDF
            pdf_content = self._create_pdf_labels(labels_data)
            
            # Save to storage
            filename = f"labels_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_ref = storage_manager.save_report(pdf_content, filename, "application/pdf")
            
            return {
                "pdf_url": storage_manager.get_file_url(pdf_ref),
                "pdf_ref": pdf_ref,
                "label_count": len(labels_data),
                "filename": filename
            }
        
        except Exception as e:
            logger.error(f"Error generating labels: {e}")
            raise
    
    def _create_pdf_labels(self, labels_data: List[Dict[str, str]]) -> bytes:
        """Create PDF with QR code labels"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.graphics.shapes import Drawing
            from reportlab.graphics.barcode.qr import QrCodeWidget
            from reportlab.graphics.barcode import getCodes
            from reportlab.platypus import Paragraph
            from reportlab.lib.styles import getSampleStyleSheet
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=letter, 
                rightMargin=36, 
                leftMargin=36, 
                topMargin=36, 
                bottomMargin=36
            )
            
            # Calculate label dimensions
            available_width = letter[0] - 72  # Page width minus margins
            available_height = letter[1] - 72  # Page height minus margins
            
            label_width = available_width / self.labels_per_row
            label_height = available_height / self.labels_per_col
            
            # Create pages
            story = []
            styles = getSampleStyleSheet()
            
            for page_start in range(0, len(labels_data), self.labels_per_page):
                page_labels = labels_data[page_start:page_start + self.labels_per_page]
                
                # Create table data for this page
                table_data = []
                for row in range(self.labels_per_col):
                    row_data = []
                    for col in range(self.labels_per_row):
                        label_index = row * self.labels_per_row + col
                        if label_index < len(page_labels):
                            label_data = page_labels[label_index]
                            cell_content = self._create_label_cell(label_data, label_width, label_height)
                            row_data.append(cell_content)
                        else:
                            row_data.append("")  # Empty cell
                    table_data.append(row_data)
                
                # Create table
                table = Table(table_data, colWidths=[label_width] * self.labels_per_row, 
                             rowHeights=[label_height] * self.labels_per_col)
                
                table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                story.append(table)
                
                # Add page break if not the last page
                if page_start + self.labels_per_page < len(labels_data):
                    from reportlab.platypus import PageBreak
                    story.append(PageBreak())
            
            doc.build(story)
            
            pdf_content = buffer.getvalue()
            buffer.close()
            
            return pdf_content
        
        except ImportError:
            logger.warning("ReportLab not available, generating simple text labels")
            return self._create_simple_labels_pdf(labels_data)
        
        except Exception as e:
            logger.error(f"Error creating PDF labels: {e}")
            raise
    
    def _create_label_cell(self, label_data: Dict[str, str], width: float, height: float):
        """Create content for a single label cell"""
        try:
            from reportlab.graphics.shapes import Drawing
            from reportlab.graphics.barcode.qr import QrCodeWidget
            from reportlab.graphics import renderPDF
            from reportlab.platypus import Paragraph, Table
            from reportlab.lib.styles import getSampleStyleSheet
            
            item_id = label_data["item_id"]
            
            # Create QR code
            qr_size = min(width * 0.6, height * 0.6)
            qr_code = QrCodeWidget(item_id)
            qr_drawing = Drawing(qr_size, qr_size)
            qr_drawing.add(qr_code)
            qr_code.barWidth = qr_size
            qr_code.barHeight = qr_size
            
            # Create text
            styles = getSampleStyleSheet()
            text_style = styles['Normal']
            text_style.fontSize = 8
            text_style.alignment = 1  # Center
            
            text = Paragraph(f"<b>{item_id}</b><br/>{datetime.now().strftime('%Y-%m-%d')}", text_style)
            
            # Combine QR code and text in a mini table
            cell_table = Table([[qr_drawing], [text]], colWidths=[qr_size], rowHeights=[qr_size, 20])
            
            return cell_table
        
        except Exception as e:
            logger.error(f"Error creating label cell: {e}")
            # Fallback to text only
            return label_data["item_id"]
    
    def _create_simple_labels_pdf(self, labels_data: List[Dict[str, str]]) -> bytes:
        """Create simple text-based labels when advanced libraries aren't available"""
        try:
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 12)
            
            # Title
            pdf.cell(0, 10, 'Item Labels', 0, 1, 'C')
            pdf.ln(5)
            
            # Labels in a simple grid
            pdf.set_font('Arial', '', 10)
            x_start = 20
            y_start = 30
            label_width = 80
            label_height = 40
            
            for i, label_data in enumerate(labels_data):
                row = i // 2
                col = i % 2
                
                x = x_start + col * (label_width + 10)
                y = y_start + row * (label_height + 10)
                
                # Check if we need a new page
                if y > 250:
                    pdf.add_page()
                    y = y_start
                    row = 0
                
                # Draw label border
                pdf.rect(x, y, label_width, label_height)
                
                # Add text
                pdf.set_xy(x + 5, y + 5)
                pdf.cell(label_width - 10, 10, label_data["item_id"], 0, 1, 'C')
                pdf.set_xy(x + 5, y + 15)
                pdf.cell(label_width - 10, 10, datetime.now().strftime('%Y-%m-%d'), 0, 1, 'C')
                
                # Add placeholder for QR code
                pdf.set_xy(x + 5, y + 25)
                pdf.cell(label_width - 10, 10, '[QR CODE]', 0, 1, 'C')
            
            return pdf.output(dest='S').encode('latin1')
        
        except ImportError:
            # Ultimate fallback to plain text
            logger.warning("PDF libraries not available, generating plain text labels")
            content = "ITEM LABELS\n"
            content += "=" * 50 + "\n\n"
            
            for label_data in labels_data:
                content += f"Item ID: {label_data['item_id']}\n"
                content += f"Date: {datetime.now().strftime('%Y-%m-%d')}\n"
                content += f"QR Code: {label_data['item_id']}\n"
                content += "-" * 30 + "\n\n"
            
            return content.encode('utf-8')
    
    def generate_bin_labels(self, bin_ids: List[str]) -> Dict[str, Any]:
        """Generate bin location labels"""
        try:
            labels_data = [{"item_id": bin_id, "type": "bin"} for bin_id in bin_ids]
            
            # Generate PDF
            pdf_content = self._create_pdf_labels(labels_data)
            
            # Save to storage
            filename = f"bin_labels_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_ref = storage_manager.save_report(pdf_content, filename, "application/pdf")
            
            return {
                "pdf_url": storage_manager.get_file_url(pdf_ref),
                "pdf_ref": pdf_ref,
                "label_count": len(labels_data),
                "filename": filename
            }
        
        except Exception as e:
            logger.error(f"Error generating bin labels: {e}")
            raise


def create_label_service() -> LabelService:
    """Factory function to create label service"""
    return LabelService()