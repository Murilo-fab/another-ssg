# another-ssg

A highly opinionated, minimalistic, and strict Static Site Generator (SSG) built in Python. Designed specifically for engineering logs, academic notes, and digital gardens that require native support for **LaTeX formulas**, **Mermaid.js diagrams**, and **automated syntax highlighting**.

Engineered with a **fail-fast architecture** and a built-in **reusable CI/CD workflow** to isolate your compilation engine from your content repositories.

---

## ✨ Features

* **100% Markdown-Driven:** Content, static pages, and global site configurations are managed entirely in pure Markdown.
* **Strict Validation (Fail-Fast):** Aborts compilation immediately if required metadata (`title`, `date`, `category`) or vital infrastructure files are missing.
* **Automated Code Theming:** Leverages `Pygments` to dynamically inject full syntax-highlighting styles directly into your compiled CSS during build time.
* **Technical Native:** Built-in client-side rendering for complex mathematical equations (MathJax) and vector diagrams (Mermaid.js).
* **Decoupled Architecture:** Features a centralized GitHub Action workflow, meaning your blog repositories hold only text and styles—no build scripts required.

---

## 📂 Repository Structures

### 1. The Engine Repo (`another-ssg`)

This repository contains the core logic and dependencies configuration.

```text
another-ssg/
├── .github/workflows/
│   └── compile-and-deploy.yml  # Centralized Reusable Workflow
├── another_ssg.py              # Core Python compiler logic
├── pyproject.toml              # Modern dependency locking & CLI entrypoint
└── README.md

```

### 2. Your Blog Content Repos

Your actual writing spaces require zero Python files. They simply structure data like this:

```text
your-digital-garden/
├── .github/workflows/
│   └── deploy.yml              # Small trigger workflow pointing to the engine
├── assets/
│   ├── favicon.svg             # Your logo/site icon
│   └── photo.png               # Post images
├── content/
│   ├── programming/
│   │   └── async-python.md     # Note file with front-matter
│   └── math/
│       └── calculus.md
├── about.md                    # Core static page
├── config.md                   # Global site configuration
├── index.md                    # Homepage content
├── style.css                   # Custom theme rules
└── template.html               # The layout skeleton

```

---

## 🛠️ Configuration & Content Rules

### The `config.md` File

Every blog must provide a `config.md` at the root containing exact metadata fields:

```markdown
blog_name: Your blog name
footer_text: Built by
author: Your name
email: contato@seudominio.com
social: GitHub
social_link: https://github.com/seu-usuario
---

# Global Configurations for your blog
Any text below the three dashes acts as internal documentation.

```

### Markdown Post Front-Matter

Every markdown note under `content/` must strictly include `title`, `category`, and `date`. The `toc` field is optional.

```markdown
title: Advanced Quantum Mechanics
category: Physics
date: 2026-05-29
toc: true
---
# Quantum Note Header
Your markdown text, equations like $E = mc^2$, or charts go here.

```

---

## 💻 Local Development

If you want to run the compiler locally on your machine:

1. Clone this repository and install it locally in editable mode:
```bash
pip install -e .

```


2. Navigate to your blog's content folder (where `config.md` sits) and run the generated CLI command:
```bash
another-ssg

```


3. View your static site inside the newly generated `output/` folder.

---

## 🚀 Centralized CI/CD Deployment

To deploy any of your blogs using this central engine via GitHub Actions:

### 1. Enable GitHub Actions on the Blog Repo

Go to your blog repository on GitHub -> **Settings** -> **Pages** -> Under **Build and deployment (Source)**, change it from *Deploy from a branch* to **GitHub Actions**.

### 2. Add the Trigger Workflow

Create `.github/workflows/deploy.yml` inside your blog repository with the following minimal layout:

```yaml
name: Trigger Blog Build

on:
  push:
    branches:
      - main

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  run-central-ssg:
    uses: Murilo-fab/another-ssg/.github/workflows/compile-and-deploy.yml@main

```

---

## 📄 License

This project is open-source and licensed under the **MIT License**. Feel free to use, modify, and distribute it as you see fit. Cultivate your knowledge base freely!
