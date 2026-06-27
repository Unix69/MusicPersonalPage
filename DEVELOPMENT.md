# 🛠️ Model Extraction & Customization Guide

This operational developer document clarifies how to refactor the software design, extract core semantic components, and implement structural features.

---

## 🔄 Model Extraction & Headless Architecture Strategy

If your design objectives require transitioning from a monolith to a **Headless CMS architecture** (e.g., using a modern frontend framework like React, Next.js, or Vue), you can decouple the current SQLAlchemy data layer into an isolated backend data engine.

### 🗺️ Data Extraction Architecture Blueprint
To safely migrate the current implementation toward a decoupled architecture, follow this strategic evolutionary path:

<pre>
   [ Current System Design ]                     [ Modern Headless Paradigm ]
 
 +---------------------------+                 +---------------------------+
 | Flask-Admin / Jinja Views |                 |  Next.js / React Frontend |
 +---------------------------+                 +---------------------------+
               |                                             ^
               v (Direct SQL)                                | (Secure JSON REST API)
 +---------------------------+                 +---------------------------+
 |  SQLAlchemy ORM Database  |                 | Flask API + Marshmallow   |
 +---------------------------+                 +---------------------------+
                                                             |
                                                             v (Abstracted ORM)
                                               +---------------------------+
                                               |  SQLAlchemy Data Models   |
                                               +---------------------------+
</pre>

### 🛠️ Step-by-Step API Extraction Recipe
1. **Preserve Database Schemas**: Keep the existing structural classes inside <code>database.py</code> intact, as they provide a mature, stable schema definition for data management.
2. **Introduce Serialization Tooling**: Install high-performance serialization libraries like <code>marshmallow-sqlalchemy</code> to automate model-to-JSON transformations.
3. **Build REST API Routing Endpoints**: Replace the standard Flask-Admin views with programmatic API data streams:

<pre><code>
from flask import Blueprint, jsonify
from database import Tour

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/api/v1/tours', methods=['GET'])
def get_active_tours():
    tours_query = Tour.query.all()
    # Serialize data attributes into a structured JSON payload response
    output_payload = [
        {
            "id": tour.id,
            "title": tour.name,
            "description": tour.description
        } for tour in tours_query
    ]
    return jsonify(output_payload), 200
</code></pre>

---

## 🧑‍💻 Adding a New Administrative Feature Model

To extend the system's core capabilities (for example, introducing a digital merchandise tracking layer), follow this development pattern:

### 1. Register the Database Model Class
Append your target database design entity structure inside <code>database.py</code>:

<pre><code>
class Merchandise(db.Model):
    __tablename__ = "merchandise_product"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock_count = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)

    def __str__(self):
        return f"{self.title} (${self.price})"
</code></pre>

### 2. Craft the Administrative View Binding Structure
Create a dedicated administrator management class and register it within the application's runtime lifecycle context inside <code>app_core.py</code>:

<pre><code>
# 1. Implement secure view handling parameters
class MerchandiseAdmin(AdminView):
    column_searchable_list = ['title']
    column_filters = ['price', 'is_available']
    form_columns = ['title', 'price', 'stock_count', 'is_available']

# 2. Inject view logic inside App.init() mapping arrays
self.admin.add_view(
    MerchandiseAdmin(
        Merchandise, 
        db.session, 
        admin_authenticator=self.admin_authenticator, 
        app=self, 
        name="Store Merchandise"
    )
)
</code></pre>

---

## ⚠️ Critical Operational Guardrails

When updating or maintaining this application, adhere to the following core system design constraints:
1. **Image Engine Integrity Constraints**: Never remove the dependency configuration or import routines tied to <code>compatibility_pillow.py</code>. Doing so will break asset processing operations on servers running updated distributions of the Pillow graphics package.
2. **Context Instantiation Flow Rules**: Database operation classes, configuration loaders, and cookie routers are designed around a strict initialization order. Avoid triggering or invoking database queries before the execution of the <code>web_app.configure()</code> bootstrap sequence completes.