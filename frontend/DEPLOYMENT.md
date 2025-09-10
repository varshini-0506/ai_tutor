# Frontend Deployment Guide for Render

## Overview
This guide helps you deploy the React frontend to Render.

## Render Configuration

### 1. Create a new Static Site on Render
- Go to your Render dashboard
- Click "New" → "Static Site"
- Connect your GitHub repository
- Select the repository containing this frontend

### 2. Build Configuration
- **Build Command**: `npm run build`
- **Publish Directory**: `dist`
- **Environment**: `Node`

### 3. Environment Variables (if needed)
Add these environment variables in Render:
- `VITE_API_URL`: `https://ai-tutor-backend-m4rr.onrender.com` (your backend URL)

### 4. Build Settings
- **Node Version**: 18 or higher
- **Install Command**: `npm install`
- **Build Command**: `npm run build`

## Troubleshooting

### Common Issues:

1. **"vite: not found" error**
   - ✅ **Fixed**: Moved `vite` and `@vitejs/plugin-react` to `dependencies` in `package.json`

2. **Build fails with module not found**
   - Make sure all dependencies are in `dependencies` (not `devDependencies`)
   - Check that `package-lock.json` is committed

3. **CORS issues after deployment**
   - The backend CORS configuration should allow your frontend domain
   - Check that the backend URL is correctly set in all API calls

### Build Process:
1. Render installs dependencies: `npm install`
2. Render runs build: `npm run build`
3. Render serves the `dist` folder

### File Structure After Build:
```
dist/
├── index.html
├── assets/
│   ├── css/
│   ├── js/
│   └── images/
└── ...
```

## API Configuration
Make sure all API calls in the frontend point to the deployed backend URL:
- Backend URL: `https://ai-tutor-backend-m4rr.onrender.com`
- All fetch/axios calls should use this URL

## Testing the Deployment
1. After deployment, visit your Render URL
2. Test login/signup functionality
3. Test all major features (quizzes, reports, etc.)
4. Check browser console for any CORS errors

## Environment Variables
If you need to use environment variables in the frontend:
1. Create a `.env` file locally with `VITE_` prefix
2. Add the same variables in Render dashboard
3. Access them in code with `import.meta.env.VITE_VARIABLE_NAME`

Example:
```env
VITE_API_URL=https://ai-tutor-backend-m4rr.onrender.com
```

## Notes
- The frontend is a Single Page Application (SPA)
- All routing is handled client-side
- Static files are served from the `dist` directory
- No server-side rendering is required
