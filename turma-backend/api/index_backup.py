from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import jwt
import hashlib
import json
import csv
import io

app = Flask(__name__)
CORS(app, origins="*")

# Secret key for JWT
SECRET_KEY = "turma-digital-agency-secret-key-2024"

# In-memory database (replace with real database in production)
users_db = [
    {
        "id": 1,
        "name": "Admin User",
        "email": "admin@turmadigital.com",
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "position": "System Administrator",
        "department": "IT",
        "created_at": "2024-01-01T00:00:00",
        "is_active": True
    },
    {
        "id": 2,
        "name": "John Doe",
        "email": "john.doe@turmadigital.com",
        "password": hashlib.sha256("password123".encode()).hexdigest(),
        "role": "employee",
        "position": "Software Developer",
        "department": "Engineering",
        "created_at": "2024-01-01T00:00:00",
        "is_active": True
    },
    {
        "id": 3,
        "name": "Jane Smith",
        "email": "jane.smith@turmadigital.com",
        "password": hashlib.sha256("password123".encode()).hexdigest(),
        "role": "employee",
        "position": "UI/UX Designer",
        "department": "Design",
        "created_at": "2024-01-01T00:00:00",
        "is_active": True
    },
    {
        "id": 4,
        "name": "Mike Johnson",
        "email": "mike.johnson@turmadigital.com",
        "password": hashlib.sha256("password123".encode()).hexdigest(),
        "role": "employee",
        "position": "Project Manager",
        "department": "Operations",
        "created_at": "2024-01-01T00:00:00",
        "is_active": True
    }
]

time_records_db = []
eod_reports_db = []
announcements_db = [
    {
        "id": 1,
        "title": "Welcome to Turma Digital Agency",
        "content": "Welcome to our new employee management system. Please familiarize yourself with all the features.",
        "priority": "normal",
        "date": "2024-01-15",
        "created_by": 1,
        "created_at": "2024-01-15T09:00:00"
    },
    {
        "id": 2,
        "title": "System Maintenance",
        "content": "Scheduled maintenance will occur this weekend. Please save your work regularly.",
        "priority": "high",
        "date": "2024-01-16",
        "created_by": 1,
        "created_at": "2024-01-16T10:00:00"
    }
]

# Request management databases
leave_requests_db = []
salary_loan_requests_db = []
time_adjustment_requests_db = []

