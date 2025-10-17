# AI Context - N2S Impact Model State

**Last Updated:** October 17, 2025  
**Status:** WORKING but needs final calibration tweaks

---

## Current State

**What's Working:**
- ✅ Matrix-based calculation engine (validated approach)
- ✅ Assessment questions linked to initiative maturity
- ✅ Role-based analysis (16 roles)
- ✅ Strategic bucket breakdown (Methodology, AI, OOtB)
- ✅ Recalibrated to 75th percentile of research

**What's NOT Working:**
- ⚠️ Starting at ~6.5% for Level 2 (should be ~10%)
- ⚠️ Matrix may need another 1.5x bump to hit targets

---

## The Model Architecture

### Core Files
```
app.py          - Streamlit UI, assessment questions link to initiatives
model.py        - Calculation engine with calibrated matrix
config.py       - Initiative definitions, role definitions, CMMI levels
```

### The Math Flow

```
Assessment Questions
├─ Test coverage: 30% → Automated Testing: 30%
├─ CI/CD maturity: "Basic" → Agile+DevOps: 25%
├─ Environment: "Some scripts" → Preconfigured Envs: 25%
└─ etc.
    ↓
Maturity Levels (8 initiatives × 0-100%)
    ↓
Matrix Calculation (8 initiatives × 7 phases)
    ↓
Baseline Hours - Matrix Deltas = Modeled Hours
    ↓
Actual Savings % = (Baseline - Modeled) / Baseline
```

### The Calibrated Matrix

**Structure:** 8 initiatives × 7 phases = 56 values

**Example row (Automated Testing):**
```
Discover: -15, Plan: -22, Design: -82, Build: -270, 
Test: -345, Deploy: -67, Post Go-Live: -112
```

**Interpretation:** At 100% maturity on 17,054 hr project:
- Saves 345 hours in Test phase
- Saves 270 hours in Build phase
- etc.

**Current Calibration:** 1.5x the original validated matrix
- Original: 50% maturity → 8.7%
- Current: 50% maturity → ~13%
- Target: 50% maturity → ~10% (Level 2 typical)

**Adjustment needed:** Reduce by ~0.77x to hit 10% at 50%

---

## The 25% Target Question

**Client needs:** Ability to set 25% target and see path to achieve it

**Current state:**
- Matrix shows ~26-28% at 100% maturity ✅ Target achievable
- But starts too high at defaults (6.5% vs expected 10%)
- Need to recalibrate so defaults match CMMI levels

**Solution:** Fine-tune matrix multiplier

---

## CMMI Level Definitions (from config.py)

```
Level 1: 6.5% typical (range 5-8%)
  - 0-20% test automation
  - Manual deployments
  - 0-10% code reuse

Level 2: 10% typical (range 8-12%) ← DEFAULT LEVEL
  - 20-40% test automation
  - Basic build automation
  - 10-25% code reuse

Level 3: 15% typical (range 12-18%)
  - 40-65% test automation
  - Automated testing in pipeline
  - 25-40% code reuse

Level 4: 21.5% typical (range 18-25%)
  - 65-85% test automation
  - Full deployment automation
  - 40-60% code reuse

Level 5: 27.5% typical (range 25-30%)
  - 85%+ test automation
  - Self-healing pipelines
  - 60%+ code reuse
```

**Assessment default values map to Level 2:**
- Test: 30% (within 20-40% range)
- CI/CD: "Basic build automation" (Level 2)
- Code reuse: 20% (within 10-25% range)
- This SHOULD give ~10%, but showing 6.5%

**Diagnosis:** Matrix under-calibrated by ~1.5x

---

## Next Steps (Priority Order)

### 1. **Fix Matrix Calibration** (CRITICAL)
- Multiply current matrix by 1.3x
- Validate: Level 2 defaults → 10% ✅
- Validate: 50% all initiatives → 13% ✅
- Validate: 100% all initiatives → 27-28% ✅

### 2. **Test Reactivity** (CRITICAL)
- Verify assessment dropdowns update savings
- Verify fine-tune sliders work
- If broken: Add st.rerun() triggers

### 3. **Validate Role Breakdown** (HIGH)
- Check Integration Engineer shows ~25-30% savings
- Check PM shows ~15-20% savings
- Check values look realistic across all 16 roles

