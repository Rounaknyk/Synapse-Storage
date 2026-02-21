# 🤖 Botpress Chatbot Integration Plan

## Overview
Integrate Botpress AI chatbot into your Semantic Storage Gateway to provide intelligent document assistance, search help, and user guidance.

---

## 🎯 Use Cases for Your Project

### 1. **Document Search Assistant**
- Natural language document queries
- "Find all financial reports from last month"
- "Show me legal contracts about X"

### 2. **Upload Guidance**
- Help users understand document classification
- Explain similarity scores
- Guide through features

### 3. **FAQ & Support**
- Answer questions about the system
- Troubleshooting help
- Feature explanations

---

## 🚀 Implementation Guide

### Phase 1: Botpress Setup (15-20 minutes)

#### 1.1 Create Botpress Cloud Account
```
1. Visit https://botpress.com
2. Sign up for free account
3. Create new workspace
4. Create new bot: "Synapse Assistant"
```

#### 1.2 Configure Bot Knowledge Base
```
Topics to add:
- Document upload process
- File type support (.pdf, .txt, .md, .docx, .xlsx, etc.)
- Classification categories (finance, legal, general)
- Similarity scores explanation
- Search functionality
- Preview feature
```

#### 1.3 Create Custom Flows

**Flow 1: Document Search Help**
```
Trigger: "search", "find", "look for"
Response:
"I can help you search for documents! 🔍
- Use natural language (e.g., 'tax documents')
- Adjust similarity threshold (60% minimum recommended)
- Results show relevance percentage
- Click 'View' to open the document

What would you like to search for?"
```

**Flow 2: Upload Assistance**
```
Trigger: "upload", "add document", "how to upload"
Response:
"Uploading is easy! 📤

Supported formats:
• PDF, Word (.docx), Excel (.xlsx)
• PowerPoint (.pptx), CSV
• Text files (.txt, .md)

Just drag & drop or click to browse.
Your documents are automatically:
✓ Classified (finance/legal/general)
✓ Indexed for semantic search
✓ Stored securely

Try uploading now!"
```

**Flow 3: Similarity Explanation**
```
Trigger: "similarity", "percentage", "score"
Response:
"Similarity scores show how relevant documents are to your search:

🟢 80-100%: Excellent match
🟡 60-79%: Good match
🔴 <60%: Weak match

The system uses AI embeddings to understand meaning, not just keywords.
That's why 'tax report' finds 'revenue analysis'! 🧠"
```

---

### Phase 2: Backend Integration (30 minutes)

#### 2.1 Create Botpress API Integration

**File:** `backend/services/botpress.py`
```python
import requests
from typing import Optional
from config import settings

class BotpressService:
    def __init__(self):
        self.webhook_url = settings.BOTPRESS_WEBHOOK_URL
        self.bot_id = settings.BOTPRESS_BOT_ID
    
    def send_message(self, user_id: str, message: str) -> dict:
        """Send message to Botpress bot"""
        payload = {
            "type": "text",
            "text": message,
            "userId": user_id
        }
        
        try:
            response = requests.post(
                f"{self.webhook_url}/messages",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            return response.json()
        except Exception as e:
            print(f"Botpress error: {e}")
            return {"error": str(e)}
    
    def get_document_suggestions(self, query: str) -> str:
        """Get AI suggestions for document search"""
        # This would integrate with your search service
        # and provide natural language results
        pass

botpress_service = BotpressService()
```

#### 2.2 Add Environment Variables

**File:** `backend/.env`
```bash
# Botpress Configuration
BOTPRESS_BOT_ID=your_bot_id_here
BOTPRESS_WEBHOOK_URL=https://webhook.botpress.cloud/your_webhook_id
BOTPRESS_API_KEY=your_api_key_here
```

#### 2.3 Create Chat Endpoint (Optional)

**File:** `backend/main.py`
```python
from services.botpress import botpress_service

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"

@app.post("/chat")
async def chat_with_bot(request: ChatRequest):
    """
    Send message to Botpress assistant
    """
    try:
        response = botpress_service.send_message(
            request.user_id, 
            request.message
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )
```

---

### Phase 3: Frontend Integration (30 minutes)

