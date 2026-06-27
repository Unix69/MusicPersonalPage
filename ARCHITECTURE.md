# 🏗️ Database & System Architecture

This file provides a precise engineering breakdown of the core relational structures, internal decorators, and session processing schemas.

---

## 🗄️ Relational Database & Entity Relationship Map

The system runs a fully normalized SQL architecture managed via SQLAlchemy models. The primary architectural backbone separates Core Identity profiles from highly dynamic logistical objects (Tours and Concerts).

### 👥 1. The Artist Identity Group
* **Profile**: The root identity table containing <code>name</code>, raw text <code>bio</code>, and reference pointers to uploaded structural image files.
* **Contact**: Tied to a Profile via a tight **1:1 Relational Bound** (<code>uselist=False</code>) with strict cascade deletion parameters. It houses protected transactional lines like emails and phone registries.
* **MusicChannels & Socials**: Independent structured entities handling external hyperlink allocations (e.g., Spotify trackers, social graph URIs). They feature single-parent enforcement vectors to prevent data corruption.

### 📅 2. The Logistical Event Pipeline
* **Tour**: Represents an aggregate operational tour framework (e.g., "World Tour 2026"). It maintains a direct **1:1 Relationship** with a <code>TourSchedule</code> (defining structural boundaries via <code>startdate</code> and <code>enddate</code>) and a **1:N Relationship** with physical concert entries.
* **Concert**: The relational binding element interconnecting a specific <code>Tour</code>, a <code>Place</code> node, and a definitive chronological scheduler instance.
* **Place & Address**: Highly normalized structural lookup tables designed to decouple geographical data points (City, Venue Title, Zip Codes, Street names) from volatile event planning schedules.

| Database Table | Core Responsibility | Relational Mapping Vector |
| :--- | :--- | :--- |
| **Profile** | Base Identity Root | Parent of Contact, MusicChannels, Socials (1:1 Single Parent) |
| **Tour** | Unified Event Series Grouping | Parent of TourSchedule (1:1) and Concert (1:N) |
| **Concert** | Event Instance Concrete Spec | Many-to-One Child linked to Tour, Place, Schedule |
| **BoardMessage** | Unauthenticated Fan Registry | Isolated Chronological Storage Stream |

---

## 🔐 Authentication Infrastructure & Admin Security

The security configuration avoids session-state overhead by executing real-time inspection of inbound network packets using an elegant Basic HTTP authorization wrapper.

* **Decoupled Protection Core**: The <code>AdminView</code> overrides standard Flask-Admin accessibility boundaries by interfacing directly with the custom <code>AdminAuthenticator</code> entity.
* **Inbound Header Verification**: The system queries <code>request.authorization</code>. If credentials match the values loaded from environment parameters during bootstrap, execution is authorized; otherwise, it sends an immediate HTTP 401 response containing a <code>WWW-Authenticate</code> challenge header.

---

## 🍪 Compliance & Cookie Tracking Protocol

The framework includes a built-in module (<code>CookieSupporter</code>) designed to satisfy data protection regulations by enforcing user-selected tracking restrictions.

* **Route Registration Framework**: Hooks directly into the Flask application instance to handle state payloads through a dedicated <code>/set_cookie</code> target path.
* **Serialization Processing Flow**: Automatically constructs and serializes structured cookie records. If an end user rejects non-essential analytical cookies, the engine safely triggers explicit termination routines, deleting old cookies from the client browser by setting their expiration date to zero (<code>expires=0</code>).