# Training materials database - will be populated from CSV
training_materials_db = [
    {
        "Tutorial Title": "Google\u2019s AI Course for Beginners",
        "Article Link": "https://grow.google/ai-essentials/?utm_source=chatgpt.com",
        "Video": "https://www.youtube.com/watch?v=Yq0QkCxoTHM",
        "Categories": "AI Fundamentals",
        "Tags": "AI, Beginner, Google AI, Basics"
    },
    {
        "Tutorial Title": "Harvard CS50\u2019s Artificial Intelligence with Python",
        "Article Link": "https://medium.com/analytics-vidhya/how-to-break-into-ai-harvard-cs50ai-introduction-to-artificial-intelligence-course-review-fe14b78e6575?utm_source=chatgpt.com",
        "Video": "https://www.youtube.com/watch?v=5NgNicANyqM",
        "Categories": "Artificial Intelligence with Python",
        "Tags": "Harvard, Python, AI, CS50"
    },
    {
        "Tutorial Title": "How To Make An Art Audio Course Using AI To Sell More Art",
        "Article Link": "https://www.elegantthemes.com/blog/design/midjourney-ai-art?utm_source=chatgpt.com",
        "Video": "https://www.youtube.com/watch?v=mQkUxUrCKFg",
        "Categories": "AI & Art",
        "Tags": "Art, Audio Course, AI, Monetization"
    },
    {
        "Tutorial Title": "AI Agents Fundamentals In 21 Minutes",
        "Article Link": "https://www.ai-academy.com/blog/understanding-ai-agents-from-fundamentals-to-implementation?utm_source=chatgpt.com",
        "Video": "https://www.youtube.com/watch?v=qU3fmidNbJE&t=73s",
        "Categories": "Agents",
        "Tags": "AI Agents, Fundamentals, Quick Guide"
    },
    {
        "Tutorial Title": "Midjourney AI Tutorial | Learn How To Use Midjourney",
        "Article Link": "https://docs.midjourney.com/hc/en-us/articles/33329261836941-Getting-Started-Guide?utm_source=chatgpt.com",
        "Video": "https://www.youtube.com/watch?v=dBvdGJVF4ic&list=PL9ooVrP1hQOFIOOkGN2gbjvse8jcz-mux&index=4",
        "Categories": "Image Generation",
        "Tags": "Midjourney, AI Art, Image Generation"
    },
    {
        "Tutorial Title": "Prompt Engineering For Code Generation ",
        "Article Link": "https://www.promptingguide.ai/applications/coding?utm_source=chatgpt.com",
        "Video": "https://www.youtube.com/watch?v=oFj3dHcEKqg&list=PL9ooVrP1hQOFIOOkGN2gbjvse8jcz-mux&index=10",
        "Categories": "Code Generation",
        "Tags": "Prompt Engineering, Code, AI, Programming"
    },
    {
        "Tutorial Title": "AI for Marketing",
        "Article Link": "https://professional.dce.harvard.edu/blog/ai-will-shape-the-future-of-marketing/?utm_source=chatgpt.com",
        "Video": "https://www.youtube.com/watch?v=HA4G14DCiT0&list=PL9ooVrP1hQOFIOOkGN2gbjvse8jcz-mux&index=14",
        "Categories": "Marketing",
        "Tags": "AI Marketing, Business, Strategy"
    },
    {
        "Tutorial Title": "Whats new in ChatGPT 4o | ChatGPT 4o explained",
        "Article Link": "https://www.techtarget.com/whatis/feature/GPT-4o-explained-Everything-you-need-to-know?utm_source=chatgpt.com",
        "Video": "https://www.youtube.com/watch?v=x6srdggPQr4&list=PL9ooVrP1hQOFIOOkGN2gbjvse8jcz-mux&index=15",
        "Categories": "ChatGPT",
        "Tags": "ChatGPT 4o, OpenAI, AI Update"
    },
    {
        "Tutorial Title": "AI for HR | Generative AI for HR",
        "Article Link": "https://www.shrm.org/labs/resources/generative-ai-for-hr?utm_source=chatgpt.com",
        "Video": "https://www.youtube.com/watch?v=OK2mmINL4NY&list=PL9ooVrP1hQOFIOOkGN2gbjvse8jcz-mux&index=17",
        "Categories": "AI for HR",
        "Tags": "AI, HR, Generative AI"
    },
    {
        "Tutorial Title": "AI in Cybersecurity | Working of AI in Cybersecurity",
        "Article Link": "https://www.excelsior.edu/article/ai-in-cybersecurity/?utm_source=chatgpt.com",
        "Video": "https://www.youtube.com/watch?v=3tqkiUT9Sxw&list=PL9ooVrP1hQOFIOOkGN2gbjvse8jcz-mux&index=19",
        "Categories": "Security",
        "Tags": "Cybersecurity, AI, Security Tools"
    },
    {
        "Tutorial Title": "AI for legal | AI Legal assistant for Lawyers",
        "Article Link": "https://timesofindia.indiatimes.com/city/delhi/e-research-library-with-ai-tools-to-assist-lawyers/articleshow/122348095.cms?utm_source=chatgpt.com",
        "Video": "https://www.youtube.com/watch?v=JUbknnxkAAg&list=PL9ooVrP1hQOFIOOkGN2gbjvse8jcz-mux&index=20",
        "Categories": "Legal",
        "Tags": "AI Legal Assistant, Law, Productivity, Legal Tech"
    },
    {
        "Tutorial Title": "What is LLM | Mastering Generative AI: Build Cutting-Edge Projects & Concepts",
        "Article Link": "https://www.techtarget.com/whatis/feature/GPT-4o-explained-Everything-you-need-to-know?utm_source=chatgpt.com",
        "Video": "https://www.youtube.com/watch?v=JUbknnxkAAg&list=PL9ooVrP1hQOFIOOkGN2gbjvse8jcz-mux&index=20",
        "Categories": "LLM Concepts",
        "Tags": "LLM, Generative AI, Projects, Concepts"
    },
    {
        "Tutorial Title": "What is LangChain? | How LangChain is Changing the Way We Use APIs |",
        "Article Link": "",
        "Video": "https://www.youtube.com/watch?v=V6ddMAUCOys&list=PL9ooVrP1hQOFIOOkGN2gbjvse8jcz-mux&index=31",
        "Categories": "Tooling",
        "Tags": "LangChain, API Integration, AI Tools"
    },
    {
        "Tutorial Title": "What is Shell GPT? | Unlocking ChatGPT on Linux",
        "Article Link": "",
        "Video": "https://www.youtube.com/watch?v=Sq_K7lTZjnM&list=PL9ooVrP1hQOFIOOkGN2gbjvse8jcz-mux&index=33",
        "Categories": "CLI Tools",
        "Tags": "Shell GPT, Linux, CLI, ChatGPT"
    },
    {
        "Tutorial Title": "Schedule a Meeting",
        "Article Link": "https://support.zoom.us/hc/en-us/articles/201362003-Scheduling-your-first-meeting",
        "Video": "https://www.youtube.com/watch?v=Cbw1UhvSQRU",
        "Categories": "Communication & Meetings",
        "Tags": "Zoom, scheduling, meetings"
    },
    {
        "Tutorial Title": "Create Recurring Meetings",
        "Article Link": "https://support.zoom.us/hc/en-us/articles/360020673491-Recurring-meetings",
        "Video": "https://www.youtube.com/watch?v=Dq6mo6Rgpic",
        "Categories": "Communication & Meetings",
        "Tags": "Zoom, recurring meetings"
    },
    {
        "Tutorial Title": "Screen Sharing",
        "Article Link": "https://support.zoom.us/hc/en-us/articles/201362153-Sharing-your-screen",
        "Video": "https://www.youtube.com/watch?v=XH-K0AdQacw",
        "Categories": "Communication & Meetings",
        "Tags": "Zoom, screen share"
    },
    {
        "Tutorial Title": "Local Recording",
        "Article Link": "https://support.zoom.us/hc/en-us/articles/201362473-Local-recording",
        "Video": "https://www.youtube.com/watch?v=Kb8DJ-2g1xs",
        "Categories": "Communication & Meetings",
        "Tags": "Zoom, recording"
    },
    {
        "Tutorial Title": "Managing Breakout Rooms",
        "Article Link": "https://support.zoom.us/hc/en-us/articles/360032750952-Managing-breakout-rooms",
        "Video": "https://www.youtube.com/watch?v=G0oK_mpaHU4",
        "Categories": "Communication & Meetings",
        "Tags": "Zoom, breakout rooms"
    },
    {
        "Tutorial Title": "Create a Channel",
        "Article Link": "https://slack.com/help/articles/360022499954-Creating-a-channel",
        "Video": "https://www.youtube.com/watch?v=Sod4uWWy7zs",
        "Categories": "Communication & Meetings",
        "Tags": "Slack, channels"
    },
    {
        "Tutorial Title": "Workflow Builder Basics",
        "Article Link": "https://slack.com/help/articles/17542172840595-Build-a-workflow--Create-a-workflow-in-Slack",
        "Video": "https://www.youtube.com/watch?v=7PwwJjU_uGc",
        "Categories": "Communication & Meetings",
        "Tags": "Slack, Workflow Builder, basics"
    },
    {
        "Tutorial Title": "9 Slack Workflow Examples",
        "Article Link": "https://zapier.com/blog/slack-workflow-builder/",
        "Video": "https://www.youtube.com/watch?v=j8hbXWRti6U",
        "Categories": "Communication & Meetings",
        "Tags": "Slack, Workflow Builder, examples"
    },
    {
        "Tutorial Title": "Schedule a Meeting",
        "Article Link": "https://support.microsoft.com/en-us/office/schedule-a-meeting-in-microsoft-teams-943507a9-8583-4c58-b5d2-8ec8265e04e5",
        "Video": "https://www.youtube.com/watch?v=P90nz4-IUiI",
        "Categories": "Communication & Meetings",
        "Tags": "Teams, scheduling"
    },
    {
        "Tutorial Title": "Plan a Live Event",
        "Article Link": "https://support.microsoft.com/en-us/office/plan-and-schedule-a-live-event-f92363a0-6d98-46d2-bdd9-f2248075e502",
        "Video": "https://www.youtube.com/watch?v=fUPNK3mvWzs",
        "Categories": "Communication & Meetings",
        "Tags": "Teams, live events"
    },
    {
        "Tutorial Title": "Getting Started with Calendly",
        "Article Link": "https://help.calendly.com/hc/en-us/articles/360020195534-Getting-Started-with-Calendly",
        "Video": "https://www.youtube.com/watch?v=LLbCX31HiQ8",
        "Categories": "Scheduling & Calendar",
        "Tags": "Calendly, setup, scheduling"
    },
    {
        "Tutorial Title": "Embed Calendly on a Website",
        "Article Link": "https://help.calendly.com/hc/en-us/articles/223147027-How-do-I-embed-Calendly-on-a-website",
        "Video": "https://www.youtube.com/watch?v=_n3m5MGYBsY",
        "Categories": "Scheduling & Calendar",
        "Tags": "Calendly, embed, website"
    },
    {
        "Tutorial Title": "Create a Doodle Poll",
        "Article Link": "https://support.doodle.com/hc/en-us/articles/115005982629-How-to-schedule-a-Doodle-poll",
        "Video": "https://www.youtube.com/watch?v=5ZrTk3h0uhM",
        "Categories": "Scheduling & Calendar",
        "Tags": "Doodle, polls"
    },
    {
        "Tutorial Title": "Advanced Doodle Settings",
        "Article Link": "https://support.doodle.com/hc/en-us/articles/360017092479-Advanced-settings-for-Doodle-polls",
        "Video": "https://www.youtube.com/watch?v=8aQHQZMaDnU",
        "Categories": "Scheduling & Calendar",
        "Tags": "Doodle, advanced"
    },
    {
        "Tutorial Title": "Trello Guide for Beginners",
        "Article Link": "https://trello.com/guide",
        "Video": "https://www.youtube.com/watch?v=geRKHFzTxNY",
        "Categories": "Project & Task Management",
        "Tags": "Trello, basics"
    },
    {
        "Tutorial Title": "Butler Automation Basics",
        "Article Link": "https://trello.com/guide/automate-anything",
        "Video": "https://www.youtube.com/watch?v=-emiHNjVNa4",
        "Categories": "Project & Task Management",
        "Tags": "Trello, automation"
    },
    {
        "Tutorial Title": "Using Power-Ups",
        "Article Link": "https://support.atlassian.com/trello/docs/power-ups/",
        "Video": "https://www.youtube.com/watch?v=3hoEhOzumyc",
        "Categories": "Project & Task Management",
        "Tags": "Trello, Power-Ups"
    },
    {
        "Tutorial Title": "Getting Started with Asana",
        "Article Link": "https://asana.com/guide/help/get-started/basics",
        "Video": "https://www.youtube.com/watch?v=xlW3rnrOdgg",
        "Categories": "Project & Task Management",
        "Tags": "Asana, basics"
    },
    {
        "Tutorial Title": "Workflows & Rules",
        "Article Link": "https://asana.com/guide/help/advanced/workflows",
        "Video": "https://www.youtube.com/watch?v=5jVsYLGSJ78",
        "Categories": "Project & Task Management",
        "Tags": "Asana, automation"
    },
    {
        "Tutorial Title": "ClickUp Getting Started",
        "Article Link": "https://clickup.com/blog/getting-started/",
        "Video": "https://www.youtube.com/watch?v=ZFRlCYZwjNI",
        "Categories": "Project & Task Management",
        "Tags": "ClickUp, basics"
    },
    {
        "Tutorial Title": "Automations in ClickUp",
        "Article Link": "https://clickup.com/features/automations",
        "Video": "https://www.youtube.com/watch?v=R1eJULWxMYY",
        "Categories": "Project & Task Management",
        "Tags": "ClickUp, automation"
    },
    {
        "Tutorial Title": "Remove Image Background with Background Remover",
        "Article Link": "https://www.canva.com/features/background-remover/",
        "Video": "https://www.youtube.com/watch?v=YJbg5aEcn8g",
        "Categories": "Graphic Design",
        "Tags": "background-removal,canva"
    },
    {
        "Tutorial Title": "Collaborate Using Team Folders",
        "Article Link": "https://www.canva.com/help/team-folders/",
        "Video": "https://www.youtube.com/watch?v=FhEwWQnCiq0",
        "Categories": "Graphic Design",
        "Tags": "team-folders,canva"
    },
    {
        "Tutorial Title": "Set Up Veo Cam for Recording",
        "Article Link": "https://support.veo.co/hc/en-us/articles/5922516538897-How-to-set-up-your-Veo-Cam-for-recording",
        "Video": "https://www.youtube.com/watch?v=1UOOwDtCTQw",
        "Categories": "Sports Analytics",
        "Tags": "setup,recording"
    },
    {
        "Tutorial Title": "Live Stream to YouTube via RTMP",
        "Article Link": "https://support.veo.co/hc/en-us/articles/26783279685265-Live-stream-to-YouTube-with-your-Veo-Cam",
        "Video": "https://www.youtube.com/watch?v=XbIrCNHoafo",
        "Categories": "Sports Analytics",
        "Tags": "live-stream,rtmp"
    },
    {
        "Tutorial Title": "Send SMS with Twilio Quickstart",
        "Article Link": "https://www.twilio.com/docs/sms/send-messages",
        "Video": "https://www.youtube.com/watch?v=hvEYNMvlpBE",
        "Categories": "Communication API",
        "Tags": "sms,api"
    },
    {
        "Tutorial Title": "Implement Phone Verification with Twilio Verify",
        "Article Link": "https://www.twilio.com/docs/verify/api",
        "Video": "https://www.youtube.com/watch?v=Fdoxg0SjNP8",
        "Categories": "Communication API",
        "Tags": "verify,api"
    },
    {
        "Tutorial Title": "Create and Send Your First Campaign in MailerLite",
        "Article Link": "https://help.mailerlite.com/tutorial-how-to-send-your-first-campaign",
        "Video": "https://www.youtube.com/watch?v=6wz9oMnzITs",
        "Categories": "Email Marketing",
        "Tags": "campaigns,mailerlite"
    },
    {
        "Tutorial Title": "Build Automation Workflows in MailerLite",
        "Article Link": "https://help.mailerlite.com/tutorial-how-to-create-an-automation",
        "Video": "https://www.youtube.com/watch?v=Qf3Scci8vJE",
        "Categories": "Email Marketing",
        "Tags": "automation,workflows"
    },
    {
        "Tutorial Title": "Record Your First Loom Video",
        "Article Link": "https://support.loom.com/hc/en-us/articles/360038471414-Launch-your-first-Recording",
        "Video": "https://www.youtube.com/watch?v=1sAcNLfRhKE",
        "Categories": "Video Recording",
        "Tags": "screen-recording,loom"
    },
    {
        "Tutorial Title": "Customize Viewer Call-to-Actions in Loom",
        "Article Link": "https://support.loom.com/hc/en-us/articles/360046638314-Using-Viewer-Customizations",
        "Video": "https://www.youtube.com/watch?v=FjFIFtEUxC8",
        "Categories": "Video Recording",
        "Tags": "customization,CTA"
    },
    {
        "Tutorial Title": "Schedule Email Delivery in Outlook",
        "Article Link": "https://support.microsoft.com/office/schedule-email-delivery",
        "Video": "https://www.youtube.com/watch?v=2a9YXA3fDxA",
        "Categories": "Email Client",
        "Tags": "email,delay-delivery"
    },
    {
        "Tutorial Title": "Create Advanced Mail Rules in Outlook",
        "Article Link": "https://support.microsoft.com/office/manage-email-messages-by-using-rules",
        "Video": "https://www.youtube.com/watch?v=XeAqGhrYr2Y",
        "Categories": "Email Client",
        "Tags": "rules,automation"
    },
    {
        "Tutorial Title": "Undo Send Emails in Gmail",
        "Article Link": "https://support.google.com/mail/answer/1385",
        "Video": "https://www.youtube.com/watch?v=DlUbp01l2To",
        "Categories": "Email Client",
        "Tags": "undo-send,gmail"
    },
    {
        "Tutorial Title": "Set Up Filters and Labels in Gmail",
        "Article Link": "https://support.google.com/mail/answer/6579",
        "Video": "https://www.youtube.com/watch?v=mn22fUvKl1A",
        "Categories": "Email Client",
        "Tags": "filters,labels"
    },
    {
        "Tutorial Title": "Build a Sales Funnel in GoHighLevel",
        "Article Link": "https://help.gohighlevel.com/en/articles/3174229-funnel-builder",
        "Video": "https://www.youtube.com/watch?v=ZYUlfUNKQo0",
        "Categories": "Marketing Automation",
        "Tags": "funnels,automation"
    },
    {
        "Tutorial Title": "Integrate Custom APIs in GoHighLevel",
        "Article Link": "https://help.gohighlevel.com/en/articles/3384715-api-overview",
        "Video": "https://www.youtube.com/watch?v=6OMx-6Z0GFY",
        "Categories": "Marketing Automation",
        "Tags": "api,integration"
    },
    {
        "Tutorial Title": "Send and Request Money with PayPal",
        "Article Link": "https://www.paypal.com/us/smarthelp/article/how-do-i-send-money-to-a-friend-or-family-member-faq2997",
        "Video": "https://www.youtube.com/watch?v=hlwVUahTj2k",
        "Categories": "Payment Processing",
        "Tags": "transfers,paypal"
    },
    {
        "Tutorial Title": "Set Up Recurring Subscriptions with PayPal",
        "Article Link": "https://developer.paypal.com/docs/subscriptions/integrate",
        "Video": "https://www.youtube.com/watch?v=aypY9Ku1CcY",
        "Categories": "Payment Processing",
        "Tags": "subscriptions,api"
    },
    {
        "Tutorial Title": "Generate Instagram Hashtags with Rella",
        "Article Link": "https://www.rella.co/hashtag-generator",
        "Video": "https://www.youtube.com/watch?v=Q2fT4z4Yz98",
        "Categories": "Social Media Marketing",
        "Tags": "hashtags,Instagram"
    },
    {
        "Tutorial Title": "Analyze Competitor Hashtags in Rella",
        "Article Link": "https://www.rella.co/analytics",
        "Video": "https://www.youtube.com/watch?v=3RfQ5YPH4uA",
        "Categories": "Social Media Marketing",
        "Tags": "analytics,hashtags"
    },
    {
        "Tutorial Title": "Canva Magic Resize Trick",
        "Article Link": "https://www.canva.com/features/magic-resize/",
        "Video": "https://www.youtube.com/watch?v=1UZ-Hi3uzr4",
        "Categories": "Graphic Design",
        "Tags": "magic-resize;canva"
    },
    {
        "Tutorial Title": "Canva Keyboard Shortcuts for Speed",
        "Article Link": "https://www.canva.com/learn/keyboard-shortcuts/",
        "Video": "https://www.youtube.com/watch?v=xOyK2sCje-4",
        "Categories": "Graphic Design",
        "Tags": "keyboard-shortcuts;efficiency"
    },
    {
        "Tutorial Title": "Send SMS with Twilio Quickstart",
        "Article Link": "https://www.twilio.com/docs/sms/send-messages",
        "Video": "https://www.youtube.com/watch?v=kb9aV_tjY-0",
        "Categories": "Communication API",
        "Tags": "sms;api"
    },
    {
        "Tutorial Title": "Implement Phone Verification with Twilio Verify",
        "Article Link": "https://www.twilio.com/docs/verify/api",
        "Video": "https://www.youtube.com/watch?v=UBjMm_nb45U",
        "Categories": "Communication API",
        "Tags": "verify;api"
    },
    {
        "Tutorial Title": "Create and Send Your First Campaign in MailerLite",
        "Article Link": "https://help.mailerlite.com/tutorial-how-to-send-your-first-campaign",
        "Video": "https://www.youtube.com/watch?v=6wz9oMnzITs",
        "Categories": "Email Marketing",
        "Tags": "campaigns;mailerlite"
    },
    {
        "Tutorial Title": "Build Automation Workflows in MailerLite",
        "Article Link": "https://help.mailerlite.com/tutorial-how-to-create-an-automation",
        "Video": "https://www.youtube.com/watch?v=Qf3Scci8vJE",
        "Categories": "Email Marketing",
        "Tags": "automation;workflows"
    },
    {
        "Tutorial Title": "Record Your First Loom Video",
        "Article Link": "https://support.loom.com/hc/en-us/articles/360038471414-Launch-your-first-Recording",
        "Video": "https://www.youtube.com/watch?v=1sAcNLfRhKE",
        "Categories": "Video Recording",
        "Tags": "screen-recording;loom"
    },
    {
        "Tutorial Title": "Customize Viewer Call-to-Actions in Loom",
        "Article Link": "https://support.loom.com/hc/en-us/articles/360046638314-Using-Viewer-Customizations",
        "Video": "https://www.youtube.com/watch?v=FjFIFtEUxC8",
        "Categories": "Video Recording",
        "Tags": "customization;CTA"
    },
    {
        "Tutorial Title": "Schedule Email Delivery in Outlook",
        "Article Link": "https://support.microsoft.com/office/schedule-email-delivery",
        "Video": "https://www.youtube.com/watch?v=2a9YXA3fDxA",
        "Categories": "Email Client",
        "Tags": "email;delay-delivery"
    },
    {
        "Tutorial Title": "Create Advanced Mail Rules in Outlook",
        "Article Link": "https://support.microsoft.com/office/manage-email-messages-by-using-rules",
        "Video": "https://www.youtube.com/watch?v=XeAqGhrYr2Y",
        "Categories": "Email Client",
        "Tags": "rules;automation"
    },
    {
        "Tutorial Title": "Undo Send Emails in Gmail",
        "Article Link": "https://support.google.com/mail/answer/1385",
        "Video": "https://www.youtube.com/watch?v=DlUbp01l2To",
        "Categories": "Email Client",
        "Tags": "undo-send;gmail"
    },
    {
        "Tutorial Title": "Set Up Filters and Labels in Gmail",
        "Article Link": "https://support.google.com/mail/answer/6579",
        "Video": "https://www.youtube.com/watch?v=mn22fUvKl1A",
        "Categories": "Email Client",
        "Tags": "filters;labels"
    },
    {
        "Tutorial Title": "Build a Sales Funnel in GoHighLevel",
        "Article Link": "https://help.gohighlevel.com/en/articles/3174229-funnel-builder",
        "Video": "https://www.youtube.com/watch?v=ZYUlfUNKQo0",
        "Categories": "Marketing Automation",
        "Tags": "funnels;automation"
    },
    {
        "Tutorial Title": "Send and Request Money with PayPal",
        "Article Link": "https://www.paypal.com/us/smarthelp/article/how-do-i-send-money-to-a-friend-or-family-member-faq2997",
        "Video": "https://www.youtube.com/watch?v=hlwVUahTj2k",
        "Categories": "Payment Processing",
        "Tags": "transfers;paypal"
    },
    {
        "Tutorial Title": "Set Up Recurring Subscriptions with PayPal",
        "Article Link": "https://developer.paypal.com/docs/subscriptions/integrate",
        "Video": "https://www.youtube.com/watch?v=aypY9Ku1CcY",
        "Categories": "Payment Processing",
        "Tags": "subscriptions;api"
    },
    {
        "Tutorial Title": "Analyze Competitor Hashtags in Rella",
        "Article Link": "https://www.rella.co/analytics",
        "Video": "https://www.youtube.com/watch?v=3RfQ5YPH4uA",
        "Categories": "Social Media Marketing",
        "Tags": "analytics;hashtags"
    },
    {
        "Tutorial Title": "Set Up Veo Cam for Recording",
        "Article Link": "https://support.veo.co/hc/en-us/articles/5922516538897-How-to-set-up-your-Veo-Cam-for-recording",
        "Video": "https://www.youtube.com/watch?v=1UOOwDtCTQw",
        "Categories": "Sports Analytics",
        "Tags": "setup;recording"
    },
    {
        "Tutorial Title": "Live Stream to YouTube via RTMP",
        "Article Link": "https://support.veo.co/hc/en-us/articles/26783279685265-Live-stream-to-YouTube-with-your-Veo-Cam",
        "Video": "https://www.youtube.com/watch?v=XbIrCNHoafo",
        "Categories": "Sports Analytics",
        "Tags": "live-stream;rtmp"
    },
    {
        "Tutorial Title": "Translate a Document in Google Docs",
        "Article Link": "https://support.google.com/docs/answer/10710316",
        "Video": "https://www.youtube.com/watch?v=QW5rdTqtC60",
        "Categories": "Word Processing",
        "Tags": "translate;multilingual"
    },
    {
        "Tutorial Title": "Version History & Restore",
        "Article Link": "https://support.google.com/docs/answer/190843",
        "Video": "https://www.youtube.com/watch?v=CdiJ5CZxtTE",
        "Categories": "Word Processing",
        "Tags": "version-history;restore"
    },
    {
        "Tutorial Title": "Split Text to Columns",
        "Article Link": "https://support.google.com/docs/answer/3094137",
        "Video": "https://www.youtube.com/watch?v=2_LgY8bYZc4",
        "Categories": "Spreadsheets",
        "Tags": "split-text;data-cleanup"
    },
    {
        "Tutorial Title": "Use XLOOKUP for Two-Way Lookups",
        "Article Link": "https://support.microsoft.com/en-us/office/xlookup-function",
        "Video": "https://www.youtube.com/watch?v=trn56zlrnY4",
        "Categories": "Spreadsheets",
        "Tags": "xlookup;lookup"
    },
    {
        "Tutorial Title": "Install & Configure the Yoast SEO Plugin",
        "Article Link": "https://yoast.com/help/wordpress-seo/",
        "Video": "https://www.youtube.com/watch?v=VA5s9GhDILI",
        "Categories": "Web CMS",
        "Tags": "seo;yoast"
    },
    {
        "Tutorial Title": "Build Conditional \u201cPaths\u201d in Zaps",
        "Article Link": "https://zapier.com/apps/paths/help",
        "Video": "https://www.youtube.com/watch?v=aeQCNEMXjEQ",
        "Categories": "Automation",
        "Tags": "paths;conditional-logic"
    },
    {
        "Tutorial Title": "Master Auto Layout",
        "Article Link": "https://www.figma.com/resources/learn-design/auto-layout/",
        "Video": "https://www.youtube.com/watch?v=gyMwXuJLB6w",
        "Categories": "UI/UX Design",
        "Tags": "auto-layout;responsive-design"
    },
    {
        "Tutorial Title": "Create Automated Workflows in HubSpot",
        "Article Link": "https://knowledge.hubspot.com/workflows/create-and-manage-workflows",
        "Video": "https://www.youtube.com/watch?v=ZjzXIQK-KmY",
        "Categories": "CRM",
        "Tags": "workflows;automation"
    },
    {
        "Tutorial Title": "Set Up Mailchimp Customer Journeys",
        "Article Link": "https://mailchimp.com/features/customer-journeys/",
        "Video": "https://www.youtube.com/watch?v=5jItbM8RyfM",
        "Categories": "Email Marketing",
        "Tags": "customer-journeys;automation"
    },
    {
        "Tutorial Title": "Add Site Tracking to ActiveCampaign",
        "Article Link": "https://help.activecampaign.com/hc/en-us/articles/360003730494-Get-your-site-tracking-code",
        "Video": "https://www.youtube.com/watch?v=PS8q4pVXWWM",
        "Categories": "Email Marketing",
        "Tags": "site-tracking;personalization"
    },
    {
        "Tutorial Title": "Schedule Bulk Posts via CSV Upload",
        "Article Link": "https://help.hootsuite.com/hc/en-us/articles/204598240",
        "Video": "https://www.youtube.com/watch?v=M6vGq1eFqK4",
        "Categories": "Social Scheduling",
        "Tags": "bulk-scheduling;csv-upload"
    },
    {
        "Tutorial Title": "Create Images with Buffer\u2019s Pablo Tool",
        "Article Link": "https://buffer.com/library/pablo",
        "Video": "https://www.youtube.com/watch?v=5GPjRnusNbY",
        "Categories": "Social Scheduling",
        "Tags": "pablo;image-design"
    },
    {
        "Tutorial Title": "Add & Use Blocks (Apps) in Airtable",
        "Article Link": "https://support.airtable.com/hc/en-us/articles/115013940188-Using-apps",
        "Video": "https://www.youtube.com/watch?v=c4e4W-Er8rI",
        "Categories": "Database",
        "Tags": "blocks;apps"
    },
    {
        "Tutorial Title": "Send Automated Due-Date Alerts via Slack",
        "Article Link": "https://asana.com/guide/help/api/slack",
        "Video": "https://www.youtube.com/watch?v=xoEUI2r6_K0",
        "Categories": "Project Management",
        "Tags": "slack-integration;notifications"
    },
    {
        "Tutorial Title": "How to Edit a Cinematic Video in CapCut [With AI]",
        "Article Link": "https://www.capcut.com/en-US/tutorials/cinematic-editing",
        "Video": "https://www.youtube.com/watch?v=5QUSuMPD95k",
        "Categories": "Video Editing",
        "Tags": "cinematic;capcut;ai-editing"
    },
    {
        "Tutorial Title": "16 Canva Shortcuts You MUST Know",
        "Article Link": "https://www.canva.com/learn/keyboard-shortcuts/",
        "Video": "https://www.youtube.com/watch?v=0E_lZPwnJ7I&pp=ygUOdHV0b3JpYWwgY2xpcHM%3D",
        "Categories": "Graphic Design",
        "Tags": "keyboard-shortcuts;canva;efficiency"
    },
    {
        "Tutorial Title": "HOW TO MAKE an ANIMATION in Procreate",
        "Article Link": "https://folio.procreate.art/handbook/animationassist",
        "Video": "https://www.youtube.com/shorts/LPPVo8qzqZs",
        "Categories": "Illustration",
        "Tags": "animation;procreate;shorts"
    },
    {
        "Tutorial Title": "How To Create Viral AI Animated Music Videos With AI Tools",
        "Article Link": "https://www.kapwing.com/resources/ai-music-video/",
        "Video": "https://www.youtube.com/watch?v=yN9pwetBdnE&pp=ygUOdHV0b3JpYWwgY2xpcHM%3D",
        "Categories": "AI Video Creation",
        "Tags": "ai-video;music-video;animation"
    },
    {
        "Tutorial Title": "How To Make a YouTube Clip",
        "Article Link": "https://support.google.com/youtube/answer/9884572",
        "Video": "https://www.youtube.com/shorts/XP9_7ciIfDk",
        "Categories": "Video Platform",
        "Tags": "youtube;clips;shorts"
    },
    {
        "Tutorial Title": "How to use Microsoft\u2019s FREE Video Editor \u2013 Clipchamp",
        "Article Link": "https://clipchamp.com/en/resources/edit-video/",
        "Video": "https://www.youtube.com/watch?v=Kf_14bvASxY&pp=ygUOdHV0b3JpYWwgY2xpcHM%3D",
        "Categories": "Video Editing",
        "Tags": "clipchamp;video-editing;free-editor"
    },
    {
        "Tutorial Title": "My SIMPLE process for writing short-form video scripts",
        "Article Link": "https://www.descript.com/blog/article/how-to-write-a-video-script-like-a-pro",
        "Video": "https://www.youtube.com/shorts/HpSuY4fd6wc",
        "Categories": "Content Creation",
        "Tags": "scriptwriting;video-scripting;short-form"
    },
    {
        "Tutorial Title": "Optimize Your Bio In 7 Simple Steps",
        "Article Link": "https://blog.hubspot.com/marketing/linkedin-profile-tips",
        "Video": "https://www.youtube.com/watch?v=E23Tuz9h8xo",
        "Categories": "Social Media",
        "Tags": "linkedin;profile-optimization;bio"
    },
    {
        "Tutorial Title": "What Is Copywriting? The NEW Definition You Need To Know In 2025",
        "Article Link": "https://blog.hubspot.com/marketing/copywriting-definition",
        "Video": "https://www.youtube.com/watch?v=AeTYpSDIT4Q&pp=0gcJCcMJAYcqIYzv",
        "Categories": "Writing & Marketing",
        "Tags": "copywriting;marketing;writing"
    },
    {
        "Tutorial Title": "Build Your First WordPress Website in Minutes with AI Magic!",
        "Article Link": "https://wordpress.org/support/article/new-to-wordpress-where-to-start/",
        "Video": "https://www.youtube.com/watch?v=nSbZEpzWv2c",
        "Categories": "Web CMS",
        "Tags": "wordpress;website-setup;ai"
    },
    {
        "Tutorial Title": "Create Children's Stories with AI! How to Use ReadKidz for Books",
        "Article Link": "https://www.readkidz.com/library/tutorials",
        "Video": "https://www.youtube.com/watch?v=zbVVr7YjSnk&pp=0gcJCcMJAYcqIYzv",
        "Categories": "AI Publishing",
        "Tags": "storytelling;ai;education"
    },
    {
        "Tutorial Title": "Top 10 Cinematic Shots For Beginners",
        "Article Link": "https://blog.audiosocket.com/filmmaking/top-10-cinematic-shots-for-beginners/",
        "Video": "https://www.youtube.com/watch?v=y7si6iAo0Vo",
        "Categories": "Videography",
        "Tags": "shots, cinematography, filmmaking basics"
    },
    {
        "Tutorial Title": "How to Use the Hook Model to Make Your Content Irresistible",
        "Article Link": "https://www.animalz.co/blog/content-hook-model/",
        "Video": "https://www.youtube.com/watch?v=LmXpbP7dD48",
        "Categories": "Copywriting",
        "Tags": "hooks, engagement, content strategy"
    },
    {
        "Tutorial Title": "10 Instagram Reels and TikTok Ideas for Artists with Examples",
        "Article Link": "https://samrodriguezart.com/blog/2022/12/30/10-instagram-reels-and-tiktok-ideas-for-artists-with-examples",
        "Video": "https://www.youtube.com/watch?v=EDS9sJFFBS8",
        "Categories": "Social Media",
        "Tags": "instagram reels, tiktok, artist workflow"
    },
    {
        "Tutorial Title": "Clips User Guide",
        "Article Link": "https://support.apple.com/guide/clips/welcome/ios",
        "Video": "https://www.youtube.com/watch?v=c9SBAW2hngk",
        "Categories": "Mobile Video Editing",
        "Tags": "clips, mobile editing, apple"
    },
    {
        "Tutorial Title": "Clipchamp Video Editing Tutorial: FREE Windows 11 Video Editor",
        "Article Link": "https://clipchamp.com/en/resources/edit-video/",
        "Video": "https://www.youtube.com/watch?v=AMH38LNONoU",
        "Categories": "Video Editing",
        "Tags": "clipchamp, windows editor, free tools"
    },
    {
        "Tutorial Title": "Video \u2013 Midjourney",
        "Article Link": "https://docs.midjourney.com/hc/en-us/articles/37460773864589-Video",
        "Video": "https://www.youtube.com/watch?v=sQ1jII2-oTM",
        "Categories": "AI Video Generation",
        "Tags": "midjourney, ai video, tutorial"
    },
    {
        "Tutorial Title": "6 Essential Tips for Shooting Smooth Handheld Vlogs",
        "Article Link": "https://www.ulanzi.com/blogs/news/handheld-vlogging-tips-guide",
        "Video": "https://www.youtube.com/watch?v=U4KIOGS9Xj0",
        "Categories": "Equipment",
        "Tags": "Ulanzi, tripod, vlogging"
    },
    {
        "Tutorial Title": "How to Tell Imaginative Stories to Captivate Your Target Audience",
        "Article Link": "https://blog.hubspot.com/marketing/storytelling",
        "Video": "https://www.youtube.com/watch?v=MP49IrjvwBY",
        "Categories": "Content Creation",
        "Tags": "storytelling, marketing, audience engagement"
    },
    {
        "Tutorial Title": "How to Make YouTube Thumbnails: the Ultimate Guide for 2025",
        "Article Link": "https://podcastle.ai/blog/how-to-make-youtube-thumbnails/",
        "Video": "https://www.youtube.com/watch?v=Iqy644uOOqM",
        "Categories": "Graphic Design",
        "Tags": "youtube, thumbnails, design"
    },
    {
        "Tutorial Title": "Social Media Marketing Mastery: How to Turn Likes into Loyal Customers",
        "Article Link": "https://blog.hubspot.com/marketing/social-media-marketing",
        "Video": "https://www.youtube.com/watch?v=u7Sb-GIdBqw",
        "Categories": "Marketing",
        "Tags": "social media, marketing strategies, growth hacks"
    },
    {
        "Tutorial Title": "The Art of Public Speaking: Mastering the Skills to Speak and Improve",
        "Article Link": "https://saspod.com/blog/post/the-art-of-public-speaking",
        "Video": "https://www.youtube.com/watch?v=35SPFdc1eXY",
        "Categories": "Communication",
        "Tags": "public speaking, communication, presentation skills"
    },
    {
        "Tutorial Title": "How to Create a Custom AI Chatbot with Zapier Chatbots",
        "Article Link": "https://zapier.com/blog/create-custom-ai-chatbots-with-interfaces/",
        "Video": "https://www.youtube.com/watch?v=g9aYdAat3hY",
        "Categories": "Automation",
        "Tags": "zapier, chatbots, ai automation"
    },
    {
        "Tutorial Title": "How to build a ChatGPT Slack bot with Zapier",
        "Article Link": "https://zapier.com/blog/how-to-build-chatgpt-slack-bot/",
        "Video": "https://www.youtube.com/watch?v=ScwvR6REOqI",
        "Categories": "Integration",
        "Tags": "slack, chatgpt, zapier integration"
    },
    {
        "Tutorial Title": "These Are the Only Shots You Will Ever Need",
        "Article Link": "https://blog.audiosocket.com/filmmaking/top-10-cinematic-shots-for-beginners/ (blog.audiosocket.com)",
        "Video": "https://www.youtube.com/watch?v=y7si6iAo0Vo&pp=ygUOdHV0b3JpYWwgY2xpcHM%3D (youtube.com)",
        "Categories": "Videography",
        "Tags": "shots;cinematic;filmmaking"
    },
    {
        "Tutorial Title": "How to Craft Magnetic Copywriting Hooks",
        "Article Link": "https://www.animalz.co/blog/content-hook-model/ (animalz.co)",
        "Video": "https://www.youtube.com/watch?v=LmXpbP7dD48&pp=ygUOdHV0b3JpYWwgY2xpcHM%3D (youtube.com)",
        "Categories": "Content Writing",
        "Tags": "copywriting;hooks;content-marketing"
    },
    {
        "Tutorial Title": "How I Make Aesthetic Instagram Reels & TikToks as an Artist!",
        "Article Link": "https://later.com/blog/instagram-aesthetic/ (later.com)",
        "Video": "https://www.youtube.com/watch?v=EDS9sJFFBS8&pp=ygUOdHV0b3JpYWwgY2xpcHM%3D (youtube.com)",
        "Categories": "Social Media Marketing",
        "Tags": "instagram-reels;aesthetic;social-media"
    },
    {
        "Tutorial Title": "Show What You\u2019ve Learned With Apple Clips - 2018 Tutorial",
        "Article Link": "https://support.apple.com/en-ca/guide/clips/welcome/ios (support.apple.com)",
        "Video": "https://www.youtube.com/watch?v=c9SBAW2hngk&pp=ygUOdHV0b3JpYWwgY2xpcHM%3D (youtube.com)",
        "Categories": "Mobile Video Editing",
        "Tags": "clips;mobile-editing;apple"
    },
    {
        "Tutorial Title": "Clipchamp Video Editing Tutorial: FREE Windows 11 Editor",
        "Article Link": "https://help.clipchamp.com/en/articles/1508549-how-do-i-edit-a-video-in-clipchamp (help.clipchamp.com)",
        "Video": "https://www.youtube.com/watch?v=AMH38LNONoU&pp=ygUOdHV0b3JpYWwgY2xpcHM%3D (youtube.com)",
        "Categories": "Video Editing",
        "Tags": "clipchamp;video-editing;windows"
    },
    {
        "Tutorial Title": "Midjourney Video Is FINALLY Here! (And It Is INSANE)",
        "Article Link": "https://docs.midjourney.com/hc/en-us/articles/37460773864589-Video (docs.midjourney.com)",
        "Video": "https://www.youtube.com/watch?v=sQ1jII2-oTM&t=61s&pp=ygUOdHV0b3JpYWwgY2xpcHM%3D (youtube.com)",
        "Categories": "AI Video Generation",
        "Tags": "midjourney;ai-video;generative-ai"
    },
    {
        "Tutorial Title": "These 3 Things Will Improve Your Travel Films ft. Ulanzi TT38",
        "Article Link": "https://www.ulanzi.com/blogs/news/handheld-vlogging-tips-guide (ulanzi.com)",
        "Video": "https://www.youtube.com/watch?v=U4KIOGS9Xj0 (youtube.com)",
        "Categories": "Vlogging Accessories",
        "Tags": "tripod;vlogging;travel"
    },
    {
        "Tutorial Title": "An Easy Way of Storytelling",
        "Article Link": "https://blog.hubspot.com/marketing/storytelling (blog.hubspot.com)",
        "Video": "https://www.youtube.com/watch?v=MP49IrjvwBY (youtube.com)",
        "Categories": "Content Strategy",
        "Tags": "storytelling;content-strategy;marketing"
    },
    {
        "Tutorial Title": "How to Create Irresistible Thumbnails (and Blow Up Your Content)",
        "Article Link": "https://blog.hubspot.com/marketing/youtube-thumbnail (blog.hubspot.com)",
        "Video": "https://www.youtube.com/watch?v=Iqy644uOOqM (youtube.com)",
        "Categories": "Design",
        "Tags": "youtube-thumbnails;design;thumbnail-tips"
    },
    {
        "Tutorial Title": "44 Tricks To Instantly Get More Views on Social Media",
        "Article Link": "https://galaxy.ai/youtube-summarizer/44-tricks-to-instantly-get-more-views-on-social-media-u7Sb-GIdBqw (galaxy.ai)",
        "Video": "https://www.youtube.com/watch?v=u7Sb-GIdBqw (youtube.com)",
        "Categories": "Social Media Marketing",
        "Tags": "social-media;growth;hacks"
    },
    {
        "Tutorial Title": "Windows Desktop App Demo",
        "Article Link": "https://support.toggl.com/en/articles/6176883-toggl-track-desktop-app-for-windows (support.toggl.com)",
        "Video": "https://youtu.be/dMKByKJbB2E?si=1CvEs1_tQhPslBAL",
        "Categories": "Productivity",
        "Tags": "time-tracking, productivity, desktop-app"
    },
    {
        "Tutorial Title": "Product Demo",
        "Article Link": "https://support.toggl.com/en/collections/1461327-introduction-to-toggl-track (support.toggl.com)",
        "Video": "https://youtu.be/e_SKyiGgilg?si=6sUgnQqfD0j4Mbtz",
        "Categories": "Productivity",
        "Tags": "time-tracking, productivity, reporting"
    },
    {
        "Tutorial Title": "How To Set Up Native Salesforce Integration",
        "Article Link": "https://support.toggl.com/en/articles/5391572-salesforce-sync (support.toggl.com)",
        "Video": "https://youtu.be/cnmkueKUGrA?si=19lWMO5pISAdBEFa",
        "Categories": "Productivity",
        "Tags": "toggl, salesforce, integration, time-tracking"
    },
    {
        "Tutorial Title": "Reports Demo \u2014 Popular reporting features in Toggl Track",
        "Article Link": "https://support.toggl.com/en/collections/1148692-analyzing-time-and-reporting (support.toggl.com)",
        "Video": "https://youtu.be/z3baHn8AKRo?si=uwK1O7SL7m2_12td",
        "Categories": "Productivity",
        "Tags": "reports, time-tracking, productivity"
    },
    {
        "Tutorial Title": "Start Time Entry from URL Demo",
        "Article Link": "https://support.toggl.com/en/articles/6368086-can-i-start-a-time-entry-with-a-url (support.toggl.com)",
        "Video": "https://youtu.be/yLxoHB4VO5U?si=4AloONDypcKiTJp_",
        "Categories": "Productivity",
        "Tags": "time-tracking, url-integration"
    },
    {
        "Tutorial Title": "Video unavailable",
        "Article Link": "https://support.toggl.com/en/articles/2206984-toggl-track-browser-extension (support.toggl.com)",
        "Video": "https://youtu.be/_xJ9ER2ZZBw?si=C-YBWgdIzXqWes8",
        "Categories": "Productivity",
        "Tags": "unknown"
    },
    {
        "Tutorial Title": "Reports Demo \u2014 Popular reporting features in Toggl Track",
        "Article Link": "https://support.toggl.com/en/collections/1148692-analyzing-time-and-reporting (support.toggl.com)",
        "Video": "https://youtu.be/1SYZyKQAjvE?si=1HvffEJfCPPCQfxo",
        "Categories": "Productivity",
        "Tags": "reports, productivity, time-tracking"
    },
    {
        "Tutorial Title": "Triggers",
        "Article Link": "https://help.gohighlevel.com/support/solutions/articles/48000982202-triggers-overview (help.gohighlevel.com)",
        "Video": "https://www.youtube.com/watch?v=R_cq7TPVWJg&list=PLUjgZhyQd8yXREQY0ujh_C8Ium33g2iyM",
        "Categories": "Website, Automation",
        "Tags": "triggers, workflows, automation"
    },
    {
        "Tutorial Title": "Zapier",
        "Article Link": "https://help.gohighlevel.com/support/solutions/articles/155000005109-connect-highlevel-sub-account-with-zapier",
        "Video": "https://www.youtube.com/watch?v=iRMTkTz1Xs0&list=PLUjgZhyQd8yXREQY0ujh_C8Ium33g2iyM&index=2",
        "Categories": "Website, Automation",
        "Tags": "zapier, integration, automation"
    },
    {
        "Tutorial Title": "Contact Flow",
        "Article Link": "https://help.gohighlevel.com/support/solutions/articles/48001157626-contact-flow",
        "Video": "https://www.youtube.com/watch?v=H-G8fijOzwo&list=PLUjgZhyQd8yXREQY0ujh_C8Ium33g2iyM&index=3",
        "Categories": "Website, Automation",
        "Tags": "contact-flow, workflows, automation"
    },
    {
        "Tutorial Title": "How to Cancel SaaS Sub-Accounts for Client",
        "Article Link": "https://help.gohighlevel.com/support/solutions/articles/48001216453-how-to-cancel-saas-sub-account-for-your-client",
        "Video": "https://www.youtube.com/watch?v=c-IVH1nCIlE&list=PLUjgZhyQd8yXj1sWPGqnUuG4y5pvciWIB&index=1",
        "Categories": "Website, Automation",
        "Tags": "saas, sub-accounts, billing"
    },
    {
        "Tutorial Title": "Guide to Direct Payment Integration with Mobile Estimates",
        "Article Link": "https://help.gohighlevel.com/support/solutions/articles/155000005617-how-to-use-direct-payments-in-estimates-in-the-mobile-app",
        "Video": "https://www.youtube.com/watch?v=blWyBKLaJwQ&list=PLUjgZhyQd8yXj1sWPGqnUuG4y5pvciWIB&index=2",
        "Categories": "Website, Automation",
        "Tags": "mobile, payments, estimates"
    },
    {
        "Tutorial Title": "Streamline Your Tasks: A How-To Guide for the Updated Task Manager",
        "Article Link": "https://help.gohighlevel.com/support/solutions/articles/155000005529-unified-task-management-across-contacts-and-opportunities",
        "Video": "https://youtu.be/oYnIUeIhPUg?si=GtC1LUmM79T9_72P",
        "Categories": "Website, Automation",
        "Tags": "tasks, management, productivity"
    },
    {
        "Tutorial Title": "SMS Messaging Ramp: A Step-by-Step Guide",
        "Article Link": "https://help.gohighlevel.com/support/solutions/articles/155000005572-messaging-ramp-progress-card",
        "Video": "https://youtu.be/HHu9qI29Ays?si=CgY1boSNJEAcs_mC",
        "Categories": "Website, Automation",
        "Tags": "sms, messaging, ramp-up"
    },
    {
        "Tutorial Title": "How to Resend Unopened Emails Using RSS and Batch Scheduling",
        "Article Link": "https://help.gohighlevel.com/support/solutions/articles/155000005570-resend-to-unopened-for-rss-and-batch-scheduled-emails",
        "Video": "https://youtu.be/UP93A7GT0hI?si=lrjn7ZJ-cCi58RP5",
        "Categories": "Website, Automation",
        "Tags": "rss, email-marketing, automation"
    },
    {
        "Tutorial Title": "How to Activate a 30-Day Free WhatsApp Trial with HighLevel",
        "Article Link": "https://help.gohighlevel.com/support/solutions/articles/155000005420-whatsapp-30-days-free-subscription-trial-promotion",
        "Video": "https://youtu.be/pTiyZwBlZpg?si=DeuKh_cN3rWr0p_P",
        "Categories": "Website, Automation",
        "Tags": "whatsapp, trial, integration"
    },
    {
        "Tutorial Title": "How to Automate Tagging in Email Campaigns",
        "Article Link": "https://help.gohighlevel.com/support/solutions/articles/155000004425-how-to-automate-tagging-based-on-email-campaign-interactions",
        "Video": "https://youtu.be/T0zBdvpdPo8?si=r8M8AZ9PnCVKHls_",
        "Categories": "Website, Automation",
        "Tags": "tags, email, automation"
    },
    {
        "Tutorial Title": "How to Manage SaaS Subscription Upgrades and Downgrades",
        "Article Link": "https://help.gohighlevel.com/support/solutions/articles/155000001979-upgrading-and-cancelling-saas-plans-for-clients",
        "Video": "https://youtu.be/BVw4v5bF-U0?si=TEaxXDy8XPLQQUfC",
        "Categories": "Website, Automation",
        "Tags": "saas, subscription, billing, upgrades"
    },
    {
        "Tutorial Title": "How To Add Product Categories In Shopify 2025 (For Beginners)",
        "Article Link": "https://help.shopify.com/en/manual/products/details/product-type (help.shopify.com)",
        "Video": "https://www.youtube.com/watch?v=L1j78aWjF3w",
        "Categories": "E-commerce, Website",
        "Tags": "product-types, categories, taxonomy"
    },
    {
        "Tutorial Title": "How To Organize Products In Your Shopify Store",
        "Article Link": "https://help.shopify.com/en/manual/products (help.shopify.com)",
        "Video": "https://www.youtube.com/watch?v=_fNPHKuSxag",
        "Categories": "E-commerce, Website",
        "Tags": "products, organization, catalog"
    },
    {
        "Tutorial Title": "How To Create Collections on Shopify Store \u2013 Online Store",
        "Article Link": "https://help.shopify.com/en/manual/products/collections (help.shopify.com)",
        "Video": "https://www.youtube.com/watch?v=r8k4IKyxyZc",
        "Categories": "E-commerce, Website",
        "Tags": "collections, smart-collections, manual-collections"
    },
    {
        "Tutorial Title": "Shopify Shipping Tutorial: Set Up Shipping Rates & Portfolios",
        "Article Link": "https://help.shopify.com/en/manual/fulfillment/setup/shipping-rates (help.shopify.com)",
        "Video": "https://www.youtube.com/watch?v=gkPnQngCLNA",
        "Categories": "E-commerce, Website",
        "Tags": "shipping, rates, fulfillment"
    },
    {
        "Tutorial Title": "How To Build a Shopify Store: Shipping and Fulfillment",
        "Article Link": "https://help.shopify.com/en/manual/fulfillment/setup (help.shopify.com)",
        "Video": "https://www.youtube.com/watch?v=X6hBF5bnnto",
        "Categories": "E-commerce, Website",
        "Tags": "fulfillment, shipping, setup"
    },
    {
        "Tutorial Title": "How to restore deleted content in Canva?",
        "Article Link": "https://www.canva.com/help/article/where-are-my-deleted-designs",
        "Video": "https://www.youtube.com/watch?v=QtTqLMaV1xA&list=PLmL-TRKY9xWijf8w4t7GncSuQW3ll3rh9&index=1&pp=iAQB",
        "Categories": "Design & Graphics",
        "Tags": "restore, deleted-content, Canva"
    },
    {
        "Tutorial Title": "How to make canvas transparent in Paint 3D?",
        "Article Link": "https://www.lifewire.com/create-3d-drawing-microsoft-paint-3d-4151873",
        "Video": "https://www.youtube.com/watch?v=Mu24eO45-b8&list=PLmL-TRKY9xWijf8w4t7GncSuQW3ll3rh9&index=2&pp=iAQB",
        "Categories": "Design & Graphics",
        "Tags": "paint-3d, transparency, graphics"
    },
    {
        "Tutorial Title": "How do you make a trifold brochure in Canva?",
        "Article Link": "https://www.canva.com/learn/trifold-brochures",
        "Video": "https://www.youtube.com/watch?v=z7-gxL0uTe4&list=PLmL-TRKY9xWijf8w4t7GncSuQW3ll3rh9&index=3&pp=iAQB0gcJCcMJAYcqIYzv",
        "Categories": "Design & Graphics",
        "Tags": "trifold, brochures, Canva"
    },
    {
        "Tutorial Title": "How to make a professional resume with Canva",
        "Article Link": "https://www.canva.com/create/resumes",
        "Video": "https://www.youtube.com/watch?v=VYHtTMU5VsM&list=PLmL-TRKY9xWijf8w4t7GncSuQW3ll3rh9&index=4&pp=iAQB",
        "Categories": "Design & Graphics",
        "Tags": "resume, templates, career"
    },
    {
        "Tutorial Title": "How to use Google Slides",
        "Article Link": "https://support.google.com/docs/answer/6282736?hl=en",
        "Video": "https://youtu.be/7vSnesQDLBE?si=R3bwbCyIAlIj1sZM",
        "Categories": "Productivity & Presentation",
        "Tags": "presentations, collaboration, Google"
    },
    {
        "Tutorial Title": "How to connect Shopify to Facebook Shop (Integration & Setup Tutorial)",
        "Article Link": "https://help.shopify.com/en/manual/online-sales-channels/facebook-instagram",
        "Video": "https://www.youtube.com/watch?v=x20_7LB6VRw",
        "Categories": "E-commerce & Social Media",
        "Tags": "Shopify, Facebook-Shop, integration"
    },
    {
        "Tutorial Title": "Pollo AI Quickstart: How to use Pollo AI for beginners",
        "Article Link": "https://docs.pollo.ai/docs/quick-start",
        "Video": "https://www.youtube.com/watch?v=zOMLoG6r65Q",
        "Categories": "AI & Video Generation",
        "Tags": "Pollo AI, video-generation, quickstart"
    },
    {
        "Tutorial Title": "Pollo AI Tutorial & Review: How to use Pollo AI for beginners (2025)",
        "Article Link": "https://docs.pollo.ai/docs/quick-start",
        "Video": "https://www.youtube.com/watch?v=fi2KwlOxcks&list=PLdTfdv66XKX4M-UYs_-gc-vv0E9faPKkY",
        "Categories": "AI & Video Generation",
        "Tags": "Pollo AI, tutorial, review"
    },
    {
        "Tutorial Title": "How to use PowerPoint \u2014 PowerPoint tutorial in 2025",
        "Article Link": "https://support.microsoft.com/office/powerpoint-for-windows-training-40e8c930-cb0b-40d8-82c4-bd53d3398787",
        "Video": "https://www.youtube.com/watch?v=WXmYKsBFb6g&list=PLdTfdv66XKX6UCgfUTH22-UGG_zvvfOtt",
        "Categories": "Productivity & Presentation",
        "Tags": "PowerPoint, slides, training"
    },
    {
        "Tutorial Title": "Reclaim AI tutorial 2025: How to use Reclaim.ai (for beginners)",
        "Article Link": "https://help.reclaim.ai/en/articles/5224992-getting-started-with-reclaim",
        "Video": "https://www.youtube.com/watch?v=8KmSXDuispE&list=PLdTfdv66XKX4eJo8FnA-6cc06Mzw87ChJ",
        "Categories": "Productivity & Time Management",
        "Tags": "scheduling, calendar, productivity"
    },
    {
        "Tutorial Title": "LM Studio tutorial: How to run large language models (LLM)",
        "Article Link": "https://lmstudio.ai/docs/getting-started",
        "Video": "https://www.youtube.com/watch?v=34283Fj1S54&list=PLdTfdv66XKX6zCLgWdTd0UjxIqK9fxgzE",
        "Categories": "AI Tools & Development",
        "Tags": "LLM, local-AI, LM-Studio"
    },
    {
        "Tutorial Title": "How to add signature in Outlook 2025 (step-by-step)",
        "Article Link": "https://support.microsoft.com/office/create-and-add-an-email-signature-in-outlook-com-or-outlook-on-the-web-776d9006-abdf-444e-b5b7-a61821dff034",
        "Video": "https://www.youtube.com/watch?v=i2vVfzbpvos&list=PLdTfdv66XKX5uKa1N2DM36FfeLFL1Keb6",
        "Categories": "Email & Productivity",
        "Tags": "Outlook, signature, email"
    },
    {
        "Tutorial Title": "How to fulfill orders on Shopify 2025 (for beginners)",
        "Article Link": "https://help.shopify.com/en/manual/orders/fulfilling-orders",
        "Video": "https://www.youtube.com/watch?v=19Kh8CntfA8",
        "Categories": "E-commerce & Fulfillment",
        "Tags": "order-fulfillment, shipping, Shopify"
    }
]

