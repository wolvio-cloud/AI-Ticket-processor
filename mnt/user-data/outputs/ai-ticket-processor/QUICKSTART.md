# 🚀 QUICK START GUIDE

Get your AI Ticket Processor running in **5 minutes**!

## ⚡ Fastest Way to Start

```bash
# 1. Navigate to project
cd ai-ticket-processor

# 2. Start everything with one command
./start.sh

# 3. Open your browser
# Go to: http://localhost:8000/docs
```

That's it! The API is now running.

---

## 🎯 Next Steps

### **1. Create Your Account**

Open the API docs at http://localhost:8000/docs and try:

```bash
# Or use curl:
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "you@example.com",
    "password": "yourpassword123"
  }'
```

### **2. Login & Get Token**

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=you@example.com&password=yourpassword123"
```

Save the `access_token` you get back!

### **3. Configure Integrations**

Using your token:

```bash
curl -X PUT "http://localhost:8000/settings/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "zendesk_subdomain": "your-company",
    "zendesk_email": "you@example.com",
    "zendesk_api_token": "your_zendesk_token",
    "openai_api_key": "sk-your-openai-key"
  }'
```

### **4. Process Your First Ticket**

```bash
curl -X POST "http://localhost:8000/tickets/process" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": 123
  }'
```

---

## 🧪 Test the API

Run the test script:

```bash
python test_api.py
```

This will verify all endpoints are working!

---

## 📊 View Analytics

```bash
curl -X GET "http://localhost:8000/analytics/dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🛑 Stop Services

```bash
docker-compose down
```

---

## 🔧 Troubleshooting

### API won't start?

```bash
# Check if Docker is running
docker ps

# Check logs
docker-compose logs -f backend

# Restart services
docker-compose restart
```

### Can't connect to database?

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Recreate database
docker-compose down -v
docker-compose up -d
```

### Need to reset everything?

```bash
# Remove all containers and data
docker-compose down -v

# Start fresh
./start.sh
```

---

## 📚 More Information

- **Full Documentation**: See [README.md](README.md)
- **Architecture Details**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

---

## 💡 Tips

1. **Use the Swagger UI** at `/docs` - it's interactive!
2. **Check logs** if something fails: `docker-compose logs -f`
3. **The .env file** controls all settings
4. **Test connections** before processing tickets (use `/settings/zendesk/test`)

---

## 🎉 You're Ready!

Your AI Ticket Processor backend is now running and ready to automate your support tickets!

**Next**: Build the React frontend dashboard to visualize everything! 🚀
