import json
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound

from debit_service import DebitService
from exceptions import ValidationError


class App(object):

    def __init__(self):
        self.url_map = Map(
            [
                Rule("/", endpoint=""),
                Rule("/get_next_debit", endpoint="get_next_debit")
            ]
        )

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, f"on_{endpoint}")(request, **values)
        except HTTPException as e:
            return e

    def on_get_next_debit(self, request):
        body = request.get_json()
        try:
            loan = DebitService(body['loan'])
        except ValidationError as e:
            return Response(json.dumps({'message': str(e)}), 400, mimetype='application/json')
        return Response(json.dumps(loan.calculate_next_payment()), mimetype='application/json')

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def create_app():
    app = App()
    return app


if __name__ == '__main__':
    from werkzeug.serving import run_simple

    app = create_app()
    run_simple('0.0.0.0', 5000, app, use_debugger=True, use_reloader=True)
