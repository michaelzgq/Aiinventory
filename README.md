# Inventory AI

AI-powered warehouse inventory management system with QR code scanning, OCR bin detection, automated reconciliation, and natural language queries.

## Features

- **📷 Smart Scanning**: QR code detection with OpenCV + OCR bin identification with PaddleOCR
- **🤖 AI Reconciliation**: Automated daily inventory reconciliation with anomaly detection
- **🗣️ Natural Language**: Voice and text queries in English and Chinese
- **📊 Real-time Dashboard**: Live inventory status and system health monitoring
- **📋 Report Generation**: CSV and PDF reports with automated anomaly categorization
- **🏷️ Label Printing**: QR code label generation for items and bins
- **🔌 API Integration**: RESTful APIs for WMS integration and webhooks

## Quick Start

### Local Development

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd inventory-ai
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or .venv\Scripts\activate  # Windows
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run Application**
   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access Application**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Docker Deployment

1. **Build and Run**
   ```bash
   docker-compose up -d
   ```

2. **Check Status**
   ```bash
   docker-compose ps
   docker-compose logs inventory-ai
   ```

### Railway Deployment

1. **Connect Repository**
   - Connect your GitHub repository to Railway
   - Railway will auto-detect the Dockerfile

2. **Set Environment Variables**
   ```
   APP_ENV=production
   API_KEY=your-secret-key-here
   DB_URL=postgresql://user:pass@host:port/db  # Use Railway PostgreSQL
   TZ=America/Los_Angeles
   USE_PADDLE_OCR=true
   STAGING_BINS=S-01,S-02,S-03,S-04
   STAGING_THRESHOLD_HOURS=12
   STORAGE_BACKEND=local
   ```

3. **Deploy**
   - Railway automatically builds and deploys on git push
   - Access via the generated Railway URL

## System Architecture

### Core Components

1. **Backend Services**
   - `ingest.py`: CSV data import (orders, allocations, bins)
   - `snapshot.py`: Image processing and QR/OCR detection
   - `reconcile.py`: Daily reconciliation engine with anomaly detection
   - `nlq.py`: Natural language query processing
   - `report.py`: CSV/PDF report generation
   - `labels.py`: QR code label printing

2. **API Endpoints**
   - `/api/orders/*`: Order management
   - `/api/allocations/*`: Item allocation tracking
   - `/api/snapshots/*`: Image upload and processing
   - `/api/reconcile/*`: Reconciliation and anomaly management
   - `/api/nlq/*`: Natural language queries
   - `/api/labels/*`: Label generation

3. **Frontend Pages**
   - `/`: Dashboard with real-time stats
   - `/scan`: Camera scanning interface
   - `/upload-orders`: CSV data upload
   - `/reconcile`: Reconciliation results and reports

### Data Flow

1. **Data Input**
   - CSV uploads (orders, allocations, bins)
   - Camera scanning (QR codes + OCR)
   - WMS webhooks (optional)

2. **Processing**
   - QR code detection with OpenCV
   - Bin ID extraction with PaddleOCR
   - Image storage (local/S3)
   - Database updates

3. **Reconciliation**
   - Compare expected vs actual inventory
   - Detect anomalies (missing, misplaced, orphaned items)
   - Generate reports and alerts

4. **Output**
   - Real-time dashboard updates
   - CSV/PDF reports
   - API responses
   - Natural language answers

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_ENV` | Environment (dev/production) | `dev` |
| `API_KEY` | API authentication key | `changeme-supersecret` |
| `DB_URL` | Database connection string | `sqlite:///./inventory.db` |
| `TZ` | Timezone for date calculations | `America/Los_Angeles` |
| `USE_PADDLE_OCR` | Enable PaddleOCR for bin detection | `true` |
| `STAGING_BINS` | Comma-separated staging bin IDs | `S-01,S-02,S-03,S-04` |
| `STAGING_THRESHOLD_HOURS` | Hours before staging alerts | `12` |
| `STORAGE_BACKEND` | Storage backend (local/s3) | `local` |
| `STORAGE_LOCAL_DIR` | Local storage directory | `./storage` |

### Database Support

- **SQLite** (default): Good for development and small deployments
- **PostgreSQL**: Recommended for production
- **Future**: MySQL, SQL Server support planned

### Storage Options

- **Local Storage**: Files stored in local directory
- **S3/R2**: Cloud storage support (configure S3 credentials)

## API Usage

### Authentication

All API endpoints require authentication via `Authorization: Bearer <API_KEY>` header.

### Example API Calls

```bash
# Upload orders CSV
curl -X POST "http://localhost:8000/api/orders/upload" \
  -H "Authorization: Bearer changeme-supersecret" \
  -F "file=@orders.csv"

# Upload snapshot image
curl -X POST "http://localhost:8000/api/snapshots/upload" \
  -H "Authorization: Bearer changeme-supersecret" \
  -F "image=@photo.jpg" \
  -F "bin_id=A54"

# Run reconciliation
curl -X POST "http://localhost:8000/api/reconcile/run?date=2025-08-17" \
  -H "Authorization: Bearer changeme-supersecret"

# Natural language query
curl -X POST "http://localhost:8000/api/nlq/query" \
  -H "Authorization: Bearer changeme-supersecret" \
  -H "Content-Type: application/json" \
  -d '{"text": "What is in bin A54?"}'
```

