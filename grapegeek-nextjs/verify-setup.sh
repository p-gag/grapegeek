#!/bin/bash
# Verification script for Task #3 - Next.js Project Setup

set -e

echo "🔍 GrapeGeek Next.js Setup Verification"
echo "========================================"
echo ""

# Check we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run from grapegeek-nextjs/ directory"
    exit 1
fi

echo "✅ In correct directory"
echo ""

# Check Node.js version
echo "📦 Checking Node.js version..."
NODE_VERSION=$(node --version)
echo "   Node.js: $NODE_VERSION"
echo ""

# Check npm version
echo "📦 Checking npm version..."
NPM_VERSION=$(npm --version)
echo "   npm: $NPM_VERSION"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules not found. Running npm install..."
    npm install
else
    echo "✅ node_modules exists"
fi
echo ""

# Verify key files exist
echo "📁 Checking project structure..."
FILES=(
    "app/layout.tsx"
    "app/page.tsx"
    "app/globals.css"
    "components/Header.tsx"
    "lib/types.ts"
    "lib/utils.ts"
    "next.config.js"
    "tailwind.config.ts"
    "tsconfig.json"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (missing)"
    fi
done
echo ""

# Check TypeScript compilation
echo "🔨 Checking TypeScript compilation..."
npx tsc --noEmit
if [ $? -eq 0 ]; then
    echo "   ✅ TypeScript compilation successful"
else
    echo "   ❌ TypeScript compilation failed"
    exit 1
fi
echo ""

# Try building the project
echo "🏗️  Building Next.js project..."
npm run build
if [ $? -eq 0 ]; then
    echo "   ✅ Build successful"
else
    echo "   ❌ Build failed"
    exit 1
fi
echo ""

# Check if out directory was created
if [ -d "out" ]; then
    echo "✅ Static export created in ./out/"
    echo "   Files in out/:"
    ls -la out/ | head -10
else
    echo "❌ Static export directory not created"
    exit 1
fi
echo ""

echo "✅ All verification checks passed!"
echo ""
echo "🎉 Next.js project setup is complete and working!"
echo ""
echo "Next steps:"
echo "  1. Run 'npm run dev' to start development server"
echo "  2. Open http://localhost:3000 to view the site"
echo "  3. Proceed to Task #4 (Database Integration)"
