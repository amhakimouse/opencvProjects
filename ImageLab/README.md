# Set up

winget install --id Git.Git -e

winget install --id=astral-sh.uv -e



cd path\to\ImageLab

uv sync



uv run pytest -q

uv run uvicorn app.main:app --reload


ImageLab/
├── app/
│   ├── main.py        # generic API: GET /tools, POST /process/{tool}
│   ├── registry.py    # tool name → function + parameters schema
│   ├── utils.py       # decode/encode, resize, metrics (PSNR...)
│   └── tools/
│       └── __init__.py
├── static/            # frontend (modern UI comes at Step 3)
├── samples/
├── tests/
├── scripts/           # experiments, one per concept
├── .gitignore
└── pyproject.toml