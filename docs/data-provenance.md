# Data provenance and public boundary

## Private retained sources inspected read-only

- Team paper PDF and Word version;
- Award-certificate PDF;
- A timestamped backup containing the paper PDF and `支撑材料.rar`;
- The archive contains only `result2.xlsx` and `result3.xlsx`.

No standalone `.m`, `.mlx`, `.py`, `.ipynb`, `.csv`, SPSS syntax, or SPSS data file was found in the inspected CUMCM project tree. The paper appendix contains code fragments, but it is not a complete runnable project.

## Workbook structure

Both workbooks contain one visible sheet, eight columns, 1,753 worksheet rows including the header, and 1,752 data records. No formulas are stored in either workbook.

The positional schema retained for public derivatives is:

| Public field | Meaning | Unit |
|---|---|---|
| `mirror_id` | Heliostat identifier | integer |
| `width_m` | Mirror width | m |
| `height_m` | Mirror height | m |
| `x_m` | Mirror-center east coordinate | m |
| `y_m` | Mirror-center north coordinate | m |
| `z_m` | Mirror-center installation height | m |

Tower coordinates are stored only in the first data row of the two original leading columns. The public aggregate summary reports them separately.

## Derived-data policy

Full workbooks are not published because they are retained team outputs and explicit redistribution permission from all teammates is not documented. `scripts/prepare_public_data.py` creates:

- 96 rows selected by evenly spaced source-row indices, including first and last;
- aggregate dimension, area, radius, clearance, and spacing statistics;
- a machine-readable derivation manifest.

The selection is deterministic and does not alter numeric values. The original headers are normalized to ASCII field names for reviewability.

## Constraint audit findings

The full retained workbooks were checked locally before publication:

| Check | result2 | result3 |
|---|---:|---:|
| Data records | 1,752 | 1,752 |
| Reported tower coordinate | (17.3, 12.7) | (13.3, 17.9) |
| Total mirror area (m2) | 34,162.248 | 34,076.002 |
| Mirrors within 100 m of reported tower | 30 | 34 |
| Minimum centre spacing (m) | 0.0 | 0.0 |
| Records violating nearest spacing `< width + 5 m` | 216 | 208 |

These checks use the workbooks exactly as retained. They reveal duplicates/overlaps and apparent violations of constraints described in the paper. Possible causes include unfinished optimization output, different coordinate interpretation, or export errors; the available evidence does not establish which explanation is correct. Therefore the workbooks are historical comparison artifacts, not validated optimal layouts.

The result3 workbook reports tower `y = 17.9`, while a paper table reports `17.7`. The workbook value is preserved in the derivative; the discrepancy is not silently corrected.

## Files deliberately excluded

- complete paper PDF/DOCX and official problem attachments;
- certificate image, personal identifiers, certificate number, and QR code;
- original RAR/XLSX files;
- local absolute paths, caches, credentials, and temporary extraction files.