# Active sessions for real-time sync
active_sessions = {}

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_user_by_id(user_id):
    return next((user for user in users_db if user['id'] == user_id and user.get('is_active', True)), None)

def get_user_by_email(email):
    return next((user for user in users_db if user['email'] == email and user.get('is_active', True)), None)

def generate_password():
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# Root endpoint
@app.route('/')
def hello():
    return jsonify({
        "message": "Turma Digital Agency Backend API",
        "status": "running",
        "version": "2.0.0"
    })

# API health check
@app.route('/api')
def api_root():
    return jsonify({
        "message": "Turma Digital Agency Backend API",
        "status": "running",
        "endpoints": [
            "/api/auth/login",
            "/api/auth/verify",
            "/api/admin/employees",
            "/api/admin/time-records",
            "/api/admin/eod-reports",
            "/api/employee/clock-in",
            "/api/employee/clock-out",
            "/api/employee/eod-report",
            "/api/announcements",
            "/api/training/materials",
            "/api/requests/leave",
            "/api/requests/salary-loan",
            "/api/requests/time-adjustment",
            "/api/admin/users/create",
            "/api/admin/users/update",
            "/api/admin/users/regenerate-password",
            "/api/admin/export/time-records",
            "/api/admin/export/eod-reports",
            "/api/system/health"
        ]
    })

