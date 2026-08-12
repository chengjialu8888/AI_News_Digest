# Artist Lottery Visual Backend

`artist-lottery` is an optional visual backend for AI News Digest. It adds a museum-grounded artist or art-movement syntax to the daily ImageGen trend visuals without turning the news report into a fixed poster template.

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

- The default catalog is limited to modern, postwar, contemporary, media, installation, design and visual-movement language with an institutional anchor from MoMA or Centre Pompidou.
- Art Basel Basel, Miami Beach, Hong Kong and Paris official exhibitor/artist pages are discovery sources, not standalone proof of historical or institutional grounding.
- A daily seed makes the draw reproducible; recent styles can be excluded; an explicit user override wins and is recorded as `override`.
- The selected style controls material, composition grammar, color relationships and visual hierarchy. It must not override the day's trend meaning.
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

Record the human review as `0=Fail`, `1=Pass`, `2=Excel`, or `N/A`. Reference: [QwenLM/Qwen-Image-Bench](https://github.com/QwenLM/Qwen-Image-Bench).