#### 3.1 Install Botpress Webchat

**Two options:**

**Option A: Script Tag (Fastest - 5 minutes)**

**File:** `frontend/src/app/layout.tsx`
```tsx
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        {/* Botpress Webchat */}
        <script 
          src="https://cdn.botpress.cloud/webchat/v1/inject.js"
        ></script>
        <script
          src="https://mediafiles.botpress.cloud/YOUR_BOT_ID/webchat/config.js"
          defer
        ></script>
      </head>
      <body>{children}</body>
    </html>
  );
}
```

**Option B: React Component (More Control)**

1. **Create Chat Component**

**File:** `frontend/src/components/BotpressChat.tsx`
```tsx
'use client';

import { useEffect } from 'react';

export default function BotpressChat() {
  useEffect(() => {
    const script1 = document.createElement('script');
    script1.src = 'https://cdn.botpress.cloud/webchat/v1/inject.js';
    document.body.appendChild(script1);

    script1.onload = () => {
      const script2 = document.createElement('script');
      script2.src = 'https://mediafiles.botpress.cloud/YOUR_BOT_ID/webchat/config.js';
      document.body.appendChild(script2);
      
      script2.onload = () => {
        // Initialize with custom config
        window.botpressWebChat.init({
          botId: 'YOUR_BOT_ID',
          hostUrl: 'https://cdn.botpress.cloud/webchat/v1',
          messagingUrl: 'https://messaging.botpress.cloud',
          clientId: 'YOUR_CLIENT_ID',
          
          // Customization
          botName: 'Synapse Assistant',
          botAvatar: '/bot-avatar.png',
          phoneNumber: null,
          emailAddress: null,
          website: 'https://your-app.com',
          
          // Theme Customization
          stylesheet: 'https://your-app.com/custom-bot-style.css',
          
          // Color scheme (match your app)
          themeColor: '#7c3aed',
          
          // Welcome message
          welcomeMessage: "Hi! I'm your Synapse Assistant 🤖\nAsk me anything about searching, uploading, or managing documents!",
          
          // Position
          composerPlaceholder: 'Ask me anything...',
          showBotInfoPage: true,
          showPoweredBy: false,
        });
      };
    };

    return () => {
      // Cleanup
      window.botpressWebChat?.destroy();
    };
  }, []);

  return null; // Chat widget is injected by Botpress
}
```

2. **Add to Layout**

**File:** `frontend/src/app/layout.tsx`
```tsx
import BotpressChat from '@/components/BotpressChat';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
        <BotpressChat />
      </body>
    </html>
  );
}
```

#### 3.2 Custom Styling (Optional)

**File:** `frontend/public/custom-bot-style.css`
```css
/* Match your app's glass morphism theme */
#bp-web-widget-container {
  font-family: 'Inter', sans-serif !important;
}

#bp-widget-web .bpw-header {
  background: linear-gradient(135deg, #7c3aed, #3b82f6) !important;
}

#bp-widget-web .bpw-layout {
  background: rgba(13, 13, 30, 0.95) !important;
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

#bp-widget-web .bpw-from-bot .bpw-message-container {
  background: rgba(124, 58, 237, 0.15) !important;
  border: 1px solid rgba(124, 58, 237, 0.3);
}

#bp-widget-web .bpw-from-user .bpw-message-container {
  background: linear-gradient(135deg, #7c3aed, #9d60ff) !important;
}
```

---

### Phase 4: Advanced Features (Optional)

#### 4.1 Context-Aware Assistance

Send user context to bot:
```tsx
// When user searches, inform the bot
const handleSearch = async (query: string) => {
  const results = await api.searchDocuments(query);
  
  // Send context to bot
  window.botpressWebChat.sendEvent({
    type: 'proactive-trigger',
    payload: {
      text: `User searched for: "${query}", found ${results.length} results`
    }
  });
};
```

#### 4.2 Suggested Actions

Add quick action buttons in chat:
```javascript
// In Botpress flow
{
  "type": "card",
  "title": "What can I help with?",
  "actions": [
    {
      "label": "🔍 Search Documents",
      "action": "Say",
      "text": "help me search"
    },
    {
      "label": "📤 Upload Guide",
      "action": "Say",
      "text": "how to upload"
    },
    {
      "label": "📊 Explain Scores",
      "action": "Say",
      "text": "what are similarity scores"
    }
  ]
}
```

