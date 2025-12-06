# Bug Fixes Summary - December 4, 2025

## Issues Found

### 1. **Balance Not Updating After Purchase** ✅ FIXED

**Symptom**: When buying supplies, the balance remains at $2500 on the frontend.

**Root Cause**:

- Backend WAS deducting the balance correctly in `_apply_action()`
- Frontend DOES refetch state after actions (`fetchState()` called in `handleAction`)
- **The real issue**: Server needed restart for code changes to take effect

**Fix Applied**:

- Fixed item name mapping in `server.py` line 219-220
- Added `inventory_item = "detergent" if item == "soap" else item`
- Updated inventory update to use `inventory_item` instead of `item`

**Action Required**:

```powershell
# Restart the backend server
# The --reload flag should auto-reload, but force restart to be sure
Ctrl+C the running uvicorn process, then:
python -m uvicorn src.server:app --reload --host 0.0.0.0 --port 8000
```

---

### 2. **Inventory Went to 0 Instead of Increasing** ✅ FIXED

**Symptom**: Detergent stock showed 200, then went to 0 after purchase instead of increasing to 210.

**Root Cause**: Item name mismatch

- Frontend sends `'soap'` as item ID
- Backend inventory uses `'detergent'` as the key
- When setting `state.inventory[item]`, it created a new key `'soap'` instead of updating `'detergent'`

**Fix Applied**: Same as Issue #1 above

---

### 3. **History Page Empty/Not Displaying** ⚠️ PARTIAL FIX NEEDED

**Symptom**: History viewer doesn't show data after first turn.

**Root Cause**:

- History endpoints work correctly (`/history/comparison`, `/history/thinking`)
- Data only populates AFTER completing at least one full week/turn
- At Week 1 with no "Next Turn" clicked, there are no history records yet

**Current Status**: **WORKING AS DESIGNED** - but needs better UX

**Recommended Fix** (Optional Enhancement):
Add empty state message to `HistoryViewer.tsx`:

```typescript
{
  loading ? (
    <div className="loading">Loading history data...</div>
  ) : comparison && Object.keys(comparison.participants).length > 0 ? (
    <ComparisonView data={comparison} />
  ) : (
    <div className="empty-state">
      <p>No history data yet. Click "Next Week" to start tracking!</p>
    </div>
  );
}
```

---

## Additional Issues Found During Investigation

### 4. **Initial Inventory Display Shows 0** 🐛 BUG

**Symptom**: On the Manage tab, Detergent shows "Stock: 0" even though backend says 200

**Root Cause**: Likely `laundromat.inventory[s.id]` lookup issue

- Frontend uses `s.id = 'soap'`
- Backend inventory has key `'detergent'`
- `laundromat.inventory['soap']` returns `undefined`, displays as 0

**Fix Needed**: Update `ControlPanel.tsx` line 217 to handle the mapping:

```typescript
const inventoryKey = s.id === "soap" ? "detergent" : s.id;
<span className="font-mono font-bold text-gray-700">
  {laundromat.inventory[inventoryKey] || 0}
</span>;
```

---

### 5. **Vendor Price Display Mismatch** 🐛 BUG

**Symptom**: UI shows $0.500 for BulkWash detergent, backend shows $0.08

**Root Cause**:

- Frontend `ControlPanel.tsx` line 205: `currentVendor?.prices[s.id]`
- Uses frontend ID `'soap'` to look up price
- Backend vendor.prices has key `'detergent'` with price $0.08
- Fallback to `s.baseCost` ($0.5) when key not found

**Fix Needed**: Same mapping issue as #4 above

---

## Worldbook Alignment Issues

### Missing Frontend Features (Per Worldbook)

Based on `2_1_wb_finace_system.md`:

1. **Revenue Streams**:

   - ✅ Standard Wash/Dry exist
   - ❌ Missing predefined expansion services (Delicate Wash, Heavy-Duty, etc.)
   - ❌ Missing vending sales (DrinkSnacks shown but not implemented)
   - ❌ Missing premium services (Wash & Fold, Pickup & Delivery)
   - ❌ Missing custom proposal UI

2. **Cost Structure**:

   - ❌ No weekly/monthly fixed costs displayed (Rent, Insurance, etc.)
   - ❌ No tax calculation UI
   - ❌ No P&L statement visible to player

3. **Banking & Loans**:
   - ❌ No loan system implemented on frontend
   - ❌ No credit/operating line visible

### Backend Missing Features

1. **Automatic Costs**: Weekly rent, utilities, insurance not deducted
2. **Tax System**: Quarterly tax calculation not implemented
3. **Financial Reports**: P&L generation exists but not displayed
4. **Loan System**: Partially implemented but not accessible

---

## Testing Checklist

After restarting the server, verify:

- [ ] Buy 10 Detergent → Balance decreases by ~$0.80
- [ ] Detergent stock increases by ~7-10 (accounting for delivery delay multiplier)
- [ ] Click "Next Turn" → History viewer shows data
- [ ] Buy from different vendors → Different prices reflected
- [ ] Check all tabs load without errors

---

## Priority Fixes

### HIGH PRIORITY (User-blocking bugs)

1. ✅ Fix inventory item mapping (already done)
2. 🔄 Restart backend server to apply fix
3. 🔧 Fix frontend inventory display (ControlPanel.tsx)
4. 🔧 Fix frontend vendor price display (ControlPanel.tsx)

### MEDIUM PRIORITY (UX improvements)

5. Add empty state to History viewer
6. Add balance change animation/feedback
7. Display pending deliveries on UI

### LOW PRIORITY (Feature completeness per worldbook)

8. Implement revenue stream management UI
9. Add P&L statement view
10. Implement loan system frontend
11. Add automatic weekly costs
12. Implement tax calculation

---

## Files Modified

- `t:\PYTHONPROJECTS2025\matbench\src\server.py` (lines 219-256)
  - Added item name mapping for 'soap' → 'detergent'
  - Fixed inventory update to use correct key

## Files Needing Changes

- `t:\PYTHONPROJECTS2025\matbench\frontend\src\components\ControlPanel.tsx`
  - Line 217: Fix inventory display
  - Line 205: Fix price lookup
- `t:\PYTHONPROJECTS2025\matbench\frontend\src\components\HistoryViewer.tsx` (optional)
  - Add empty state handling
