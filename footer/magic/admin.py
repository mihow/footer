import json
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import FooterRequest 


class FooterRequestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_leader_start', 'is_leader_end', 'created', 'user_agent')
    readonly_fields = ('is_leader', 'data_formatted', 'created')
    filter_fields = ('is_leader', 'created')

    def data_formatted(self, instance):
        """Function to display pretty version of our data"""

        # Convert the data to sorted, indented JSON
        response = json.dumps(instance.request_data, sort_keys=True, indent=2)

        # Truncate the data. Alter as needed
        response = response[:5000]

        # Get the Pygments formatter
        formatter = HtmlFormatter(style='colorful')

        # Highlight the data
        response = highlight(response, JsonLexer(), formatter)

        # Get the stylesheet
        style = "<style>" + formatter.get_style_defs() + "</style><br>"

        # Safe the output
        return mark_safe(style + response)

    data_formatted.short_description = 'Request data'

admin.site.register(FooterRequest, FooterRequestAdmin)
