# eidosSec - Onboarding Optimization Plan

**Goal:** Reduce "Time to First Scan" to under 5 minutes
**Current Assessment:** Based on frontend code review (Dashboard, NewProject, ProjectDetails, ScanDetails)

---

## Current User Journey

```
1. Landing Page → "Get Started" → Dashboard (3 clicks)
2. Dashboard → "New Project" → 3-step wizard (2-3 min)
3. Project Created → Navigate to Project → "Start Scan" (2 clicks)
4. Wait for scan (5-10 min for Quick Scan)
5. View Results
```

**Total Clicks to First Scan:** 7-8 clicks
**Total Time (excluding scan):** ~4-5 minutes (acceptable but can improve)

---

## Identified Friction Points

### 1. Empty State on Dashboard (Low Friction - Good)
**Location:** `Dashboard.tsx:127-141`

**Current:** Shows empty state with "Create Project" CTA
**Status:** ✅ Good - Clear call-to-action

### 2. NewProject Wizard - Path Input (Medium Friction)
**Location:** `NewProject.tsx:98-105`

**Current Issue:**
- Users must know the exact absolute path
- No file browser or path picker
- Example placeholder shows Unix path but Windows users need different format

**Recommendation:**
```tsx
// Add platform-aware placeholder
const placeholder = navigator.platform.includes('Win')
  ? 'e.g. C:\\Users\\dev\\projects\\my-app'
  : 'e.g. /home/user/projects/my-app'
```

**Future Enhancement:**
- Add "Browse" button (requires Electron/Tauri for native file picker)
- For Docker deployment: Show mounted volumes as selectable options

### 3. Detection Step - Mock Data (High Priority Fix Needed)
**Location:** `NewProject.tsx:46-57`

**Current Issue:**
- Detection is mocked with setTimeout
- Always returns `['Python', 'JavaScript']` and `'FastAPI'`
- Real detection should call backend endpoint

**Recommendation:**
```tsx
// Replace mock with real API call
const detectProject = async (path: string) => {
  const response = await api.post('/projects/detect', { path })
  return response.data // { languages: [...], framework: '...' }
}
```

**Backend needed:** `POST /api/v1/projects/detect` endpoint

### 4. Post-Project Creation - No Auto-Scan Option
**Location:** `NewProject.tsx:170-203` (Step 3)

**Current:** User creates project, then must navigate to project and click "Start Scan"

**Recommendation:** Add checkbox "Start Quick Scan immediately after creation"
```tsx
<div className="flex items-center gap-2">
  <input type="checkbox" id="autoScan" checked={autoScan} onChange={...} />
  <label htmlFor="autoScan">Start Quick Scan immediately</label>
</div>
```

If checked, after project creation → auto-navigate to scan page with scan already started.

### 5. Scan Progress - No Tool List Visibility
**Location:** `ScanDetails.tsx:126-143`

**Current:** Shows progress bar and generic log messages
**Missing:** List of which tools will run and their individual status

**Recommendation:**
```tsx
// Add tool status list
<div className="grid grid-cols-2 gap-2">
  {tools.map(tool => (
    <div key={tool.name} className="flex items-center gap-2">
      {tool.status === 'completed' ? <CheckCircle /> :
       tool.status === 'running' ? <Loader2 className="animate-spin" /> :
       <Clock />}
      <span>{tool.name}</span>
    </div>
  ))}
</div>
```

### 6. Results Page - No Guidance for Empty Results
**Location:** `ScanDetails.tsx:147-217`

**Current:** Shows findings table
**Missing:** Explanation when zero findings (is that good? or did scan fail silently?)

**Recommendation:**
```tsx
{findings.length === 0 && scan.status === 'completed' && (
  <Card className="border-green-500/20 bg-green-500/5">
    <CardContent className="py-8 text-center">
      <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
      <h3 className="text-lg font-semibold">No vulnerabilities found!</h3>
      <p className="text-muted-foreground">
        Great news - Quick Scan didn't detect any issues.
        Consider running a Deep Scan for more thorough analysis.
      </p>
    </CardContent>
  </Card>
)}
```

---

## Quick Wins (< 2 hours each)

### Win 1: Platform-Aware Path Placeholder
**File:** `NewProject.tsx`
**Time:** 30 min
**Impact:** Reduces user confusion on Windows

### Win 2: Auto-Scan Checkbox
**Files:** `NewProject.tsx`, minor backend change
**Time:** 1 hour
**Impact:** Saves 2 clicks, feels more "magical"

### Win 3: Zero Findings Celebration
**File:** `ScanDetails.tsx`
**Time:** 30 min
**Impact:** Better UX, reduces anxiety

### Win 4: Add "Last Scan Score" to Dashboard Cards
**File:** `Dashboard.tsx`
**Time:** 1 hour
**Impact:** At-a-glance security status

---

## Medium Effort Improvements (2-8 hours)

### Improvement 1: Real Language/Framework Detection
**Files:** Backend `/projects/detect` endpoint, `NewProject.tsx`
**Time:** 4 hours
**Impact:** Accurate tech stack display

### Improvement 2: Tool Progress List During Scan
**Files:** Backend WebSocket message format, `ScanDetails.tsx`
**Time:** 4 hours
**Impact:** Users see exactly what's happening

### Improvement 3: Quick Actions on Dashboard
**File:** `Dashboard.tsx`
**Time:** 2 hours
**Impact:** One-click "Scan" from dashboard without visiting project page

```tsx
// Add quick scan button to project row
<Button size="sm" onClick={() => startQuickScan(project.id)}>
  <Zap className="h-3 w-3 mr-1" /> Quick Scan
</Button>
```

---

## Onboarding Tour (Future Enhancement)

Consider adding a guided tour for first-time users using a library like `react-joyride`:

**Tour Steps:**
1. "Welcome! Let's add your first project" (highlight New Project button)
2. "Enter your project path" (highlight path input)
3. "Review detected technologies" (Step 2)
4. "Click to create and scan!" (Step 3 with auto-scan)
5. "Watch the scan progress" (Progress page)
6. "Here are your results!" (Results page)

**Trigger:** Show tour if user has 0 projects and hasn't dismissed it.

---

## Metrics to Track

| Metric | Current (Est.) | Target | How to Measure |
|--------|---------------|--------|----------------|
| Time to First Scan | ~5 min | < 3 min | Analytics event timestamps |
| Project Creation → Scan Start | 2+ clicks | 1 click | Auto-scan checkbox usage |
| Wizard Abandon Rate | Unknown | < 10% | Track step completion |
| First-Week Retention | Unknown | > 40% | Weekly active users |

---

## Implementation Priority

### Phase 1 (This Week) - Quick Wins
1. ✅ Platform-aware placeholder
2. ✅ Zero findings celebration message
3. ✅ Auto-scan checkbox

### Phase 2 (Next Week) - Core Improvements
1. Real language detection endpoint
2. Tool progress visibility
3. Dashboard quick actions

### Phase 3 (Month 4 Week 3-4) - Polish
1. Onboarding tour
2. Analytics integration
3. A/B testing framework

---

*Document Version: 1.0*
*Last Updated: 2026-02-03*
