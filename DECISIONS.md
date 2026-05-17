# Analysis Decisions & Findings

## data_loader.py

### Dtype Optimization
- Checked actual max values before assigning dtypes using `head` and `python3 -c`
- `aisle_id` max is 134 — exceeds int8 limit of 127, used int16
- `days_since_prior_order` has NaN for first orders — must use float32, integers can't hold NaN
- Result: prior orders file loads in ~309MB vs ~1GB+ with default dtypes

## analysis.py

### Cohort Retention
- Discovered `days_since_prior_order` is capped at 30 in this dataset
- 369K orders show exactly 30 days — means 30+ days, not exactly 30
- D30 retention was showing 100% — meaningless because of the cap
- Dataset also excludes one-time buyers — overall return rate was 100%
- Decision: exclude capped values (== 30), use D7/D14/D28 windows only
- Median dropped from 13 to 9 days after excluding capped values — confirms cap was inflating the metric
- Final metrics: reorder within 7/14/28 days, median days between orders

## Reorder Rate by Department
- Merged prior orders with products and departments to get department-level reorder rates
- Dairy eggs highest at 67% — perishable staples drive repeat purchase
- Personal care lowest at 32% — likely channel switching, not brand switching
  Users use Instacart for groceries, other platforms (Amazon, Target) for personal care
- Finding: reorder rate reflects how grocery-native the category is
