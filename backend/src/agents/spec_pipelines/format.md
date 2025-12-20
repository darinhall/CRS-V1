### Separate Files per Product Type


camera_spec_pipeline/
│
├── core/                          # Shared infrastructure
│   ├── __init__.py
│   ├── base_agents.py            # Abstract base classes
│   ├── orchestrator.py           # Generic orchestrator
│   ├── validators.py             # Shared validation utilities
│   └── utils.py                  # Common helpers
│
├── products/                      # Product-specific implementations
│   ├── __init__.py
│   ├── cameras/
│   │   ├── __init__.py
│   │   ├── agents.py             # Camera-specific agents
│   │   ├── validators.py         # Drive mode, shutter, etc.
│   │   ├── schema.json           # Camera schema
│   │   └── terminology.json      # Camera terminology mappings
│   │
│   ├── lenses/
│   │   ├── __init__.py
│   │   ├── agents.py             # Lens-specific agents
│   │   ├── validators.py         # Aperture, focal length, etc.
│   │   ├── schema.json
│   │   └── terminology.json
│   │
│   ├── tripods/
│   │   ├── __init__.py
│   │   ├── agents.py
│   │   ├── validators.py         # Load capacity, height, etc.
│   │   ├── schema.json
│   │   └── terminology.json
│   │
│   └── cinema/
│       ├── __init__.py
│       ├── agents.py
│       ├── validators.py
│       ├── schema.json
│       └── terminology.json
│
├── config/
│   └── product_registry.json     # Maps product types to implementations
│
├── main.py                        # Entry point
└── requirements.txt

one for each product category (examples, to be filled out completely later): support & grip, storage & media, action cameras, cinema lenses, lens filters, monitors & recorders, mirrorless cameras, dslr cameras, film cameras, teleconverters, power & batteries, bags & cases, accessories, dslr lenses, 360 cameras, camcorders, mirrorless lenses, drones & aerial, rangefinder lenses, lens adapters, lenses, compact cameras, lighting, cinema cameras, audio, medium format cameras, etc. 