# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from pathlib import Path

# NOTE: ディレクトリが `docs/sphinx` に移動したため、
# ソースコードが配置されている `src` ディレクトリを Python の検索パスに追加します。
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "nda"
copyright = "2026, Keisuke Ishii"
author = "Keisuke Ishii"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# 使用する Sphinx 拡張機能の設定です。
extensions = [
    "sphinx.ext.autodoc",  # ソースコードの Docstring からドキュメントを自動生成します
    "sphinx.ext.napoleon",  # Google/NumPy スタイルの Docstring を解釈できるようにします
    "sphinx.ext.viewcode",  # ドキュメントの各説明から、実際のソースコードへリンクできるようにします
    "sphinx.ext.githubpages",  # GitHub Pages での公開時に必要な `.nojekyll` ファイルを自動生成します
    "myst_parser",  # Markdown 形式 (.md) のファイルを Sphinx ドキュメントとして使えるようにします
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "ja"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# ドキュメントのテーマとして、モダンでレスポンシブな 'furo' テーマを使用します。
html_theme = "furo"

# 静的ファイル (カスタムCSSや画像など) を格納するディレクトリのパスを指定します。
html_static_path = ["_static"]

# TODO: 必要に応じて、_static/custom.css などのカスタムスタイルシートを追加してデザインを微調整できます
