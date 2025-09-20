# Deployment Guide for Render

## Prerequisites
- Render account
- Git repository with your code

## Deployment Steps

### 1. Create a New Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" and select "Web Service"
3. Connect your Git repository
4. Configure the service:
   - **Name**: `ai-tutor-backend` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### 2. Environment Variables

Add these environment variables in Render dashboard:

```
JWT_SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url
```

### 3. Build Configuration

The service will automatically:
- Install dependencies from `requirements.txt`
- Start the Flask app with Gunicorn
- Handle HTTPS and load balancing

### 4. Alternative Requirements Files

If you encounter build issues, try these alternative requirements files:

#### For minimal deployment:
```bash
# Use requirements-minimal.txt instead
pip install -r requirements-minimal.txt
```

#### For flexible version constraints:
```bash
# Use requirements-deploy.txt instead
pip install -r requirements-deploy.txt
```

### 5. Troubleshooting

#### Build Errors
- If you get build errors, try using `requirements-minimal.txt`
- Remove problematic packages temporarily
- Check Python version compatibility

#### Runtime Errors
- Check logs in Render dashboard
- Ensure all environment variables are set
- Verify database connection

### 6. Health Check

Add a health check endpoint to your app:

```python
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200
```

### 7. CORS Configuration

Ensure CORS is properly configured for your frontend domain:

```python
CORS(app, resources={r"/*": {"origins": ["https://your-frontend-domain.com"]}})
```

## File Structure

```
backend/
├── app.py                 # Main Flask application
├── requirements.txt       # Production dependencies
├── requirements-minimal.txt # Minimal dependencies
├── requirements-deploy.txt # Flexible versions
├── pdf_generator.py      # PDF generation
├── report_db.py          # Database operations
└── DEPLOYMENT.md         # This file
```

## Notes

- The app uses SQLite by default (good for development)
- For production, consider using PostgreSQL
- OCR features are optional and will be disabled if pytesseract is not available
- Chart generation requires matplotlib and numpy 