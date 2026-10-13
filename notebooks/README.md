# v1: the first cleaning notebook

This is where SafeTrade's data work started: one notebook that read the Google Sheet, cleaned it in pandas, and saved a file.

It is kept on purpose, to show the starting point. The pipeline in `pipeline/` and `sql/` replaced it, and fixed three mapping bugs it had (see [docs/3-testing.md](../docs/3-testing.md#bugs-the-tests-found)).

The sheet link is read from the `SAFETRADE_SHEET_URL` environment variable and is not in the code.
