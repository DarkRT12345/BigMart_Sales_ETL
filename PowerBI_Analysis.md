# Power BI Analysis: BigMart Sales

## Scope

This document summarizes insights from the three dashboard pages:

- Executive Overview
- Outlet Sales Analysis
- Product Analysis

The analysis is based on the current dashboard snapshots and uses train-sales records (`source_dataset = train`).

## Executive Overview Findings

### Headline KPIs

- Total Sales: ~18.59M
- Average Sales: ~2.18K
- Total Products: ~2K
- Total Outlets: 10

### Sales by Outlet Type

- `Supermarket Type1` is the dominant sales channel.
- `Grocery Store` contributes the least.
- Sales concentration is high in supermarket-led channels.

### Sales by Establishment Year

- Most establishment years contribute around a similar band, with a sharp drop around one year (likely due to a smaller outlet cohort in that year).
- No clear long-term upward trend; performance appears outlet-mix driven rather than purely age-driven.

### Sales Mix by Fat Content

- Low Fat products contribute the larger share (~64%).
- Regular products still represent a meaningful share (~36%).

### Sales by Product Type

- Top categories include:
  - Fruits and Vegetables
  - Snack Foods
  - Household
- Lower categories include Breakfast and Seafood.

## Outlet Sales Analysis Findings

### Sales Share by Outlet Type and Location

- `Supermarket Type1` has multi-tier distribution and broad coverage.
- `Supermarket Type2` and `Supermarket Type3` are concentrated in higher-tier locations.
- `Grocery Store` performance is weaker and more location-sensitive.

### Top Outlets by Sales

- `OUT027` leads by a clear margin.
- `OUT035`, `OUT049`, and `OUT017` form the next performance band.
- A small set of outlets drives a high share of total revenue.

### Outlet Size vs Sales (Matrix)

- Medium and Small outlets contribute strongly across major outlet types.
- `Unknown` outlet size still carries significant sales, indicating data quality opportunity.

### Outlet KPI Table

- Avg MRP is stable across top outlets (around ~140), so sales differences are likely volume/mix driven rather than pricing alone.
- Some outlet types show materially higher average sales per record.

## Product Analysis Findings

### Product Type Contribution

- Treemap confirms concentration in a few categories:
  - Fruits and Vegetables
  - Snack Foods
  - Household
  - Frozen Foods
- Long-tail categories contribute limited revenue share.

### Top Products by Sales

- A handful of product IDs consistently outperform, indicating SKU concentration.
- Top-product performance should be protected through inventory and placement priority.

### Product Type Rank Across Establishment Years

- Category ranking varies across years, but top categories remain resilient.
- The pattern suggests persistent category demand leadership.

### Sales vs Visibility by Product Type

- Higher visibility does not always produce proportionally higher sales.
- Some mid-visibility categories deliver stronger sales efficiency.

## Strategic Implications

### Channel Strategy

- Prioritize `Supermarket Type1` for growth investments, assortment expansion, and promotions.
- Use `Grocery Store` selectively for convenience-led, high-turn SKUs.

### Outlet Strategy

- Replicate practices from top outlets (especially `OUT027`) in lower-performing outlets.
- Investigate operational differences: assortment depth, stock-out rates, shelf placement, and local demand mix.

### Product Portfolio Strategy

- Protect and deepen top categories (Fruits and Vegetables, Snack Foods, Household).
- Review low-performing categories for rationalization or targeted promotions.

### Merchandising Strategy

- Since visibility alone is not sufficient, optimize for visibility quality:
  - placement location
  - in-aisle adjacency
  - promotion timing
  - outlet-specific planograms

### Data Quality / Governance

- Reduce `Unknown` outlet size records to improve segmentation reliability.
- Track data completeness metrics as part of ETL quality checks.

## Recommended Next Analyses

1. Build outlet-level contribution and Pareto (80/20) analysis.
2. Add category-by-location profitability proxy (sales, not margin, in current data).
3. Segment outlets into performance tiers for targeted interventions.
4. Add periodic refresh and trend monitoring in Power BI Service.

## Suggested KPI Extensions

- Sales share of Top 5 outlets
- Sales share of Top 5 product types
- Sales per outlet by location tier
- Category concentration index (revenue dependency risk)
