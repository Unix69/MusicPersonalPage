# 🎵 Musician Personal Web Engine & Administration Hub

An enterprise-grade, lightweight content management system (CMS) and portfolio engine designed specifically for solo musicians, bands, and record labels. Built on top of the Flask microframework and powered by Flask-Admin, this architecture isolates the public presentation layer from a secure, relational administration dashboard.

---

## 🗺️ Documentation Index
To ensure high maintainability and straightforward customization, the system documentation is modularized into specialized sections:
* **[Database & System Architecture](ARCHITECTURE.md)**: Deep-dive into the relational SQLAlchemy schemas, custom HTTP Basic Auth barriers, and cookie compliance tracking engines.
* **[Getting Started & Deployment](GETTING_STARTED.md)**: Installation guidelines, environmental configurations, shell automation scripts, and WSGI production setups.
* **[Model Extraction & Customization Guide](DEVELOPMENT.md)**: Strategies to decouple the data layer, extend existing views, and transition toward a headless API infrastructure.

---

## 🛠️ Technology Stack & Official References

The platform leverages industry-standard, high-performance packages from the Python web ecosystem:

| Component | Technology | Official Reference |
| :--- | :--- | :--- |
| **Web Framework** | Flask (v2.3.3) | [Flask Official Docs](https://flask.palletsprojects.com/) |
| **Backoffice Dashboard** | Flask-Admin (v1.6.1) | [Flask-Admin Documentation](https://flask-admin.readthedocs.io/) |
| **Object-Relational Mapping** | Flask-SQLAlchemy (v3.0.5) | [SQLAlchemy Documentation](https://www.sqlalchemy.org/) |
| **Form Processing & Validation** | Flask-WTF & WTForms | [WTForms Ecosystem](https://wtforms.readthedocs.io/) |
| **Imaging Engine Backend** | Pillow (with custom patch) | [Pillow Official Site](https://python-pillow.org/) |

---

## 🚀 Application & Core System Features

### 🎸 Application-Level Capabilities (What the Site Shows)
* **Artist Biographies & Profiles**: Dynamic management of the musician's background text, profile images, and multi-channel resource routing.
* **Social & Stream Synchronization**: Centralized repository for structural asset linking, connecting profiles seamlessly to Spotify, Apple Music, YouTube, Instagram, and custom external social graphs.
* **Tour & Live Show Tracker**: Relational schedule registry grouping complex performance maps (Tours) to granular event instances (Concerts) bound to specific spatial metrics (Venues, Addresses, and Maps).
* **Fan Interaction Guestbook**: A persistent public message board (BoardMessage) enabling organic user engagement and sentiment tracking directly onto the local database.

### ⚙️ System-Level Architectural Operations
* **Basic Auth Protection Barrier**: A secure, decoupled authentication wrapper (<code>AdminAuthenticator</code>) executing raw HTTP header inspections to wall off admin paths without overloading memory footprints.
* **Compliant Consent Matrix**: A granular cookie coordinator (<code>CookieSupporter</code>) parsing and isolating essential operational sessions from analytical tracker objects.
* **Backward-Compatible Imaging Framework**: Includes <code>compatibility_pillow.py</code> to patch deprecation holes inside advanced image filtering calls, guaranteeing long-term operating system package stability.
* **Dual Runtime Engine Configuration**: Native support for instant local debugging wrappers alongside a standard production WSGI exposure target flag.

---

## 🧱 Architectural Schema Overview

<pre>
          [ Public Enduser UI Layer ]             [ Flask-Admin Backoffice Workspace ]
                      |                                            |
                      +--------------------+-----------------------+
                                           |
                                           v
                             [ Flask Application Core Core Engine ]
                                           |
                +--------------------------+--------------------------+
                |                                                     |
                v                                                     v
   [ Cookie & Session Manager ]                          [ Admin HTTP Authentication ]
                |                                                     |
                +--------------------------+--------------------------+
                                           |
                                           v
                              [ SQLAlchemy Relational Layer ]
                                           |
                                           v
                             [ SQLite/PostgreSQL Database ]
</pre>

---

## 📄 License
This web suite and its layout architectures are distributed under the **BSD Free License**. You are authorized to modify, copy, re-implement, distribute, and monetize this system, on the sole condition that the original copyright headers remain intact within the source code files.