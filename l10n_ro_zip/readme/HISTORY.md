## 18.0.0.0.1

- **The postal code search now matches word by word, so the word order no longer
  matters.** The nomenclature spells streets named after people surname first
  (`Strada Balcescu Nicolae`), while users type them the natural way round
  ("Nicolae Balcescu") — and a plain substring match never bridged the two. The
  data is not even consistent with itself: 131 rows spell "Balcescu Nicolae" and
  none the reverse, while "Alexandru Ioan Cuza" appears both ways. Since these
  are largely the main streets of every city, a good part of the street data was
  unreachable in practice.
  A multi-word term is now split, and every word must match either `street_name`
  or `street_type`. Typing the street type along with the name ("Strada Mircea")
  keeps working, and a single-word term behaves exactly as before.
- Extend the regression tests for the postal code search accordingly.
