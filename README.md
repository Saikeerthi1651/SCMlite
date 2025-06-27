# SCM Project (Shipment Management System)

This project is a **Shipment Management System** built with **FastAPI** for the backend, **MongoDB** for the database, and uses **JWT** for authentication. The system allows users to manage and track shipment# SCM Project (Shipment Management System)

This project is a **Shipment Management System** built with **FastAPI** for the backend, **MongoDB** for the database, and uses **JWT** for authentication. The system allows users to manage and track shipments and devices, and also includes role-based authorization.

## Table of Contents
- [Features](#features)
- [Technologies](#technologies)
- [Installation Instructions](#installation-instructions)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
  - [Environment Variables](#environment-variables)
  - [Running the Project](#running-the-project)
  - [Testing](#testing)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Development Notes](#development-notes)

## Features
- **User Authentication**: User signup and login with JWT-based authentication.
- **Role-Based Access Control**: Admin and user roles with appropriate permissions.
- **Shipment Management**: Create and view shipments.
- **Device Data**: Store and retrieve IoT device sensor data.
- **Frontend**: Static frontend for user interaction.

## Technologies
- **FastAPI** - Web framework for building APIs.
- **Uvicorn** - ASGI server for running FastAPI applications.
- **MongoDB** - NoSQL database to store user and shipment data.
- **JWT** - For user authentication.
- **Kafka** - Messaging service for communication (optional).
- **Pydantic** - Data validation and settings management.
- **python-dotenv** - For loading environment variables.

## Installation Instructions

### Prerequisites
1. Install **Python 3.8+**.
2. Install **MongoDB** (or use a MongoDB cloud service like Atlas).
3. Set up **Kafka** if you plan to use it (optional).

### Setup

Clone this repository to your local machine:

git clone https://github.com/pswaroop412/scm-project.git
cd scm-project



Create and activate a virtual environment:

**Windows:**
python -m venv venv
.\venv\Scripts\activate



**Mac/Linux:**
python3 -m venv venv
source venv/bin/activate



### Environment Variables

Create a `.env` file in the root directory and add the following:

MongoDB URI (for local MongoDB or Atlas connection)
MONGODB_URI=mongodb+srv://<your-username>:<your-password>@cluster0.mongodb.net/<your-db-name>?retryWrites=true&w=majority

JWT Secret Key (Replace with your own secret key)
JWT_SECRET_KEY=your_jwt_secret_key



> **Note:** Replace the placeholders with your actual MongoDB URI and JWT secret key.

### Install Dependencies

pip install -r requirements.txt



### Running the Project

Start the backend server:

uvicorn main:app --reload



The server will start at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

Frontend files are served from the `/frontend` directory.

### Testing

- **Unit Tests:** Write and run unit tests using any test framework like `pytest`.
- **API Endpoints:** Use tools like Postman or `curl` to test the API endpoints.

## Usage

- **Sign Up:** Create a new user by sending a `POST` request to `/auth/signup`.
- **Login:** Authenticate and obtain a JWT token (stored as an HTTP-only cookie).
- **Create Shipment:** Admins can create new shipments via `POST /shipment/create_shipment`.
- **View Shipments:** View all shipments at `/shipment/all_ships`.
- **Device Data:** Access device sensor data at `/device/device_data`.

## API Endpoints

### Authentication Routes

| Method | Endpoint             | Description                      |
|--------|----------------------|--------------------------------|
| POST   | `/auth/signup`       | Sign up a new user              |
| POST   | `/auth/login`        | Login and receive a JWT token   |
| POST   | `/auth/renew_token`  | Renew the JWT token             |
| GET    | `/auth/logout`       | Logout and delete JWT cookie    |

### Shipment Routes

| Method | Endpoint                          | Description                           |
|--------|---------------------------------|-------------------------------------|
| POST   | `/shipment/create_shipment`      | Create a new shipment (Admin only)  |
| GET    | `/shipment/all_ships`            | Retrieve all shipments               |
| GET    | `/shipment/get_shipment/{id}`   | Get details of a specific shipment   |
| GET    | `/shipment/search_shipments`     | Search shipments by logged-in user  |

### Device Routes

| Method | Endpoint              | Description                          |
|--------|-----------------------|------------------------------------|
| GET    | `/device/device_data`  | Retrieve latest IoT device sensor data |

## Development Notes

- **MongoDB:** Stores user data, shipment details, and sensor readings.
- **JWT Authentication:** User authentication is managed via JWT tokens stored in HTTP-only cookies.
- **Role-Based Access:** Admin and user roles control access to certain routes.


## Table of Contents
- [Features](#features)
- [Technologies](#technologies)
- [Installation Instructions](#installation-instructions)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
  - [Environment Variables](#environment-variables)
  - [Running the Project](#running-the-project)
  - [Testing](#testing)
- [Usage](#usage)

## Features
- **User Authentication**: User signup and login with JWT-based authentication.
- **Role-Based Access Control**: Admin and user roles with appropriate permissions.
- **Shipment Management**: Create and view shipments.
- **Device Data**: Store and retrieve IoT device sensor data.
- **Frontend**: Static frontend for user interaction.

## Technologies
- **FastAPI** - Web framework for building APIs.
- **Uvicorn** - ASGI server for running FastAPI applications.
- **MongoDB** - NoSQL database to store user and shipment data.
- **JWT** - For user authentication.
- **Kafka** - Messaging service for communication (if needed).
- **Pydantic** - Data validation and settings management.
- **python-dotenv** - For loading environment variables.

## Installation Instructions

### Prerequisites
1. Install **Python 3.8+**.
2. Install **MongoDB** (or use a MongoDB cloud service like Atlas).
3. Set up **Kafka** if you plan to use it.

### Setup

Clone this repository to your local machine:

```bash
git clone https://github.com/your-username/scm-project.git
cd scm-project
