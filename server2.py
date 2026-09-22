from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

DATA_FILE = "users.json"


def load_users():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as user_data:
        try:
            return json.load(user_data)
        except json.JSONDecodeError:
            return []


def write_users(users):
    with open(DATA_FILE, "w") as user_data:
        json.dump(users, user_data, indent=2)


class Handler(BaseHTTPRequestHandler):

    def _send(self, status, body):
        response_bytes = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def _read_json_body(self):
        content_length = self.headers.get("Content-Length")
        if not content_length:
            return None
        length = int(content_length)
        raw_data = self.rfile.read(length)
        try:
            return json.loads(raw_data)
        except json.JSONDecodeError:
            return None

    def _extract_id(self, base_path):
        if self.path.startswith(base_path):
            parts = self.path.strip("/").split("/")
            if len(parts) == 2 and parts[1].isdigit():
                return int(parts[1])
        return None

    # --- GET: Fetch all users OR a single user ---
    def do_GET(self):
        users = load_users()

        if self.path == "/users":
            self._send(200, users)
            return

        user_id = self._extract_id("/users/")
        if user_id is not None:
            user = next((u for u in users if u["id"] == user_id), None)
            if user:
                self._send(200, user)
            else:
                self._send(404, {"message": f"User with ID {user_id} not found"})
            return

        self._send(404, {"message": "Endpoint not found"})

    # --- POST: Create a new user ---
    def do_POST(self):
        if self.path == "/users" or self.path == "/create":
            body = self._read_json_body()
            if not body or "name" not in body or "email" not in body:
                self._send(
                    400,
                    {"message": "Invalid payload. 'name' and 'email' are required."},
                )
                return

            existing_users = load_users()
            new_id = (
                max([u["id"] for u in existing_users], default=0) + 1
            )

            new_user = {
                "id": new_id,
                "name": body.get("name"),
                "email": body.get("email"),
            }
            existing_users.append(new_user)
            write_users(existing_users)

            self._send(
                201,
                {
                    "message": f"User created successfully with ID: {new_id}",
                    "user": new_user,
                },
            )
        else:
            self._send(404, {"message": "Endpoint not found"})

    # --- PUT: Replace entire user ---
    def do_PUT(self):
        user_id = self._extract_id("/users/")
        if user_id is None:
            self._send(404, {"message": "Endpoint not found"})
            return

        body = self._read_json_body()
        if not body or "name" not in body or "email" not in body:
            self._send(
                400,
                {
                    "message": "PUT requires both 'name' and 'email' fields to update."
                },
            )
            return

        users = load_users()
        user = next((u for u in users if u["id"] == user_id), None)

        if not user:
            self._send(404, {"message": f"User with ID {user_id} not found"})
            return

        user["name"] = body["name"]
        user["email"] = body["email"]
        write_users(users)

        self._send(
            200, {"message": f"User {user_id} fully updated", "user": user}
        )

    # --- PATCH: Update specific fields ---
    def do_PATCH(self):
        user_id = self._extract_id("/users/")
        if user_id is None:
            self._send(404, {"message": "Endpoint not found"})
            return

        body = self._read_json_body()
        if not body:
            self._send(400, {"message": "Invalid or empty JSON body"})
            return

        users = load_users()
        user = next((u for u in users if u["id"] == user_id), None)

        if not user:
            self._send(404, {"message": f"User with ID {user_id} not found"})
            return

        if "name" in body:
            user["name"] = body["name"]
        if "email" in body:
            user["email"] = body["email"]

        write_users(users)
        self._send(
            200, {"message": f"User {user_id} partially updated", "user": user}
        )

    # --- DELETE: Remove user ---
    def do_DELETE(self):
        user_id = self._extract_id("/users/")
        if user_id is None:
            self._send(404, {"message": "Endpoint not found"})
            return

        users = load_users()
        filtered_users = [u for u in users if u["id"] != user_id]

        if len(filtered_users) == len(users):
            self._send(404, {"message": f"User with ID {user_id} not found"})
            return

        write_users(filtered_users)
        self._send(200, {"message": f"User with ID {user_id} deleted successfully"})


if __name__ == "__main__":
    print("Server running on http://localhost:8000")
    HTTPServer(("", 8000), Handler).serve_forever()