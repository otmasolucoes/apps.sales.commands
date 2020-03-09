from otma.apps.core.communications.api import BaseController

class SegmentController(BaseController):
    model = Segment
    extra_fields = ['value', 'label']
    extra_names = {}

    def get(self, request):
        return super().filter(request, self.model, queryset=Segment.objects.all(), extra_fields=self.extra_fields, is_response=True)