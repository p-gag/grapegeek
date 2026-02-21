# Photo Pipeline Integration Tests

## Current Test Files

**test_foto_credit_extraction.py**
- Tests credit extraction from foto2 modals for L'ACADIE BLANC and Petite Pearl
- Demonstrates expected credit formats (JKI vs external)

**test_photo_extraction.py**
- Tests HTML parsing to extract photo IDs from photoview pages
- Shows onclick handler parsing logic

**fetch_photo_credits.py**
- Simple script to fetch and display credits for specific varieties
- Useful for manual verification

**Fixtures**
- `vivc_17638_passport.html` - L'ACADIE BLANC passport page
- `vivc_17638_photoview.html` - L'ACADIE BLANC photoview page with photos

## Future Integration Tests Needed

1. **End-to-end credit extraction**
   - Test full pipeline: photoview → foto2 → credit verification
   - Mock VIVC responses using fixtures
   - Verify all 6 allowed credit formats

2. **Cache behavior**
   - Test cache hits/misses
   - Verify delays only on cache misses

3. **Error handling**
   - Timeout handling with progressive backoff
   - Missing photos
   - Malformed HTML

4. **GCS integration**
   - Mock GCS upload/download
   - Test photo existence checks
   - Verify credit updates in grape_variety_mapping.jsonl

## Implementation

Use pytest with fixtures from HTML samples. Mock external dependencies (VIVC, GCS).
