from app import create_app
from app.blueprints.registrations import approve_registration
from app.extensions import db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        # Replace with a valid registration_id from your DB
        registration_id = 1
        # Comment out @jwt_required and @require_role decorators in approve_registration before running this test
        with app.test_request_context(f"/registrations/{registration_id}/approve", method="POST"):
            response = approve_registration(registration_id)
            # If response is a tuple (response, status), get the first element
            if isinstance(response, tuple):
                response_obj = response[0]
            else:
                response_obj = response
            print(response_obj.get_json())
