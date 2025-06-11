# Cloud Run Environment Variables

When deploying to Google Cloud Run, configure these environment variables:

## Required Variables

### Database Configuration
- `MONGO_URI`: MongoDB connection string (e.g., MongoDB Atlas)
  ```
  mongodb+srv://username:password@cluster.mongodb.net/pileup_buster
  ```

### Security Configuration
- `SECRET_KEY`: Secure secret key for application security
- `ADMIN_USERNAME`: Admin username for protected routes
- `ADMIN_PASSWORD`: Admin password for protected routes

### Runtime Configuration
- `PORT`: Port number (automatically set by Cloud Run, typically 8080)

## Optional Variables

### QRZ.com Integration
- `QRZ_USERNAME`: QRZ.com username for callsign lookups
- `QRZ_PASSWORD`: QRZ.com password for callsign lookups

### Application Configuration
- `ENVIRONMENT`: Application environment (development/production)
- `DEBUG`: Enable debug mode (true/false)
- `MAX_QUEUE_SIZE`: Maximum queue size (default: 4)

## Example Deployment Command

```bash
gcloud run deploy pileup-buster \
  --image gcr.io/YOUR_PROJECT_ID/pileup-buster \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --set-env-vars "MONGO_URI=mongodb+srv://..." \
  --set-env-vars "SECRET_KEY=your-secret-key" \
  --set-env-vars "ADMIN_USERNAME=admin" \
  --set-env-vars "ADMIN_PASSWORD=your-password"
```

## Security Notes

- Never commit secrets to source control
- Use Google Secret Manager for production secrets
- Ensure MongoDB allows connections from Cloud Run
- Use strong passwords for admin authentication