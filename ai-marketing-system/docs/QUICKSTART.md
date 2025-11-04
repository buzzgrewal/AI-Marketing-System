# Quick Start Guide

Get your AI Marketing Automation System up and running in 15 minutes!

## Prerequisites Checklist

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Node.js 16+ installed (`node --version`)
- [ ] OpenRouter API key ([Sign up here](https://openrouter.ai))
- [ ] Email SMTP credentials (Gmail, SendGrid, etc.)

## Step-by-Step Setup

### 1. Backend Setup (5 minutes)

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
```

**Edit `.env` file with your details:**
```env
SECRET_KEY=your-super-secret-key-change-this
OPENROUTER_API_KEY=sk-or-v1-your-key-here

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Your Company Name
```

### 2. Frontend Setup (3 minutes)

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install
```

### 3. Start Application (2 minutes)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```
✓ Backend running at http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
✓ Frontend running at http://localhost:3000

### 4. First Use (5 minutes)

1. **Open browser**: Go to http://localhost:3000

2. **Start Using** (No Login Required!):
   - System loads directly to dashboard
   - No registration needed

3. **Test Content Generation**:
   - Go to "Content Generator"
   - Click "Generate Content"
   - Topic: "New cycling saddle for triathletes"
   - Click "Generate"
   - Review AI-generated content!

## Common Issues

### "Module not found" error
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

### Port already in use
```bash
# Backend: Change port
uvicorn main:app --port 8001

# Frontend: Change in vite.config.js
```

### OpenRouter API error
- Verify API key in `.env`
- Check API key has credits
- Test at https://openrouter.ai

### Email not working
- For Gmail: Use App Password (not regular password)
- Enable 2FA first, then create App Password
- Or use SendGrid free tier

## Next Steps

1. **Import Leads**: Use the sample CSV template
2. **Generate Content**: Try different content types
3. **Create Campaign**: Send to opted-in leads
4. **View Analytics**: Track performance

## Sample CSV Template

Create `sample_leads.csv`:
```csv
email,first_name,last_name,sport_type,customer_type
john@example.com,John,Doe,cycling,athlete
jane@example.com,Jane,Smith,triathlon,coach
mike@example.com,Mike,Johnson,running,athlete
```

## Quick Commands Reference

```bash
# Start backend
cd backend && source venv/bin/activate && python main.py

# Start frontend
cd frontend && npm run dev

# View API docs
# Open: http://localhost:8000/docs

# Reset database
rm backend/marketing_automation.db
```

## Getting Help

1. Check README.md for detailed documentation
2. Visit http://localhost:8000/docs for API documentation
3. Review logs in terminal for error messages

## Security Reminder

✓ Never commit `.env` file
✓ Use strong SECRET_KEY
✓ Only import contacts with consent
✓ Test campaigns before large sends

---

**Ready to automate your marketing? Let's go! 🚀**