### 4. **Validate Bucket Breakdown** (HIGH) ✅ VALIDATED
- Methodology: 40.1% of savings ✅ (EDCC 80%, CARM 65%, Agile 70%)
- OOtB Config: 33.8% of savings ✅ (Preconfigured Envs 65%, Integration Reuse 60%)
- AI & Automation: 26.1% of savings ✅ (Automated Testing 55%, AI/Automation 70%)
- **Defensible split - see STRATEGIC_BUCKET_DEFENSE.md**

### 5. **User Documentation** (MEDIUM)
- Update README with final calibration
- Ensure Assumptions.md has all research citations
- Keep STAKEHOLDER_JUSTIFICATION.md for board defense

### 6. **Git Commit** (WHEN WORKING)
- Only commit when model is validated
- Clean commit message explaining repair
- Don't commit broken state

---

## Known Issues

### Issue 1: Starting % Too Low
- **Current:** Level 2 defaults → 6.5%
- **Expected:** Level 2 → 10%
- **Fix:** Matrix needs 1.3x-1.5x bump

### Issue 2: Streamlit Cache (MAYBE FIXED)
- Removed @st.cache_data decorator
- Should be reactive now
- If not: Need to add manual rerun triggers

### Issue 3: Too Many Controls
- Cleaned up: Removed enable/weight checkboxes
- Simplified: Assessment → Initiative maturity
- Still complex: Could simplify further

---

## Research Sources (Quick Reference)

1. **Test Automation:** Perfecto, Testlio, Tricentis (30-50% phase reduction)
2. **AI/Automation:** GitHub Copilot (30% faster), McKinsey (20-40% productivity)
3. **Agile/DevOps:** DORA State of DevOps (15-25% faster), Accelerate book
4. **IaC:** Puppet State of DevOps (days → hours, 85% reduction)
5. **Component Reuse:** Gartner (30-50% dev reduction), Forrester API studies
6. **Architecture:** AWS Well-Architected (35-50% rework reduction)
7. **Governance:** PMI (20% waste reduction), Standish (35% success improvement)

**All at 75th percentile of published ranges**

---

## Key Design Decisions

### Why Matrix-Based?
- Captures initiative × phase interactions
- Preserves role complexity (16 roles × 7 phases)
- Validated approach (client confirmed 8.7% at 50%)
- Linear scaling (simple, transparent)

### Why Assessment → Initiative?
- Reduces duplicate inputs
- More intuitive: answer questions about current state
- Initiative maturity calculated automatically
- Can still override in expander

### Why 75th Percentile?
- Client needs to show 25% achievable
- 50th percentile (median) maxes at ~17%
- 75th percentile is ambitious but defensible
- Still below 95th percentile (outliers)

---

## What Client Needs

1. **Reactive UI:** Change dropdown → savings update ✅ (should work now)
2. **25% achievable:** At 90-95% maturity ✅ (matrix supports this)
3. **By role:** See different roles benefit differently ✅ (built in)
4. **By bucket:** Methodology vs AI vs OOtB ✅ (built in)
5. **Defensible:** Research citations for board ✅ (documented)

---

## Files to Keep

**User Documentation:**
- `README.md` - User guide
- `Assumptions.md` - Research documentation with citations
- `STAKEHOLDER_JUSTIFICATION.md` - Board defense (keep updated)

**Code:**
- `app.py` - Streamlit UI
- `model.py` - Calculation engine
- `config.py` - Configuration
- `requirements.txt` - Dependencies

**Data:**
- `fy25q3-ps-efficiency-model-02.xlsx` - Original Excel (reference)

**This file:**
- `AI_CONTEXT.md` - For AI to pick up where we left off

---

## Immediate Next Actions

**When you (AI) pick this up next:**

1. **Test the app** (http://localhost:8501)
   - Check: Level 2 defaults show what %?
   - Check: Does changing assessment update savings?
   
2. **If still showing 6.5% instead of 10%:**
   - Multiply matrix by additional 1.5x
   - Formula: target_multiplier = 10.0 / current_result
   
3. **If reactivity broken:**
   - Check Streamlit session state
   - May need to add st.experimental_rerun()
   
4. **When working correctly:**
   - Git commit with clear message
   - Update version in config.py

---

## Final Validation Checklist

- [ ] Level 2 defaults → ~10% savings
- [ ] 50% all initiatives → ~13% savings  
- [ ] 100% all initiatives → ~26-28% savings
- [ ] Change assessment → savings updates immediately
- [ ] Role breakdown shows realistic differentiation
- [ ] Bucket breakdown sums to 100%
- [ ] All research citations documented
- [ ] Ready for board presentation

---

**Status:** 90% complete, needs final calibration tweak

**Blocked on:** Verifying current starting % with client

