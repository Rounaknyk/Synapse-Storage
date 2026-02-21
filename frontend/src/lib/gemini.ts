import { GoogleGenerativeAI } from '@google/generative-ai';

const API_KEY = process.env.NEXT_PUBLIC_GEMINI_API_KEY ?? '';

const SYSTEM_PROMPT = `You are a search query optimizer for a semantic document management system.
Your job is to extract the core search intent from a user's natural language query.

Rules:
- Return ONLY the optimized search query — no explanation, no punctuation, no extra text
- Keep it to 4-8 keywords that capture the semantic meaning
- Remove filler words like "find", "show me", "get", "my", "please", "can you"
- Expand abbreviations (Q3 → Q3 quarterly, HR → human resources)
- If the query is already good keywords, return it as-is

Examples:
  "find my Q3 revenue report" → "Q3 quarterly revenue financial report"
  "show me all contract agreements from last year" → "contract agreements legal document"
  "get documents about employee performance reviews" → "employee performance review HR"
  "what are our marketing expenses" → "marketing expenses budget cost"
  "tax documents" → "tax documents"`;

export async function rewriteQuery(userQuery: string): Promise<string> {
  if (!API_KEY) {
    console.warn('[Gemini] No API key set — using original query');
    return userQuery;
  }

  try {
    const genAI = new GoogleGenerativeAI(API_KEY);
    const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });

    const result = await model.generateContent([
      { text: SYSTEM_PROMPT },
      { text: `User query: "${userQuery}"\nOptimized:` },
    ]);

    const rewritten = result.response.text().trim();
    // Safety: if Gemini returns something weird, fall back to original
    if (!rewritten || rewritten.length > 200) return userQuery;
    return rewritten;
  } catch (err) {
    console.error('[Gemini] Query rewrite failed:', err);
    return userQuery; // graceful fallback
  }
}
