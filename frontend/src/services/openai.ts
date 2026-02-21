// Direct OpenAI API integration (client-side)

import type { CodeChunk } from './clientStorage';

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export const openaiService = {
  // Chat with context
  async chat(
    apiKey: string,
    question: string,
    context: CodeChunk[],
    history: ChatMessage[] = []
  ): Promise<string> {
    if (!apiKey) {
      throw new Error('OpenAI API key is required');
    }

    // Build context from code chunks
    const contextText = context
      .map(chunk => `File: ${chunk.fileName} (lines ${chunk.lineStart}-${chunk.lineEnd})\n\`\`\`${chunk.language}\n${chunk.content}\n\`\`\``)
      .join('\n\n');

    const systemPrompt = `You are a helpful code assistant. Answer questions about the provided code context.

Code Context:
${contextText}

Instructions:
- Answer based on the code context provided
- If the answer is not in the context, say so
- Provide specific file names and line numbers when referencing code
- Keep answers concise and relevant`;

    const messages: ChatMessage[] = [
      { role: 'system', content: systemPrompt },
      ...history,
      { role: 'user', content: question },
    ];

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages,
        temperature: 0.1,
        max_tokens: 1000,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'OpenAI API request failed');
    }

    const data = await response.json();
    return data.choices[0].message.content;
  },

  // Validate API key
  async validateKey(apiKey: string): Promise<boolean> {
    try {
      const response = await fetch('https://api.openai.com/v1/models', {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
        },
      });
      return response.ok;
    } catch {
      return false;
    }
  },
};
