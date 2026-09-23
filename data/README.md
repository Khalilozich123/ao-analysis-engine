# Sample data

**All files here are 100% synthetic.** Organism names, references and tender objects are
invented for demonstration and do **not** come from any real, private or subscription source.
The column layout mirrors a generic Moroccan public-procurement export (*appels d'offres*) so the
parser and scorer can be exercised end to end.

| File | What it is |
|---|---|
| `sample_opportunities.xlsx` | ~33 fabricated rows spanning all four interest classes (Fort intérêt → Non pertinent). |
| `bad_opportunities.xlsx` | Same data with the required **Objet** column removed — exercises the upload-rejection path. |
| `sample_opportunity.json` | A single fabricated opportunity in the normalized internal shape. |
| `langgraph.png` | Rendered diagram of the LangGraph agent graph. |

## Regenerate

The workbooks are produced deterministically (fixed seed) by the generator:

```bash
docker compose exec backend python -m app.scripts.make_sample_xlsx
```

To bring your own data, upload any `.xlsx` with at least the **Numéro d'ordre**, **Référence**
and **Objet** columns — see the *Data model* section of the top-level [README](../README.md).
