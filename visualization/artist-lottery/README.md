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
