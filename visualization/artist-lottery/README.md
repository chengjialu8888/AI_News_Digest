# Artist Lottery Visual Backend

`artist-lottery` is an optional visual backend for AI News Digest. It adds a museum-grounded artist, art movement, workshop tradition, or cultural visual system to the daily ImageGen trend visuals without turning the news report into a fixed poster template.

## Enable

```bash
VISUAL_BACKEND=artist-lottery \
  python ralph-daily-loop/stage9.py
```

The default is `VISUAL_BACKEND=imagegen`. The other explicit backend is `VISUAL_BACKEND=mck-ppt`; it is rendered by the Mck PPT command documented in the repository root README.

Optional controls:

```bash
VISUAL_STYLE_OVERRIDE="Mark Rothko-inspired color field painting" \
RECENT_VISUAL_STYLES="Andy Warhol-inspired pop repetition and screenprint" \
VISUAL_BACKEND=artist-lottery \
  python ralph-daily-loop/stage9.py
```

## Selection Rules

- The default catalog includes both modern/contemporary practices and classical or cross-civilizational visual systems with an official museum collection anchor.
- Modern/contemporary sources include MoMA and Centre Pompidou; classical/global sources include [The Met Collection](https://www.metmuseum.org/art/collection), [British Museum Collection Online](https://www.britishmuseum.org/collection), [Louvre Collections](https://collections.louvre.fr/en/), the [National Archaeological Museum of Athens](https://www.namuseum.gr/en/collections/), [Staatliche Museen zu Berlin Collections Online](https://search.smb.museum/) including the Pergamonmuseum, the [Museo Nacional de Antropología Mexico](https://mna.inah.gob.mx/index.php/inicio/), and [Museo Nacional de Colombia Collections](https://museonacional.gov.co/colecciones/Paginas/default.aspx).
- The global classical pool is explicitly partitioned into regional groups in the renderer:
  - **Athens**: Cycladic marble minimal form; Attic black-figure and red-figure vase narrative. Anchored to the National Archaeological Museum of Athens.
  - **Berlin**: Ancient Near Eastern glazed-brick procession and modular relief; Hellenistic frieze and compressed bodily motion. Anchored to Staatliche Museen zu Berlin and the Pergamonmuseum.
  - **Mexico**: Maya glyphic narrative and calendrical rhythm; Teotihuacan mural geometry and ceremonial procession. Anchored to the Museo Nacional de Antropología Mexico.
- These regional pools are implemented in both `ralph-daily-loop/stage9.py` and `ralph-daily-loop/stage9_kleisli.py`, so the standard and Kleisli render paths draw from the same catalog contract.
- Art Basel Basel, Miami Beach, Hong Kong and Paris official exhibitor/artist pages are discovery sources, not standalone proof of historical or institutional grounding.
- Classical entries may represent named artists, anonymous workshops, material traditions, or cultural visual systems. They must retain period, region, catalog query and collection source; anonymous works must not be falsely attributed to an individual.
- A daily seed makes the draw reproducible; recent styles can be excluded; an explicit user override wins and is recorded as `override`.
- The selected style controls material, composition grammar, color relationships and visual hierarchy. It must not override the day's trend meaning.
- **Mechanism fidelity comes before surface resemblance.** Before prompting, extract the documented or institutionally interpreted working mechanism: spatial relations, material/action logic, rhythm or use of silence, and viewing condition. Translate those mechanisms into the day's trend instead of using a name, palette, dots, glyphs, slashes, brush marks, sacred symbols, or other signature surfaces as a shortcut.
- Three images must be newly composed for the three trends. Do not only swap labels, colors or text.
- Avoid identifiable faces. Keep Chinese titles and critical judgements large, legible and unobstructed.

## Contract, evaluator, and case memory

The Lottery is a small visual research loop, not a name picker:

```text
museum catalog
  -> mechanism extract
  -> trend translation
  -> prompt trace
  -> image + screenshot QA
  -> targeted return route
  -> accepted / rework / rejected case
  -> next draw memory
```

Every enabled run writes:

- `style_contract`: visual intent, mechanisms, translation rules, anti-patterns, fit signals, prompt components, evaluator subchecks and catalog references.
- `trend_translation`: the two or more mechanisms used for each trend, the structural variable they expose, and the composition job.
- `prompt_trace`: an auditable prompt skeleton. The artist name remains provenance and `artist_name_as_prompt_shortcut` must be `false`.
- `evaluation_contract`: an isolated review rubric with return stages `catalog`, `mechanism_extract`, `trend_translation`, `prompt`, and `craft`.
- `case_memory`: `case_id`, prior case count, current review state and the persistent case store.

Record a human review after inspecting the delivered screenshots:

```bash
python visualization/artist-lottery/record_case_review.py \
  --entry output/art-style-lottery-entry.json \
  --status accepted \
  --surface-fidelity 2 \
  --mechanism-fidelity 2 \
  --fidelity-verdict pass
```

For a failed review, use `--status rework_requested`, `--return-to mechanism_extract` (or another concrete stage), repeat `--finding` for observable issues, and provide `--fix`. The next Lottery reads reviewed cases from `data/art-style-cases.json` or the path supplied by `STYLE_CASES_PATH`; `data/art-style-cases.example.json` is the schema reference.

The mechanism lexicon is organized around space, material, rhythm, viewing condition, information hierarchy, and anti-patterns. This is the guardrail against AI-slop style transfer: visual resemblance is a result, while the working relation and the reason it clarifies today's trend are the input.

## Outputs

When enabled, Goal 9 writes:

- `output/daily-trends.json` with `visual_backend`, `style_lottery`, institutional source registries and trend-specific visual specs.
- `output/art-style-lottery-entry.json` with one-table-per-day layout metadata and the QA framework.
- `reports/YYYY-MM-DD-ai-daily/trends-imagegen/trend-1.png` through `trend-3.png` after ImageGen generation.
- A daily append to the configured Feishu document `AI日报｜艺术风格 Lottery`, containing one complete two-column table. Each trend row keeps its explanation and screenshot together.

## QA

Use Qwen-Image-Bench as the reference taxonomy, not as a claim that the pipeline ran Q-Judger:

- **Quality**: realism, detail, resolution
- **Aesthetics**: composition, color harmony, lighting, style control
- **Alignment**: attributes, layout, relations, scene
- **Real-world Fidelity**: safety/compliance, world knowledge, information visualization, cultural elements
- **Creative Generation**: imagination, logical resolution, text rendering, design applications, visual storytelling

Add a separate style-fidelity review:

- **Surface fidelity**: do the material, color, composition, texture and hierarchy execute the selected visual language?
- **Mechanism fidelity**: can a reviewer identify at least two preserved working mechanisms and explain how each clarifies today's trend?
- **Verdict**: fail when the image is recognizable only because of decorative signatures, or when the mechanism cannot be explained without saying “it looks like the artist”. Rewrite the mechanism translation or re-lottery before delivery.

Record the human review as `0=Fail`, `1=Pass`, `2=Excel`, or `N/A`, together with `surface_fidelity`, `mechanism_fidelity`, `fidelity_verdict`, and any rework reason. Reference: [QwenLM/Qwen-Image-Bench](https://github.com/QwenLM/Qwen-Image-Bench).
