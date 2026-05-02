# Full Frontend-Backend Integration Guide

## What Was Changed

Your application had static placeholder UI that wasn't displaying real analysis results from the backend. I've completely rewritten the frontend to be fully dynamic and properly integrated with your backend API.

## Key Changes

### 1. **New ResultsDisplay Component** (`components/results-display.tsx`)
   - Displays live analysis results from the backend
   - Shows overlay and heatmap images
   - Displays all 6 scoring metrics dynamically
   - Renders detected regions of interest with expandable details
   - Properly styled with animations

### 2. **Updated AnalysisSection** (`components/analysis-section.tsx`)
   - Now uses real data from backend
   - Displays ResultsDisplay component when analysis is complete
   - Shows placeholder message when no analysis has been performed
   - Automatically updates when results are available

### 3. **Enhanced DataDockingBay** (`components/data-docking-bay.tsx`)
   - Improved button styling and loading states
   - Proper error handling with visual feedback
   - Better progress indication
   - Results are now passed to shared context (no longer just local state)
   - Removed JSON raw output display

### 4. **Updated TelemetryPanel** (`components/telemetry-panel.tsx`)
   - Now shows REAL analysis metrics from backend
   - Displays SSIM score, confidence level, anomaly severity
   - Shows mean error, difference percentage, regions detected
   - Displays analysis ID, mode, and completion status
   - Conditional rendering: shows placeholder if no analysis yet

### 5. **New Context-Based State Management** (`app/page.tsx`)
   - Created `AnalysisContext` to share results across components
   - All components subscribe to the same analysis results
   - State is centralized and consistent

## Data Flow

```
User Uploads Images
        ↓
DataDockingBay sends to Backend API
        ↓
Backend returns: {
    analysis_id: "...",
    mode: "rgb" | "hybrid",
    scores: { ... },
    regions_detected: number,
    output: {
        overlay_image: "/outputs/...",
        heatmap_image: "/outputs/...",
        regions: ["/outputs/..."]
    }
}
        ↓
setAnalysisResult() updates context
        ↓
ALL components (AnalysisSection, TelemetryPanel) automatically re-render with real data
```

## Setup Instructions

### 1. Configure Backend Connection

Create or update `.env.local` in the frontend directory:

```bash
# frontend/.env.local
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

**For different environments:**
- **Local development**: `http://localhost:8000`
- **Docker/Network**: `http://backend:8000` (if using docker network)
- **Production**: `https://your-api-domain.com`

### 2. Ensure Backend is Running

```bash
cd backend/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Start Frontend (if not already running)

```bash
cd frontend
npm run dev
# or
pnpm dev
```

### 4. Test the Integration

1. Open browser to `http://localhost:3000`
2. Upload RGB Before and After images (required)
3. Optionally upload Thermal Before and After images
4. Click "Analyze Images" button
5. Watch the progress bar
6. See results appear in the Analysis section below
7. View metrics in the Telemetry section

## What You'll See Now

### When No Analysis Has Been Run:
- AnalysisSection shows: "Ready for analysis - Upload images above..."
- TelemetryPanel shows: "Telemetry data will appear here after analysis completes"

### After Analysis Completes:
- **AnalysisSection displays:**
  - ✅ Analysis ID
  - ✅ Mode (RGB or Hybrid)
  - ✅ Overlay image showing detected differences
  - ✅ Heatmap showing intensity of differences
  - ✅ All 6 metric scores (Mean Error, SSIM, Difference %, Anomaly Severity, Temporal Change, Regions Detected)
  - ✅ Expandable regions of interest with individual images

- **TelemetryPanel displays:**
  - ✅ SSIM Score (%)
  - ✅ Confidence Level (%)
  - ✅ Anomaly Severity (%)
  - ✅ Signal Integrity (%)
  - ✅ Mean Error value
  - ✅ Difference percentage
  - ✅ Number of regions found
  - ✅ Analysis mode and status
  - ✅ Analysis ID

## Backend Response Structure (Expected)

The backend is expected to return this JSON structure:

```json
{
  "analysis_id": "uuid-string",
  "mode": "rgb" | "hybrid",
  "scores": {
    "mean_error": number,
    "ssim_score": number (0-1),
    "difference_percentage": number,
    "anomaly_severity": number,
    "temporal_change": number
  },
  "regions_detected": number,
  "output": {
    "overlay_image": "/outputs/...",
    "heatmap_image": "/outputs/...",
    "regions": ["/outputs/...", ...]
  }
}
```

## Features Included

✅ Full dynamic integration  
✅ Real-time image display (overlay + heatmap)  
✅ Multiple scoring metrics  
✅ Region of interest explorer  
✅ Error handling & user feedback  
✅ Progress tracking  
✅ Loading animations  
✅ Responsive design  
✅ No more static placeholder data  
✅ Context-based state management  

## Common Issues & Solutions

### Issue: "Backend error: 404"
**Solution**: Check that your backend is running on the correct port and NEXT_PUBLIC_API_BASE is configured correctly in .env.local

### Issue: "Network error"
**Solution**: 
- Make sure backend CORS is enabled (it is in app/main.py)
- Check that the backend is accessible from your frontend
- For Docker: Use `http://backend:8000` if on same network

### Issue: Images not loading (overlay/heatmap blank)
**Solution**: 
- Verify backend is serving the `/outputs` static folder
- Check that image paths are correct in the response
- Ensure output directory exists: `backend/backend/outputs/`

### Issue: Metrics showing 0 or NaN
**Solution**: 
- Backend scoring service might need adjustment
- Check backend logs for scoring calculation errors
- Ensure thermal images are provided if expecting hybrid mode

## File Changes Summary

| File | Changes |
|------|---------|
| `app/page.tsx` | Added AnalysisContext provider |
| `components/analysis-section.tsx` | Complete rewrite - now uses real data |
| `components/data-docking-bay.tsx` | Enhanced UI, added context integration |
| `components/telemetry-panel.tsx` | Now shows real metrics from backend |
| `components/results-display.tsx` | NEW - Main results component |
| `lib/api.ts` | No changes needed (works as-is) |

## Next Steps (Optional Enhancements)

1. Add CSV export of results
2. Add comparison history/timeline
3. Add batch analysis mode
4. Add custom scoring weights
5. Add result caching
6. Add dark/light theme toggle (already implemented in UI)
