# HealthPulse Agent – Demo User Journeys

These journeys are designed to showcase the agent's ability to fetch healthcare data from the MCP server and render charts via code interpreter. Each journey uses valid tool calls and real data fields from the server.

---

## Journey 1: Quick Ambulance Check (1 minute)

**Scenario:** A simple query to verify the agent connects to the MCP server and returns data.

### Steps

1. **Open with:**
   > "What are the current ambulance wait times across all regions?"

   **What happens:** Calls `get_ambulance_wait_times` with no parameters (defaults to all regions, weekly). Returns a table of Category 1-4 response times per region. The agent presents results as text with commentary on which regions are meeting targets.

2. **Follow up with:**
   > "Show that as a bar chart with the 7-minute Category 1 target as a red line."

   **What happens:** Code interpreter takes the data and renders a grouped bar chart with an `axhline` at 7 minutes.

---

## Journey 2: Executive Dashboard (3 minutes)

**Scenario:** A health board executive wants a quick overview of regional performance.

### Steps

1. **Open with:**
   > "Give me a regional health summary for London and create a dashboard with three charts: ambulance response trend, A&E 4-hour target trend, and bed occupancy trend over the past 8 weeks."

   **What happens:** Calls `get_regional_health_summary` with region="London". Returns `weekly_trend_data` array with 8 data points containing `ambulance_cat1`, `ae_4hr_pct`, and `bed_occupancy_pct`. Code interpreter generates a 3-panel line chart.

2. **Follow up with:**
   > "Now do the same for North West so I can compare."

   **What happens:** Same tool call for North West. Generates a second dashboard for comparison.

3. **Close with:**
   > "Put both regions on the same charts so I can see them side by side."

   **What happens:** Code interpreter combines both datasets into overlaid line charts with a legend.

---

## Journey 3: Ambulance Deep Dive (2 minutes)

**Scenario:** Demonstrating ambulance response time analysis with target benchmarks.

### Steps

1. **Open with:**
   > "Show me weekly ambulance response times for all regions as a grouped bar chart. I want to see Category 1 and Category 2 side by side, with the 7-minute and 18-minute targets shown as horizontal lines."

   **What happens:** Calls `get_ambulance_wait_times` with no region filter, period="weekly". Returns data with fields: `region`, `date`, `category1_minutes`, `category2_minutes`. Code interpreter creates grouped bars with `axhline` reference lines.

2. **Follow up with:**
   > "Which regions are consistently missing the Category 1 target? Show me just those regions as a trend line over time."

   **What happens:** Code interpreter filters data where `category1_minutes > 7` and plots a line chart for those regions.

---

## Journey 4: A&E 4-Hour Target Analysis (2 minutes)

**Scenario:** Showing how far Contoso Health regions are from the 95% A&E target.

### Steps

1. **Open with:**
   > "Get A&E waiting times for all regions over the past month and show me a line chart of 4-hour target performance. Add a horizontal line at 95% to show the national target."

   **What happens:** Calls `get_ae_waiting_times` with period="monthly". Returns `four_hour_target_pct` per region per month. Code interpreter creates multi-line chart with 95% reference.

2. **Follow up with:**
   > "Show me the gap between actual performance and the 95% target as a waterfall chart for the most recent week."

   **What happens:** Code interpreter calculates `95 - four_hour_target_pct` for each region and renders a waterfall/bar chart showing the deficit.

3. **Follow up with:**
   > "Also show me 12-hour breaches as a stacked area chart over time."

   **What happens:** Uses `twelve_hour_breaches` field from the same data to create an area chart.

---

## Journey 5: Bed Capacity Crisis Scenario (2 minutes)

**Scenario:** Identifying hospitals at risk of running out of beds.

### Steps

1. **Open with:**
   > "Show me bed occupancy for all trusts in the Midlands. Create a horizontal bar chart colour-coded: green below 85%, amber 85-92%, red above 92%."

   **What happens:** Calls `get_bed_occupancy` with region="Midlands", bed_type="all". Returns per-trust data with `occupancy_pct`. Code interpreter uses conditional colouring.

2. **Follow up with:**
   > "Now show just critical care beds across all regions. Which trusts have fewer than 5 available beds?"

   **What happens:** Calls `get_bed_occupancy` with bed_type="critical_care". Filters where `available_beds < 5`. Renders a table and alert-style chart.

---

## Journey 6: Weekly Briefing Report (3 minutes)

**Scenario:** Generating a complete briefing with multiple visualisations.

### Steps

1. **Open with:**
   > "I need a weekly health briefing for South East. Get all the data: ambulance times, A&E waits, and bed occupancy. Then create a 4-chart report: (1) ambulance response by category as a bar chart, (2) A&E 4-hour performance as a gauge/progress bar, (3) bed occupancy by trust as a horizontal bar, and (4) the 8-week trend for all three metrics."

   **What happens:** Makes 3 tool calls: `get_ambulance_wait_times`, `get_ae_waiting_times`, `get_bed_occupancy` all with region="South East", plus `get_regional_health_summary`. Code interpreter generates a multi-figure report.

2. **Follow up with:**
   > "Summarise the key findings in bullet points and flag anything that breaches Contoso Health targets."

   **What happens:** Agent analyses the data and produces a text summary with specific numbers.

---

## Data Reference (Valid Fields & Regions)

### Regions (use exactly as shown)
- London
- South East
- South West
- East of England
- Midlands
- North West
- North East & Yorkshire

### Tool: `get_ambulance_wait_times`
- **Params:** region (optional), period: "daily" | "weekly" | "monthly"
- **Returns:** `date`, `region`, `category1_minutes`, `category2_minutes`, `category3_minutes`, `category4_minutes`, `total_incidents`
- **Targets:** Cat 1 = 7 min, Cat 2 = 18 min

### Tool: `get_ae_waiting_times`
- **Params:** region (optional), period: "daily" | "weekly" | "monthly"
- **Returns:** `date`, `region`, `median_wait_minutes`, `four_hour_target_pct`, `twelve_hour_breaches`, `total_attendances`, `admissions`
- **Target:** 95% within 4 hours

### Tool: `get_bed_occupancy`
- **Params:** region (optional), bed_type: "general" | "critical_care" | "maternity" | "all"
- **Returns:** `region`, `trust`, `bed_type`, `total_beds`, `occupied_beds`, `occupancy_pct`, `available_beds`
- **Target:** Below 85% occupancy

### Tool: `get_regional_health_summary`
- **Params:** region (required)
- **Returns:** Summary object with `ambulance`, `ae`, `beds` sections plus `weekly_trend_data` array (8 weeks of `ambulance_cat1`, `ae_4hr_pct`, `bed_occupancy_pct`)

---

## Tips for Demo

1. **Start with Journey 1** – it's the most visually impressive and shows the full pipeline.
2. **Data is random** – each call generates fresh random data, so charts will always look different. This is fine for a POC.
3. **Ask for specific chart types** – the agent responds well to "bar chart", "line chart", "heatmap", "gauge", etc.
4. **Follow-up questions work** – the agent retains context from previous tool calls in the conversation.
5. **Mention targets** – asking the agent to "highlight Contoso Health targets" triggers reference lines that make charts more meaningful.
