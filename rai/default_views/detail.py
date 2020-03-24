from .edit import EditView

class DetailView(EditView):
    http_method_names = ['get']
    
    def get(self, request, **kwargs):
        self.edit_handler = self.edit_handler.disable()
        return super().get(request, **kwargs)

