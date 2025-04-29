from django import forms
from django.utils.safestring import mark_safe


class MarkdownEditorWidget(forms.Textarea):
    class Media:
        css = {
            'all': (
                'https://cdnjs.cloudflare.com/ajax/libs/easymde/2.14.0/easymde.min.css',
            )
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/easymde/2.14.0/easymde.min.js',
        )

    def render(self, name, value, attrs=None, renderer=None):
        textarea_html = super().render(name, value, attrs, renderer)
        textarea_id = attrs.get('id', f'id_{name}')
        init_js = f"""
                   <script>
                   document.addEventListener('DOMContentLoaded', function() {{
                     var el = document.getElementById("{textarea_id}");
                     if (!el || !window.EasyMDE) return;
                     new EasyMDE({{
                       element: el,
                       spellChecker: false,
                       renderingConfig: {{ singleLineBreaks: false }},
                       autoDownloadFontAwesome: false,
                       toolbar: [
                         "bold","italic","heading","|",
                         "quote","unordered-list","ordered-list","|",
                         "link","image","|",
                         "preview","side-by-side","fullscreen","|",
                         "guide"
                       ]
                     }});
                   }});
                   </script>
                   """
        return mark_safe(textarea_html + init_js)
