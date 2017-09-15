from django.contrib import admin

from news_scraper.models import DetectedEvent


class DetectedEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_url', 'relevant_coins', 'date', 'validated', 'is_valid')

    def event_url(self, event):
        return '<a href="%s">%s</a>' % (event.url, event.url)

    event_url.allow_tags = True


admin.site.register(DetectedEvent, DetectedEventAdmin)
