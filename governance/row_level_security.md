# Row-Level Security design

Example role: RegionalManager

Filter concept:
`FactKPI[Region] = USERPRINCIPALNAME()` is only valid when Region stores user identifiers.

For a scalable model, use a security mapping table:

UserRegion
- UserEmail
- Region

Relationship:
UserRegion[Region] → FactKPI[Region]

Role filter:
`UserRegion[UserEmail] = USERPRINCIPALNAME()`

Test with at least two sample users and verify that each sees only authorized regions.

## Implementation in this repo

`data/user_region.csv` is the mapping table and `sql/04_row_level_security.sql` applies it: a regional manager sees only their region, the CFO sees all four, and an unmapped user sees nothing. `tests/test_pipeline.py` verifies all three cases. The same mapping table drives the Power BI role filter above.
