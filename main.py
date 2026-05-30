#!/usr/bin/env python3
import shutil
from pathlib import Path
import markdown
from pygments.formatters import HtmlFormatter

extensions = ['codehilite', 'meta', 'toc', 'extra']

extension_configs = {
    'toc': {
        'permalink': False,
        'toc_depth': '1-3',
        'title': "Index"
    },
    'codehilite': {
        'linenums': True,
        'guess_lang': False
    }
}

md_engine = markdown.Markdown(
    extensions=extensions,
    extension_configs=extension_configs,
    output_format='html5'
)

def get_configs(config_file):
    if not config_file.exists():
        raise FileNotFoundError(f"Critical Error: Required configuration file '{config_file.name}' is missing.")
    try:
        config_text = config_file.read_text(encoding="utf-8")
        md_engine.convert(config_text)
        meta_dict = {key: value[0] for key, value in md_engine.Meta.items()}

        required_keys = ['blog_name', 'footer_text', 'author', 'email', 'social', 'social_link']
        missing_keys = [key for key in required_keys if key not in meta_dict or not meta_dict[key].strip()]

        if missing_keys:
            raise ValueError(f"Missing required fields in {config_file.name}: {', '.join(missing_keys)}")
        
        return meta_dict
    except Exception as e:
        print(f"Internal error processing config.md: {e}")
        raise 
    finally:
        md_engine.reset()

def generate_html(boilerplate, title, root_path, text, toc, config):
    data = {
        "{{ title }}": title,
        "{{ root_path }}": root_path,
        "{{ content }}": text,
        "{{ toc }}": toc,
        "{{ layout_class }}": "no-sidebar" if (not toc or str(toc).lower() == "false") else "",
        "{{ blog_name }}": config.get("blog_name", ""),
        "{{ footer_text }}": config.get("footer_text", ""),
        "{{ author }}": config.get("author", ""),
        "{{ email }}": config.get("email", ""),
        "{{ social }}": config.get("social", "#"),
        "{{ social_link }}": config.get("social_link", "#")
    }
    
    html = boilerplate
    for placeholder, value in data.items():
        html = html.replace(placeholder, str(value))

    return html
    
def build_pages(content_dir, output_dir, boilerplate, config):
    notes_index = {}
    
    for md_file in content_dir.rglob("*.md"):
        try:
            md_text = md_file.read_text(encoding="utf-8")
            html_text = md_engine.convert(md_text)

            relative_path = md_file.relative_to(content_dir)
            depth_level = len(relative_path.parents) - 1
            root_path = "../" * depth_level if depth_level > 0 else ""

            html_text = html_text.replace('src="assets/', f'src="{root_path}assets/')
            html_text = html_text.replace('href="assets/', f'href="{root_path}assets/')
            
            html_toc = md_engine.toc
            metadata = md_engine.Meta
            
            required_fields = ['title', 'category', 'date']
            missing_fields = [f for f in required_fields if f not in metadata or not metadata[f][0].strip()]
            
            if missing_fields:
                raise ValueError(f"Note '{md_file.name}' is missing required front-matter: {', '.join(missing_fields)}")

            title = metadata["title"][0]
            category = metadata["category"][0]
            publication_date = metadata["date"][0]
            
            html_toc = metadata.get("toc", [html_toc])[0]

            if category not in notes_index:
                notes_index[category] = []

            link = str(relative_path.with_suffix(".html")).replace("\\", "/")
            notes_index[category].append({"title": title, "link": link, "date": publication_date})

            output_path = output_dir / relative_path.with_suffix('.html')
            html = generate_html(boilerplate, title, root_path, html_text, html_toc, config)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html, encoding="utf-8")
            print(f"✅ Rendered note: {link}")
            
        except Exception as e:
            print(f"❌ Build aborted! Failed to parse note '{md_file.name}': {e}")
            raise e 
        finally:
            md_engine.reset()

    return notes_index

def build_index(notes_index, boilerplate, output_dir, config):
    html_notes = "<h1>📝 Index</h1>"

    if not notes_index:
        html_notes += "<p>Nothing to see here.</p>"
    else:
        for category in sorted(notes_index.keys()):
            html_notes += f"<h2 class='category-title'>{category}</h2>"
            html_notes += "<ul class='notes-list'>"
            
            sorted_notes = sorted(notes_index[category], key=lambda x: x['date'], reverse=True)
            for note in sorted_notes:
                html_notes += "<li class='notes-item'>"
                html_notes += f"  <a href='{note['link']}' class='notes-link'>{note['title']}</a>"

                if note['date']:
                    html_notes += f"  <span class='notes-date'>{note['date']}</span>"
                html_notes += "</li>"
                
            html_notes += "</ul>"

    html = generate_html(boilerplate, "Notes", "", html_notes, "", config)
    (output_dir / "notes.html").write_text(html, encoding="utf-8")
    print("✅ Rendered index: notes.html")

def main():
    content_dir = Path("content")
    output_dir = Path("output")
    style = Path("style.css")
    template = Path("template.html")
    config_file = Path("config.md")
    assets_dir = Path("assets")

    static_pages = {
        "Home": Path("index.md"),
        "About": Path("about.md")
    }

    output_dir.mkdir(exist_ok=True)

    missing_system_files = [f for f in [style, template, config_file] if not f.exists()]
    if missing_system_files:
        print(f"❌ Initialization error: Missing system files -> {', '.join([f.name for f in missing_system_files])}")
        return
    
    missing_static_pages = [path for name, path in static_pages.items() if not path.exists()]
    if missing_static_pages:
        print(f"❌ Initialization error: Missing required core pages -> {', '.join([path.name for path in missing_static_pages])}")
        return
    
    if assets_dir.exists():
        shutil.copytree(assets_dir, output_dir / "assets", dirs_exist_ok=True)
        print("🖼️ Assets folder synchronized.")

    shutil.copy(style, output_dir / "style.css")

    try:
        formatter = HtmlFormatter(style="monokai")
        pygments_css = formatter.get_style_defs(".codehilite")

        with open(output_dir / "style.css", "a", encoding="utf-8") as f:
            f.write("\n")
            f.write(pygments_css)
        print("🎨 Pygments syntax theme injected into output/style.css")
    except Exception as e:
        print(f"⚠️ Warning: Could not generate Pygments styles: {e}")

    boilerplate = template.read_text(encoding="utf-8")
    config = get_configs(config_file)

    print("🌱 Initializing strict build system...")
    print("-" * 50)

    for title, md_path in static_pages.items():
        try:
            md_text = md_path.read_text(encoding="utf-8")
            text = md_engine.convert(md_text)
            
            text = text.replace('src="assets/', 'src="assets/')
            text = text.replace('href="assets/', 'href="assets/')
            
            html = generate_html(boilerplate, title, "", text, "", config)

            output_path = output_dir / md_path.with_suffix('.html')
            output_path.write_text(html, encoding="utf-8")
            print(f"✅ Rendered core page: {md_path.with_suffix('.html')}")
        except Exception as e:
            print(f"❌ Failed to generate core page {title}: {e}")
            raise e
        finally:
            md_engine.reset()

    notes_index = build_pages(content_dir, output_dir, boilerplate, config)
    build_index(notes_index, boilerplate, output_dir, config)

    print("-" * 50)
    print("🚀 Build successful! Every validation passed.")

if __name__ == '__main__':
    main()