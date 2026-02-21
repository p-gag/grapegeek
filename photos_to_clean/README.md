# Photo Pipeline - To Review/Clean

Files moved here during photo credit extraction implementation. Review and organize as needed.

## Production Documentation & Tools

**docs/**
- `PHOTO_CREDITS_NOTES.md` - Complete technical reference
  - How foto2 modal discovery worked
  - All 6 credit formats (5 JKI + Tom Plocher)
  - Code changes and pitfalls
  - Referenced from CLAUDE.md

**Production Tool:**
- `analyze_photo_credit_distribution.py` - Analyze credit distribution across varieties
  - Run to see breakdown of JKI vs external credits
  - Uses cache for fast execution

## Test Files & Fixtures (For Future Integration Tests)

See `INTEGRATION_TEST_PLAN.md` for proper test implementation plan.

**Test Scripts:**
- `test_foto_credit_extraction.py` - Tests credit extraction from foto2 modals
- `test_photo_extraction.py` - Tests photo ID parsing from photoview pages
- `fetch_photo_credits.py` - Manual verification script

**HTML Fixtures:**
- `fixtures/vivc_17638_passport.html` - L'ACADIE BLANC passport page
- `fixtures/vivc_17638_photoview.html` - L'ACADIE BLANC photoview page

## Old/Superseded Scripts

These were replaced by `src/08a_photo_sync_gcs.py`:
- `add_photo_to_variety.py` - Old photo adding script
- `vivc_photo_downloader.py` - Old downloader
- `vivc_photo_manager.py` - Old manager
- `analyze_photo_credits.py` - Analyzed breeders (not photo credits)
- `fix_photo_data.py` - One-time fix script

## Temporary Docs

- `PHOTO_PIPELINE_USAGE.md` - Redundant with docs/PHOTO_CREDITS_NOTES.md
- `PHOTO_SYNC_COMPLETE.md` - Temp completion notes

---

**Action:** Review, extract anything useful, then archive or delete.
