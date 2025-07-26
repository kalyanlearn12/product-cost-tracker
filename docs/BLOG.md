# Building a Professional Product Cost Tracker: A Developer’s Journey

## Introduction
Over the course of this project, we set out to build a robust, user-friendly, and intelligent product price tracker for e-commerce sites. The goal: track prices, discover coupons, and send Telegram notifications when deals are found—all using only free, prominent Python libraries.

## The Journey
### 1. **Scaffolding and Core Features**
We began by designing a Flask web app with a simple UI for users to enter product URLs, target prices, and Telegram details. The backend used Requests and BeautifulSoup for scraping, and python-telegram-bot for notifications. Early on, we added coupon extraction logic and made alternate site checking configurable.

### 2. **Notification Logic and Debugging**
Telegram integration was prioritized, and we iteratively debugged notification delivery and coupon extraction (including handling dynamic content). WhatsApp support was considered but dropped for simplicity and cost.

### 3. **Scheduling and Persistence**
We implemented per-product scheduling using APScheduler, allowing users to choose how often each product is checked (1 min, 2/4/8/16/24 hrs). Scheduled products are persisted in a JSON file, so tracking resumes after restarts.

### 4. **User Experience and Professionalism**
The UI was refined for clarity and balance, with input on the left and results on the right. We added the ability to delete scheduled products, default chat IDs, and made the app robust to empty or missing files. The workspace was cleaned of unused files and code.

### 5. **Testing and Documentation**
We wrote and updated test cases to ensure all logic works as expected. Documentation and user guides were updated to reflect the latest features and best practices.

## Lessons Learned
- **User feedback is invaluable:** Each round of feedback led to a more robust, user-friendly, and maintainable solution.
- **Simplicity wins:** Focusing on Telegram-only notifications and a clean UI made the app easier to use and maintain.
- **Persistence and scheduling matter:** Users expect their settings and schedules to survive restarts—robust persistence and per-product scheduling are key.

## Conclusion
The result is a professional, production-ready product cost tracker that’s easy to use, easy to extend, and reliable for daily use. The journey highlights the value of iterative development, user-driven design, and clean code practices.

---
