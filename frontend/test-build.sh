#!/bin/bash

echo "🧪 Testing frontend build process..."

# Clean previous build
echo "📦 Cleaning previous build..."
rm -rf dist/

# Install dependencies
echo "📥 Installing dependencies..."
npm install

# Run build
echo "🔨 Running build..."
npm run build

# Check if build was successful
if [ -d "dist" ]; then
    echo "✅ Build successful! dist/ directory created."
    echo "📁 Contents of dist/:"
    ls -la dist/
    
    # Check if index.html exists
    if [ -f "dist/index.html" ]; then
        echo "✅ index.html found in dist/"
    else
        echo "❌ index.html not found in dist/"
        exit 1
    fi
    
    # Check if assets directory exists
    if [ -d "dist/assets" ]; then
        echo "✅ assets/ directory found in dist/"
        echo "📁 Contents of assets/:"
        ls -la dist/assets/
    else
        echo "❌ assets/ directory not found in dist/"
        exit 1
    fi
    
    echo "🎉 Build test completed successfully!"
else
    echo "❌ Build failed! dist/ directory not created."
    exit 1
fi
