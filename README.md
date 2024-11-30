# Multi-Service Application with Docker Compose

This project consists of multiple services that work together to provide a functional system. Each service is containerized using Docker, and the setup is managed with Docker Compose.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Setup Instructions](#setup-instructions)
   - [Environment Variables](#environment-variables)
   - [Docker Compose Setup](#docker-compose-setup)
4. [Services Overview](#services-overview)

---

## Project Overview
The application is composed of the following services:
1. **User Service** (Python): Manages user-related operations.
2. **Catalogue Service** (Python): Handles product information and catalog management.
3. **Order Service** (PHP): Manages order creation.
4. **Frontend** (React): A user-facing interface to interact with the backend services.

---

## Architecture
The system is composed of the following components:
- **Backend Services**:
  - User Service
  - Catalogue Service
  - Order Service
- **Databases**:
  - Each service has its dedicated MySQL database.
- **Frontend**:
  - A React application communicates with the backend services.
- **Network**:
  - All services communicate through a custom Docker network (`library-net`).

---

## Setup Instructions

### Environment Variables
Ensure the `.env` files for each service are configured correctly. Each service has specific environment variables to connect to its database. Example `.env` file for the **User Service**:

```env
DB_HOST=user-database
DB_USER=user_service_user
DB_PASS=user_service_pass
DB_NAME=user_service_db
```
Example for the **Catalogue Service**: 
```env
DB_HOST: catalog-database
DB_USER: catalog_user
DB_PASS: catalog_pass
DB_NAME: catalog_db
```

Example for the **Order Service**:
```env
DB_HOST: order-database
DB_NAME: order_service_db
DB_USER: order_service_user
DB_PASS: order_service_pass
```

### Docker Compose Setup

**Build and start all services:**

```bash
docker-compose up --build
```

**Verify the services are running:**

-   Frontend: [http://localhost:3000](http://localhost:3000/)
-   User Service: [http://localhost:5001](http://localhost:5001/)
-   Catalogue Service: [http://localhost:5002](http://localhost:5002/)
-   Order Service: [http://localhost:5003](http://localhost:5003/)

**Stop and clean up the containers:**

```bash
docker-compose down -v
```

# Services Overview

## User Service
- **Language**: Python
- **Description**: Manages user data and authentication.
- **CRUD Operations**:
  - `POST /users/register`: Register a new user.
  - `POST /users/login`: User login.
  - `GET /users`: Retrieve all users.
  - `GET /users/{id}`: Retrieve user details by ID.
  - `PUT /users/{id}`: Update user details.
  - `DELETE /users/{id}`: Delete a user.

---

## Catalogue Service
- **Language**: Python
- **Description**: Manages the product catalog, allowing users to browse, add, and update products.
- **CRUD Operations**:
  - `POST /books`: Add a new book.
  - `GET /books`: Retrieve all books..
  - `GET /books/{id}`: Retrieve a book details by ID.
  - `GET /books/author/{author_name}`: Retrieve books details by its author.
  - `GET /books/name/{book_title}`: Retrieve books details by its title.
  - `PUT /books/{id}`: Update informations for a specific book.
  - `DELETE /books/{id}`: Remove a book.

---

## Order Service
- **Language**: PHP
- **Description**: Handles customer orders, including order creation and status tracking.
- **CRUD Operations**:
  - `POST /orders`: Create a new order.
  - `GET /orders`: Retrieve all orders.
  - `GET /orders/{id}`: Retrieve order details.
  - `PUT /orders/{id}`: Update an order.
  - `DELETE /orders/{id}`: Delete an order.

---

## Frontend
- **Language**: React (JavaScript)
- **Description**: A web interface that allows users to interact with the backend services for managing users, products, and orders.
