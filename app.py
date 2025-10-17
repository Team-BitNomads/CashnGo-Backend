from flask import Flask, jsonify
from config import Config
from services.database_service import init_db, mongo
from routes.auth_routes import auth_bp
from routes.gig_routes import gig_bp
from routes.payment_routes import payment_bp
import logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    app.logger.setLevel(logging.INFO)
    print("Loaded MONGO_URI:", app.config.get("MONGO_URI"))

    init_db(app)

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(gig_bp, url_prefix='/api/gigs')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')

    # Welcome Endpoint, Made by me to be used to create a cron-job to avoid system spinnig down with downtime
    @app.route('/')
    def index():
        return jsonify({"message": "Welcome to CashnGo Backend API!"})

    # Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"message": "Resource not found.", "status_code": 404}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"message": "Method not allowed for this resource.", "status_code": 405}), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f"Internal Server Error: {error}")
        return jsonify({"message": "An unexpected error occurred.", "status_code": 500}), 500

    app.config['MOCK_VERIFICATION'] = True 


    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        pass

    app.run(debug=True)