# System health endpoint
@app.route('/api/system/health')
def system_health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected",
        "api": "operational",
        "active_sessions": len(active_sessions)
    })

# Authentication endpoints
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required"}), 400
    
    user = get_user_by_email(email)
    if not user:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if user['password'] != hashed_password:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401
    
    token = generate_token(user['id'])
    user_data = {k: v for k, v in user.items() if k != 'password'}
    
    # Track active session
    active_sessions[user['id']] = {
        "user_id": user['id'],
        "login_time": datetime.now().isoformat(),
        "last_activity": datetime.now().isoformat()
    }
    
    return jsonify({
        "success": True,
        "token": token,
        "user": user_data
    })

@app.route('/api/auth/verify', methods=['POST'])
def verify():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    # Update last activity
    if user_id in active_sessions:
        active_sessions[user_id]["last_activity"] = datetime.now().isoformat()
    
    user_data = {k: v for k, v in user.items() if k != 'password'}
    return jsonify({"success": True, "user": user_data})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if user_id and user_id in active_sessions:
        del active_sessions[user_id]
    
    return jsonify({"success": True, "message": "Logged out successfully"})

# Admin endpoints
@app.route('/api/admin/employees', methods=['GET'])
def get_employees():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user or user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    employees = [{k: v for k, v in emp.items() if k != 'password'} for emp in users_db if emp.get('is_active', True)]
    
    # Add active session info
    for emp in employees:
        emp['is_online'] = emp['id'] in active_sessions
        if emp['is_online']:
            emp['last_activity'] = active_sessions[emp['id']]['last_activity']
    
    return jsonify({"success": True, "employees": employees})

