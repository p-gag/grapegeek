================================================================================
🔍 DRY RUN DEBUG INFORMATION
================================================================================

📋 CONTEXT INFORMATION:
----------------------------------------
• USE_CASE: Region Variety Research
• REGION_NAME: quebec
• REGION_CONTEXT:
  - name: Québec
  - country: Canada
  - summary: Québec is a key player in cold-hardy viticulture. Wineries here extensively use hybrids due to harsh winters and short seasons. Local breeding programs also test and develop regionally adapted selections.
  - known_varieties: Frontenac, Marquette, Vandal-Cliche, Sainte-Croix, Vidal
  - breeding_notes: Some selections from Elmer Swenson and the University of Minnesota have been widely adopted; local breeders like Mario Cliche also contribute.
  - trade_association: Vins du Québec
  - trade_association_url: https://vinsduquebec.com/
• PROMPTS_LOADED:
  - system_prompt: ✗ Missing
  - research_prompt: ✓ Loaded
  - region_context_file: regions/quebec.md
• CONTEXT_ELEMENTS:
  - has_summary: ✓
  - has_known_varieties: ✓
  - has_trade_association: ✓

🔧 API CONFIGURATION:
----------------------------------------
• Model: gpt-5
• Tools: [web_search]
• Mode: Responses API

📝 PROMPT STRUCTURE:
----------------------------------------
• Total sections: 9
• Total characters: 1,094
• Estimated tokens: ~273
  1. 
  2. **CRITICAL INSTRUCTIONS:**
  3. Research cold-climate grape varieties in the specified regio...
  4. Use ONLY information found through web search - never invent...
  5. **OUTPUT FORMAT:**
  ... and 4 more sections

📄 FULL PROMPT CONTENT:
================================================================================


**CRITICAL INSTRUCTIONS:**

Research cold-climate grape varieties in the specified region by:
  - Systematically analyzing wineries and their product offerings
  - Looking at regional associations and variety usage
  - Checking nurseries and grape availability for winemaking

Use ONLY information found through web search - never invent wineries or varieties.

**OUTPUT FORMAT:**

Return a simple JSON array of grape variety names, sorted by popularity/frequency of use:

```json
[
  "Frontenac",
  "Marquette", 
  "La Crescent",
  "Itasca",
  "Other Variety Name"
]
```

Include only actual grape variety names found through research. Sort by evidence of usage (most commonly found first).

REGION TO RESEARCH: Québec
Region Summary: Québec is a key player in cold-hardy viticulture. Wineries here extensively use hybrids due to harsh winters and short seasons. Local breeding programs also test and develop regionally adapted selections.
Known Varieties (for reference): Frontenac, Marquette, Vandal-Cliche, Sainte-Croix, Vidal
Trade Association: Vins du Québec - https://vinsduquebec.com/
================================================================================
🔍 END DRY RUN DEBUG
================================================================================