#### 4.3 Smart Document Recommendations

Integrate with your search API:
```python
# In Botpress webhook handler
@app.post("/botpress/webhook")
async def botpress_webhook(request: dict):
    user_message = request.get("text", "")
    
    # If user asks for documents, search automatically
    if "find" in user_message.lower() or "search" in user_message.lower():
        # Extract search query
        query = extract_search_intent(user_message)
        
        # Perform search
        results = await search_service.search_similar(query, top_k=3)
        
        # Format results for bot
        response = format_results_for_bot(results)
        
        return {"text": response}
```

---

## 🎯 Quick Start Guide (30 Minutes)

For a **hackathon demo**, here's the fastest path:

### 1. Create Bot (10 min)
1. Sign up at botpress.com
2. Create new bot
3. Add 3-5 basic flows (use templates above)
4. Test in Botpress emulator

### 2. Integrate Widget (5 min)
1. Get embed code from Botpress
2. Add script tags to `layout.tsx`
3. Reload app → Chat widget appears!

### 3. Customize (10 min)
1. Change theme color to `#7c3aed`
2. Set welcome message
3. Update bot name and avatar

### 4. Test (5 min)
1. Ask bot sample questions
2. Verify responses
3. Demo ready! 🎉

---

## 💡 Advanced Integration Ideas

### 1. **Voice Commands**
- Enable Botpress voice input
- "Search for tax documents" → triggers search

### 2. **Proactive Suggestions**
- When user uploads document: "Great! Want to search for similar files?"
- When search returns no results: "Try adjusting similarity threshold"

### 3. **Analytics Dashboard**
- Track common questions
- Improve bot responses
- User behavior insights

### 4. **Multi-language Support**
- Detect user language
- Translate bot responses
- Global accessibility

---

## 📊 Expected Benefits

### User Experience:
- ✅ 24/7 instant help
- ✅ Reduced learning curve
- ✅ Interactive guidance
- ✅ Conversational search

### Hackathon Demo:
- ✅ **"Wow factor"** - AI assistant impresses judges
- ✅ Shows forward-thinking approach
- ✅ Demonstrates user-centric design
- ✅ Differentiator from competitors

---

## 🔗 Resources

- **Botpress Docs:** [botpress.com/docs](https://botpress.com/docs)
- **Webchat SDK:** [botpress.com/docs/messaging-channels/web-chat](https://botpress.com/docs/messaging-channels/web-chat)
- **API Reference:** [botpress.com/docs/api-documentation](https://botpress.com/docs/api-documentation)

---

## ⚡ Performance Tips

1. **Lazy Load**: Only load bot widget after main content
2. **Mobile Optimization**: Test chat UX on mobile
3. **Caching**: Cache common responses
4. **Fallback**: Have manual help docs as backup

---

## ✅ Hackathon Recommendation

**Minimum Viable Integration (30 min):**
1. ✅ Create bot with 5 basic flows
2. ✅ Add script tag to layout
3. ✅ Customize theme color
4. ✅ Test 3 common questions
5. ✅ **Demo ready!**

**Enhanced Version (2 hours):**
- All above +
- Custom styling
- Context awareness
- Backend integration
- Smart suggestions

**ROI:** Medium-High impact, adds AI/chatbot credibility to your project! 🤖✨

---

## 🎬 Demo Script

During hackathon presentation:

> "And here's something cool - we have an AI assistant!" 
> 
> *[Click chat widget]*
> 
> "Ask it anything..."
> 
> *[Type: "how do I search for documents?"]*
> 
> *[Bot responds with helpful guide]*
> 
> "It can help users navigate the system, explain features, and even suggest searches. Fully integrated AI support!"

**Judges love this!** 🏆

---

**Next Steps:**
1. Sign up at [botpress.com](https://botpress.com)
2. Create your bot
3. Add conversation flows
4. Integrate webchat widget
5. Test and polish
6. Ship it! 🚀