@app.route('/api/admin/time-records', methods=['GET'])
def get_time_records():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user or user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    # Enrich time records with employee names
    enriched_records = []
    for record in time_records_db:
        employee = get_user_by_id(record['employee_id'])
        if employee:
            enriched_record = record.copy()
            enriched_record['employee_name'] = employee['name']
            enriched_record['employee_email'] = employee['email']
            enriched_records.append(enriched_record)
    
    return jsonify({"success": True, "records": enriched_records})

@app.route('/api/admin/eod-reports', methods=['GET'])
def get_eod_reports():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user or user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    # Enrich EOD reports with employee names
    enriched_reports = []
    for report in eod_reports_db:
        employee = get_user_by_id(report['employee_id'])
        if employee:
            enriched_report = report.copy()
            enriched_report['employee_name'] = employee['name']
            enriched_report['employee_email'] = employee['email']
            enriched_reports.append(enriched_report)
    
    return jsonify({"success": True, "reports": enriched_reports})

# User Management Endpoints
@app.route('/api/admin/users/create', methods=['POST'])
def create_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user or user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    data = request.get_json()
    
    # Check if email already exists
    if get_user_by_email(data.get('email')):
        return jsonify({"success": False, "message": "Email already exists"}), 400
    
    # Generate password if not provided
    password = data.get('password', generate_password())
    
    new_user = {
        "id": max([u['id'] for u in users_db]) + 1,
        "name": data.get('name'),
        "email": data.get('email'),
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "role": data.get('role', 'employee'),
        "position": data.get('position', ''),
        "department": data.get('department', ''),
        "created_at": datetime.now().isoformat(),
        "is_active": True
    }
    
    users_db.append(new_user)
    
    # Return user data without password but include generated password for admin
    user_data = {k: v for k, v in new_user.items() if k != 'password'}
    user_data['generated_password'] = password
    
    return jsonify({"success": True, "user": user_data})

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    admin_user_id = verify_token(token)
    
    if not admin_user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    admin_user = get_user_by_id(admin_user_id)
    if not admin_user or admin_user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    target_user = get_user_by_id(user_id)
    if not target_user:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    data = request.get_json()
    
    # Update user fields
    if 'name' in data:
        target_user['name'] = data['name']
    if 'email' in data:
        # Check if new email already exists
        existing_user = get_user_by_email(data['email'])
        if existing_user and existing_user['id'] != user_id:
            return jsonify({"success": False, "message": "Email already exists"}), 400
        target_user['email'] = data['email']
    if 'position' in data:
        target_user['position'] = data['position']
    if 'department' in data:
        target_user['department'] = data['department']
    if 'role' in data:
        target_user['role'] = data['role']
    if 'is_active' in data:
        target_user['is_active'] = data['is_active']
    
    user_data = {k: v for k, v in target_user.items() if k != 'password'}
    return jsonify({"success": True, "user": user_data})

