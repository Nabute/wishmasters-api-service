from rest_framework.renderers import JSONRenderer


class CustomRendererMixin:
    def transform_data(self, data, response):
        status_code = response.status_code if response else None

        if isinstance(data, list):
            return {'status_code': status_code, 'data': {'results': data}}
        elif data and data.get('results') is None:
            return {'status_code': status_code, 'data': {'result': data}}
        else:
            return {'status_code': status_code, 'data': data}

    def handle_error(self, error_message):
        return {'error': error_message}


class Renderer(CustomRendererMixin, JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response', None)

        if response and response.status_code == 204:
            data = None
        else:
            try:
                data = self.transform_data(data, response)
            except Exception as e:
                # Handle errors gracefully
                data = self.handle_error(str(e))

        return super().render(data, accepted_media_type, renderer_context)
