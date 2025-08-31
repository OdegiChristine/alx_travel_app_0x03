# 🧳 ALX Travel Listings API

A Django RESTful API backend for managing travel listings, bookings, and reviews. Users can register as hosts or travelers, list accommodations, and make or review bookings.

## 🚀 Features

- ✅ JWT-based authentication
- 🏡 Hosts can list and manage properties
- 📅 Travelers can make bookings and leave reviews
- 📄 Swagger/OpenAPI documentation
- 🛠️ Admin panel for content moderation
- 🐇 Celery + RabbitMQ integration (for async tasks)

## 📦 Tech Stack

- **Backend:** Django, Django REST Framework
- **Database:** MySQL
- **Auth:** djangorestframework-simplejwt
- **Docs:** drf-yasg (Swagger)
- **Async Tasks:** Celery with RabbitMQ
- **Environment Management:** `django-environ`

---

## 📂 Project Structure

alx_travel_app/

├── listings/ # Core app with models, views, serializers

│ ├── models.py # User, Listing, Booking, Review

│ ├── views.py

│ ├── serializers.py

│ ├── urls.py

│ └── management/

│ └── commands/

│ └── seed.py # Custom seed script

├── alx_travel_app/

│ ├── settings.py

│ ├── urls.py

│ └── wsgi.py

├── .env # Environment variables
└── requirements.txt


---

## 🧪 Installation & Setup

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/alx-travel-app.git
cd alx-travel-app
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependenciers
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file:
```dotenv
DEBUG=True
DB_NAME=alx_travel
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306
```
### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Seed Sample Data
```bash
python manage.py seed
```
## Asynchronous Email Notifications with Celery & RabbitMQ

The project uses **Celery** with **RabbitMQ** as a message broker to handle background tasks, such as sending booking confirmation emails asynchronously.

### Workflow
1. **Booking Creation**  
   When a user creates a booking, the system saves it in the database.

2. **Trigger Celery Task**  
   After saving the booking, a Celery task is triggered using `.delay()`.  
   This task is responsible for sending the booking confirmation email.

3. **Email Sending**  
   The task retrieves the booking details and sends an email to the user using Django’s email backend.

4. **Asynchronous Execution**  
   The email is sent in the background by a Celery worker, allowing the API to respond quickly without waiting.

### Setup

1. Start RabbitMQ (as the message broker):
   ```bash
   sudo service rabbitmq-server start
    ```
   
Or via Docker
    ```bash
    docker run -d --hostname rabbit --name rabbitmq -p 5672:5672 rabbitmq:3
    ```

2. Start a Celery worker:
```bash
celery -A alx_travel_app worker -l info
```

3. Run the Django server:
```bash
python manage.py runserver
```

### Configuration
- **Broker**: RabbitMQ (`amqp://localhost`)
- **Result Backend**: RPC (`rpc://`)
- **Email Backend**: Configured in `settings.py` (uses `send_mail`) 