@app.route('/api/admin/users/<int:user_id>/regenerate-password', methods=['POST'])
def regenerate_password(user_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    admin_user_id = verify_token(token)
    
    if not admin_user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    admin_user = get_user_by_id(admin_user_id)
    if not admin_user or admin_user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    target_user = get_user_by_id(user_id)
    if not target_user:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    new_password = generate_password()
    target_user['password'] = hashlib.sha256(new_password.encode()).hexdigest()
    
    # Remove user from active sessions to force re-login
    if user_id in active_sessions:
        del active_sessions[user_id]
    
    return jsonify({"success": True, "new_password": new_password})

# Employee endpoints
@app.route('/api/employee/clock-in', methods=['POST'])
def clock_in():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    # Check if already clocked in today
    today = datetime.now().strftime('%Y-%m-%d')
    existing_record = next((record for record in time_records_db 
                          if record['employee_id'] == user_id and record['date'] == today), None)
    
    if existing_record and not existing_record.get('clock_out'):
        return jsonify({"success": False, "message": "Already clocked in today"}), 400
    
    time_record = {
        "id": len(time_records_db) + 1,
        "employee_id": user_id,
        "date": today,
        "clock_in": datetime.now().isoformat(),
        "clock_out": None
    }
    
    time_records_db.append(time_record)
    return jsonify({"success": True, "message": "Clocked in successfully", "record": time_record})

@app.route('/api/employee/clock-out', methods=['POST'])
def clock_out():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    today = datetime.now().strftime('%Y-%m-%d')
    record = next((record for record in time_records_db 
                  if record['employee_id'] == user_id and record['date'] == today), None)
    
    if not record:
        return jsonify({"success": False, "message": "No clock-in record found for today"}), 400
    
    if record.get('clock_out'):
        return jsonify({"success": False, "message": "Already clocked out today"}), 400
    
    record['clock_out'] = datetime.now().isoformat()
    return jsonify({"success": True, "message": "Clocked out successfully", "record": record})

@app.route('/api/employee/eod-report', methods=['POST'])
def submit_eod_report():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    data = request.get_json()
    
    eod_report = {
        "id": len(eod_reports_db) + 1,
        "employee_id": user_id,
        "date": datetime.now().strftime('%Y-%m-%d'),
        "tasks_completed": data.get('tasks_completed', ''),
        "challenges": data.get('challenges', ''),
        "tomorrow_plan": data.get('tomorrow_plan', ''),
        "submitted_at": datetime.now().isoformat()
    }
    
    eod_reports_db.append(eod_report)
    return jsonify({"success": True, "message": "EOD report submitted successfully", "report": eod_report})

# Announcements endpoints
@app.route('/api/announcements', methods=['GET'])
def get_announcements():
    # Sort announcements by date (newest first)
    sorted_announcements = sorted(announcements_db, key=lambda x: x['created_at'], reverse=True)
    return jsonify({"success": True, "announcements": sorted_announcements})

@app.route('/api/announcements', methods=['POST'])
def create_announcement():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user or user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    data = request.get_json()
    
    announcement = {
        "id": len(announcements_db) + 1,
        "title": data.get('title'),
        "content": data.get('content'),
        "priority": data.get('priority', 'normal'),
        "date": datetime.now().strftime('%Y-%m-%d'),
        "created_by": user_id,
        "created_at": datetime.now().isoformat()
    }
    
    announcements_db.append(announcement)
    return jsonify({"success": True, "announcement": announcement})

# Request Management Endpoints

# Leave Requests
@app.route('/api/requests/leave', methods=['GET'])
def get_leave_requests():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    if user['role'] == 'admin':
        # Admin sees all requests with employee names
        enriched_requests = []
        for req in leave_requests_db:
            employee = get_user_by_id(req['employee_id'])
            if employee:
                enriched_req = req.copy()
                enriched_req['employee_name'] = employee['name']
                enriched_req['employee_email'] = employee['email']
                enriched_requests.append(enriched_req)
        return jsonify({"success": True, "requests": enriched_requests})
    else:
        # Employee sees only their requests
        user_requests = [req for req in leave_requests_db if req['employee_id'] == user_id]
        return jsonify({"success": True, "requests": user_requests})

@app.route('/api/requests/leave', methods=['POST'])
def create_leave_request():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    data = request.get_json()
    
    leave_request = {
        "id": len(leave_requests_db) + 1,
        "employee_id": user_id,
        "leave_type": data.get('leave_type'),
        "start_date": data.get('start_date'),
        "end_date": data.get('end_date'),
        "reason": data.get('reason'),
        "status": "pending",
        "requested_at": datetime.now().isoformat(),
        "approved_by": None,
        "approved_at": None
    }
    
    leave_requests_db.append(leave_request)
    return jsonify({"success": True, "request": leave_request})

@app.route('/api/requests/leave/<int:request_id>/approve', methods=['POST'])
def approve_leave_request(request_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user or user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    request_obj = next((req for req in leave_requests_db if req['id'] == request_id), None)
    if not request_obj:
        return jsonify({"success": False, "message": "Request not found"}), 404
    
    data = request.get_json()
    status = data.get('status', 'approved')  # approved or rejected
    
    request_obj['status'] = status
    request_obj['approved_by'] = user_id
    request_obj['approved_at'] = datetime.now().isoformat()
    if 'comments' in data:
        request_obj['admin_comments'] = data['comments']
    
    return jsonify({"success": True, "request": request_obj})

# Salary Loan Requests
@app.route('/api/requests/salary-loan', methods=['GET'])
def get_salary_loan_requests():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    if user['role'] == 'admin':
        # Admin sees all requests with employee names
        enriched_requests = []
        for req in salary_loan_requests_db:
            employee = get_user_by_id(req['employee_id'])
            if employee:
                enriched_req = req.copy()
                enriched_req['employee_name'] = employee['name']
                enriched_req['employee_email'] = employee['email']
                enriched_requests.append(enriched_req)
        return jsonify({"success": True, "requests": enriched_requests})
    else:
        # Employee sees only their requests
        user_requests = [req for req in salary_loan_requests_db if req['employee_id'] == user_id]
        return jsonify({"success": True, "requests": user_requests})

@app.route('/api/requests/salary-loan', methods=['POST'])
def create_salary_loan_request():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    data = request.get_json()
    amount = data.get('amount')
    
    # Validate amount
    if amount not in [5000, 10000, 15000]:
        return jsonify({"success": False, "message": "Invalid loan amount. Must be 5000, 10000, or 15000"}), 400
    
    salary_loan_request = {
        "id": len(salary_loan_requests_db) + 1,
        "employee_id": user_id,
        "amount": amount,
        "repayment_months": data.get('repayment_months', 6),
        "reason": data.get('reason'),
        "status": "pending",
        "requested_at": datetime.now().isoformat(),
        "approved_by": None,
        "approved_at": None
    }
    
    salary_loan_requests_db.append(salary_loan_request)
    return jsonify({"success": True, "request": salary_loan_request})

@app.route('/api/requests/salary-loan/<int:request_id>/approve', methods=['POST'])
def approve_salary_loan_request(request_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user or user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    request_obj = next((req for req in salary_loan_requests_db if req['id'] == request_id), None)
    if not request_obj:
        return jsonify({"success": False, "message": "Request not found"}), 404
    
    data = request.get_json()
    status = data.get('status', 'approved')  # approved or rejected
    
    request_obj['status'] = status
    request_obj['approved_by'] = user_id
    request_obj['approved_at'] = datetime.now().isoformat()
    if 'comments' in data:
        request_obj['admin_comments'] = data['comments']
    
    return jsonify({"success": True, "request": request_obj})

# Time Adjustment Requests
@app.route('/api/requests/time-adjustment', methods=['GET'])
def get_time_adjustment_requests():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    if user['role'] == 'admin':
        # Admin sees all requests with employee names
        enriched_requests = []
        for req in time_adjustment_requests_db:
            employee = get_user_by_id(req['employee_id'])
            if employee:
                enriched_req = req.copy()
                enriched_req['employee_name'] = employee['name']
                enriched_req['employee_email'] = employee['email']
                enriched_requests.append(enriched_req)
        return jsonify({"success": True, "requests": enriched_requests})
    else:
        # Employee sees only their requests
        user_requests = [req for req in time_adjustment_requests_db if req['employee_id'] == user_id]
        return jsonify({"success": True, "requests": user_requests})

@app.route('/api/requests/time-adjustment', methods=['POST'])
def create_time_adjustment_request():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    data = request.get_json()
    
    time_adjustment_request = {
        "id": len(time_adjustment_requests_db) + 1,
        "employee_id": user_id,
        "date": data.get('date'),
        "original_clock_in": data.get('original_clock_in'),
        "original_clock_out": data.get('original_clock_out'),
        "requested_clock_in": data.get('requested_clock_in'),
        "requested_clock_out": data.get('requested_clock_out'),
        "reason": data.get('reason'),
        "status": "pending",
        "requested_at": datetime.now().isoformat(),
        "approved_by": None,
        "approved_at": None
    }
    
    time_adjustment_requests_db.append(time_adjustment_request)
    return jsonify({"success": True, "request": time_adjustment_request})

@app.route('/api/requests/time-adjustment/<int:request_id>/approve', methods=['POST'])
def approve_time_adjustment_request(request_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user or user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    request_obj = next((req for req in time_adjustment_requests_db if req['id'] == request_id), None)
    if not request_obj:
        return jsonify({"success": False, "message": "Request not found"}), 404
    
    data = request.get_json()
    status = data.get('status', 'approved')  # approved or rejected
    
    request_obj['status'] = status
    request_obj['approved_by'] = user_id
    request_obj['approved_at'] = datetime.now().isoformat()
    if 'comments' in data:
        request_obj['admin_comments'] = data['comments']
    
    # If approved, update the actual time record
    if status == 'approved':
        time_record = next((record for record in time_records_db 
                          if record['employee_id'] == request_obj['employee_id'] 
                          and record['date'] == request_obj['date']), None)
        
        if time_record:
            if request_obj.get('requested_clock_in'):
                time_record['clock_in'] = request_obj['requested_clock_in']
            if request_obj.get('requested_clock_out'):
                time_record['clock_out'] = request_obj['requested_clock_out']
            time_record['adjusted'] = True
            time_record['adjusted_by'] = user_id
            time_record['adjusted_at'] = datetime.now().isoformat()
    
    return jsonify({"success": True, "request": request_obj})

# Training materials endpoints
@app.route('/api/training/materials', methods=['GET'])
def get_training_materials():
    return jsonify({"success": True, "materials": training_materials_db})

@app.route('/api/training/materials', methods=['POST'])
def add_training_material():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user or user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    data = request.get_json()
    
    training_material = {
        "id": len(training_materials_db) + 1,
        "Tutorial Title": data.get('title'),
        "Article Link": data.get('article_link'),
        "Video": data.get('video_link'),
        "Categories": data.get('category'),
        "Tags": data.get('tags'),
        "added_by": user_id,
        "added_at": datetime.now().isoformat()
    }
    
    training_materials_db.append(training_material)
    return jsonify({"success": True, "material": training_material})

# CSV Export Endpoints
@app.route('/api/admin/export/time-records', methods=['GET'])
def export_time_records():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user or user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    # Create CSV data
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Employee Name', 'Employee Email', 'Date', 'Clock In', 'Clock Out', 'Hours Worked', 'Adjusted'])
    
    # Write data
    for record in time_records_db:
        employee = get_user_by_id(record['employee_id'])
        if employee:
            hours_worked = ""
            if record.get('clock_in') and record.get('clock_out'):
                clock_in = datetime.fromisoformat(record['clock_in'])
                clock_out = datetime.fromisoformat(record['clock_out'])
                hours_worked = str(clock_out - clock_in)
            
            writer.writerow([
                employee['name'],
                employee['email'],
                record['date'],
                record.get('clock_in', ''),
                record.get('clock_out', ''),
                hours_worked,
                'Yes' if record.get('adjusted') else 'No'
            ])
    
    csv_data = output.getvalue()
    output.close()
    
    return jsonify({
        "success": True,
        "csv_data": csv_data,
        "filename": f"time_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    })

@app.route('/api/admin/export/eod-reports', methods=['GET'])
def export_eod_reports():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user or user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    # Create CSV data
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Employee Name', 'Employee Email', 'Date', 'Tasks Completed', 'Challenges', 'Tomorrow Plan', 'Submitted At'])
    
    # Write data
    for report in eod_reports_db:
        employee = get_user_by_id(report['employee_id'])
        if employee:
            writer.writerow([
                employee['name'],
                employee['email'],
                report['date'],
                report.get('tasks_completed', ''),
                report.get('challenges', ''),
                report.get('tomorrow_plan', ''),
                report.get('submitted_at', '')
            ])
    
    csv_data = output.getvalue()
    output.close()
    
    return jsonify({
        "success": True,
        "csv_data": csv_data,
        "filename": f"eod_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    })

# Real-time status endpoint
@app.route('/api/realtime/status', methods=['GET'])
def get_realtime_status():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    # Update last activity
    if user_id in active_sessions:
        active_sessions[user_id]["last_activity"] = datetime.now().isoformat()
    
    status_data = {
        "active_users": len(active_sessions),
        "pending_leave_requests": len([req for req in leave_requests_db if req['status'] == 'pending']),
        "pending_loan_requests": len([req for req in salary_loan_requests_db if req['status'] == 'pending']),
        "pending_time_adjustments": len([req for req in time_adjustment_requests_db if req['status'] == 'pending']),
        "recent_announcements": len([ann for ann in announcements_db if ann['date'] == datetime.now().strftime('%Y-%m-%d')]),
        "timestamp": datetime.now().isoformat()
    }
    
    if user['role'] == 'admin':
        status_data['active_sessions'] = list(active_sessions.values())
    
    return jsonify({"success": True, "status": status_data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