## Sample Data

The `sample_data/` directory contains example CSV files:

- `orders.csv`: Sample orders with shipping dates and item allocations
- `allocations.csv`: Item-to-bin allocations with status
- `bins.csv`: Bin definitions with zones and coordinates

### Loading Sample Data

1. **Via Web Interface**: Use the upload page at `/upload-orders`
2. **Via API**: Upload CSV files using the API endpoints
3. **Development**: Access `/api/dev/sample-data` to create test data

## Camera Scanning

### Supported Features

- **Live QR Detection**: Real-time QR code scanning in browser
- **Multi-frame Capture**: Capture multiple frames for better accuracy
- **OCR Bin Detection**: Automatic bin ID extraction from images
- **Voice Feedback**: Audio confirmation of scan results

### Browser Compatibility

- **Chrome/Edge**: Full camera and QR support
- **Firefox**: Camera support, limited QR features
- **Safari**: Camera support with limitations
- **Mobile**: Works on iOS Safari and Android Chrome

### Scanning Best Practices

1. **Lighting**: Ensure good, even lighting
2. **Distance**: Get close to QR codes (6-12 inches)
3. **Stability**: Hold camera steady during capture
4. **Angle**: Avoid glare and extreme angles
5. **Multi-capture**: Use 3-frame capture for better accuracy

## Natural Language Queries

### Supported Query Types

1. **Bin Contents**: "A54现在有什么？", "What's in bin A54?"
2. **SKU Location**: "找 SKU-5566", "Where is SKU-5566?"
3. **Item Tracking**: "PALT-0001 在哪", "Where is PALT-0001?"
4. **Report Export**: "导出今天的差异报告", "Export today's report"
5. **Anomaly Stats**: "今天有多少异常", "How many anomalies today?"
6. **Inventory Summary**: "库存总览", "Inventory summary"

### Voice Input

- **Languages**: English and Chinese supported
- **Activation**: Click microphone button or voice command
- **Browser**: Requires Web Speech API support

## Reconciliation Engine

### Anomaly Detection Rules

1. **Missing Items**: Allocated items not seen in recent snapshots
2. **Misplaced Items**: Items in wrong bins (allocation mismatch)
3. **Orphan Items**: Items seen but not in system
4. **Stale Staging**: Items in staging areas too long
5. **Unshipped Orders**: Orders marked shipped but items still visible

### Severity Levels

- **High**: Unshipped orders, stale staging, critical misplacements
- **Medium**: Misplaced items, missing allocations
- **Low**: Minor discrepancies, orphaned items

### Report Generation

- **CSV**: Detailed anomaly data with timestamps
- **PDF**: Formatted report with summary and charts
- **Real-time**: Live dashboard updates

## Troubleshooting

### Common Issues

1. **Camera Not Working**
   - Check browser permissions
   - Ensure HTTPS (required for camera)
   - Try different browsers

2. **QR Codes Not Detected**
   - Clean QR codes and remove obstructions
   - Improve lighting conditions
   - Use multi-frame capture mode

3. **OCR Not Working**
   - Verify PaddleOCR installation
   - Check `USE_PADDLE_OCR=true` in environment
   - Ensure clear, readable bin labels

4. **Upload Failures**
   - Check file format (CSV only)
   - Verify column headers match expected format
   - Check file size limits

5. **Database Issues**
   - Check database permissions
   - Verify connection string
   - Ensure storage directory is writable

### Development Debug Mode

Set `APP_ENV=dev` to enable:
- API documentation at `/docs`
- Sample data endpoint at `/api/dev/sample-data`
- Database reset at `/api/dev/reset-db`
- Detailed error messages

### Logs and Monitoring

- Application logs: Check container logs or console output
- Health checks: Access `/health` for system status
- Detailed health: Access `/health/detailed` for comprehensive info

## Performance Optimization

### Recommendations

1. **Database**
   - Use PostgreSQL for production
   - Add indexes for large datasets
   - Regular maintenance and backups

2. **Storage**
   - Use S3/R2 for scalability
   - Implement image compression
   - Set up CDN for static files

3. **Scanning**
   - Limit image resolution for faster processing
   - Use multi-frame capture selectively
   - Optimize OCR settings

4. **Caching**
   - Enable browser caching for static assets
   - Consider Redis for session storage
   - Cache API responses where appropriate

## Security Considerations

### Production Checklist

- [ ] Change default API key
- [ ] Use HTTPS in production
- [ ] Secure database connections
- [ ] Implement proper CORS settings
- [ ] Set up firewall rules
- [ ] Enable access logging
- [ ] Regular security updates
- [ ] Backup procedures

### API Security

- Authentication required for all endpoints
- Rate limiting (implement if needed)
- Input validation and sanitization
- SQL injection protection (SQLAlchemy ORM)

## Support and Contributing

### Getting Help

- Check documentation and troubleshooting section
- Review API documentation at `/docs`
- Check system health at `/health/detailed`

### Development

1. **Code Style**: Use Black for formatting, Flake8 for linting
2. **Testing**: Run tests with `pytest`
3. **Database**: Use Alembic for migrations
4. **Documentation**: Update README for new features

### License

[Insert your license information here]

---

**Version**: 1.0.0  
**Last Updated**: August 2025  
**Requirements**: Python 3.11+, Modern web browser with camera support