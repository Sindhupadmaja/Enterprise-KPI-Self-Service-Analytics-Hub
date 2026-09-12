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
