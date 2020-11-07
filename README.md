# rus_readability_flask

Website for determining the CEFR readability level of Russian texts

## Dependencies

This tool assumes the presence of two files:

1. `rf.joblib`
   * Serialized Random Forest sklearn model
2. `rf.features`
   * List of features used in `rf.joblib`
   * Feature names must match those in `udar`
