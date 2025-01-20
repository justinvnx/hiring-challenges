from flask import Flask
from storage.bucket import bucket_blueprint
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Initialize the Flask app
app = Flask(__name__, static_url_path="", static_folder="../static")
app.config.from_object(__name__)

# Register the Blueprint
app.register_blueprint(bucket_blueprint, url_prefix="/api")

# Add Prometheus /metrics endpoint
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})