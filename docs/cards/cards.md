# Instagram Cards Documentation

This folder contains HTML cards designed for Instagram carousel format (1080x1350 pixels) showcasing wine statistics from the Grape Geek dataset.

## Card Specifications

### Format Requirements

- **Size**: 1080x1350 pixels (Instagram carousel format)
- **Purpose**: Screenshot for social media sharing
- **Content must fit vertically** within the height constraint
- **Mobile-friendly** design with large, readable fonts

### Design Guidelines

- Clean, modern aesthetic with gradients and shadows
- Animated slide-in effects for visual appeal
- Consistent typography using Segoe UI font family
- Color-coded regions with meaningful visual hierarchy
- Medal/emoji system for rankings

## Available Cards

### 1. Hybrid Wine Percentage Leaders (`non-vinifera-champions.html`)

**Focus**: Regions by percentage of hybrid wines

**Content Structure**:

- **Title**: "Hybrid Wine Percentage Leaders"
- **Subtitle**: "Cold-Climate Non-Vinifera Champions"
- **Intro**: "Regions by percentage of wines made with hybrid grape varieties - the cold-hardy heroes of northern wine country."

**Data Format**:

- Region name
- Producer count • Wine count format
- Percentage of hybrid wines (large, prominent display)
- Top 5 regions ranked by non-vinifera percentage

**Color Scheme**: Purple gradient header, red/orange/yellow region accents

### 2. Hybrid Wine Volume Leaders (`wine-count-champions.html`)

**Focus**: Regions by absolute count of hybrid wines

**Content Structure**:

- **Title**: "Hybrid Wine Volume Leaders"
- **Subtitle**: "Most Non-Vinifera Wines by Count"
- **Intro**: "Regions ranked by hybrid wine count - showcasing the scale of cold-climate wine production."

**Data Format**:

- Region name
- "x% of y total wines" format
- Calculated hybrid wine count (wines × percentage)
- Top 5 regions ranked by absolute hybrid wine count

**Color Scheme**: Green gradient header, green/blue/purple region accents

### 3. Grape Variety Innovators (`experimentation-masters.html`)

**Focus**: Regions by unique non-vinifera varieties used

**Content Structure**:

- **Title**: "Grape Variety Innovators"
- **Subtitle**: "Most Hybrid Wine Varieties Used"
- **Intro**: "Regions ranked by unique non-vinifera varieties - the pioneers pushing boundaries with cold-climate grape experimentation."

**Data Format**:

- Region name
- Producer count • Wine count format
- Count of unique non-vinifera varieties used
- Top 5 regions ranked by absolute non-vinifera variety count

**Color Scheme**: Red/brown gradient header, red/orange/yellow region accents

## Design Requirements

### Sizing Specifications

1. **Header optimization**: Title (42px), subtitle (24px), padding (50px), emoji (80px)
2. **Content spacing**: Content padding (40px), intro margin (35px), region gap (25px)
3. **Region cards**: Padding (40px), border radius (28px), border width (8px)
4. **Typography**: Region names (34px), details (22px), main metrics (44px), medals (36px)
5. **Footer**: Padding (45px) and font size (20px)

### Content Requirements

- **Text flow**: Avoid starting sentences with "%" symbol
- **Calculation method**: Hybrid wine counts = (total wines × hybrid percentage)
- **Data transparency**: Show calculation components clearly
- **Source attribution**: Include www.GrapeGeek.com reference

## Data Source

All statistics sourced from `docs/cards/regions_data.json` which contains:

### Available Data Fields

- `by_non_vinifera_percentage_in_wines`: Percentage of grape variety appearances in wines that are non-vinifera
- `by_hybrid_wine_count`: Calculated hybrid wine count (total wines × non-vinifera percentage)  
- `by_non_vinifera_varieties_used`: Absolute count of unique non-vinifera varieties used
- `by_total_wines`: Total wine count per region
- `by_total_producers`: Total producer count per region

### Card Data Mapping

1. **Hybrid Wine Percentage Leaders**: Uses `by_non_vinifera_percentage_in_wines`
2. **Hybrid Wine Volume Leaders**: Uses `by_hybrid_wine_count` 
3. **Grape Variety Innovators**: Uses `by_non_vinifera_varieties_used`

All data is pre-sorted in descending order (highest values first).

## Usage Instructions

1. Open HTML files in browser
2. Set browser to 1080x1350 viewport or take full-screen screenshot
3. Crop to exact Instagram carousel dimensions if needed
4. Post as carousel content on social media platforms