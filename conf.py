# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'SAYC'
copyright = '2025, Joel Burton'
author = 'Joel Burton'
version = "1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'ls'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_book_theme'
html_static_path = ['_static']

html_title = html_short_title = "SAYC"
html_show_sphinx = False
html_show_copyright = False
html_show_sourcelink = False
nitpicky = True
keep_warnings = True

html_theme_options = {
    "use_download_button": False,
}


rst_prolog = r"""
.. role:: raw-html(raw)
   :format: html

.. role:: raw-latex(raw)
   :format: latex

.. .. |h| replace:: :raw-html:`<span class="h">&heartsuit;</span>`
.. |h| replace:: :raw-html:`<span class="h">&#9829;</span>`
.. |s| replace:: :raw-html:`<span class="s">&#9824;</span>`
.. |d| replace:: :raw-html:`<span class="d">&#9830;</span>`
.. |c| replace:: :raw-html:`<span class="c">&#9827;</span>`
.. .. |hl| replace:: :raw-latex:`$\textcolor{green}{\clubsuit}$`
.. |nbsp| unicode:: U+00A0

.. raw:: html

  <style>
    .page-content ul > li > p { margin-top: 0; margin-bottom: 0 } 
    .h { color: red } 
    .d { color: #ffbf00 } 
    .c { color: green } 
    .s { color: blue }

    .body ul { margin-top: 0; margin-bottom: 0; }
    table.docutils.table-unstriped td, table.docutils.table-unstriped th { padding: 0.1em 0.4em; border: none; }
    div.bottom-of-page { display: none }
    .section-number { color: #68a; font-size: 75%; margin-right: 0.4em; }
    .section-number::before { content: "§" }
    .prev-next-area .section-number { display: none }
  </style>
"""

