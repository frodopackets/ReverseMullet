'use client'

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Brain, ChevronDown, ChevronRight } from 'lucide-react';

interface MessageFormatterProps {
  content: string;
  className?: string;
}

export function MessageFormatter({ content, className = '' }: MessageFormatterProps) {
  const [showThinking, setShowThinking] = React.useState(false);
  
  // Parse thinking tags and format content
  const parseMessage = (text: string) => {
    // Check for <thinking> tags
    const thinkingMatch = text.match(/<thinking>([\s\S]*?)<\/thinking>/);
    
    if (thinkingMatch) {
      const thinkingContent = thinkingMatch[1].trim();
      const mainContent = text.replace(/<thinking>[\s\S]*?<\/thinking>/, '').trim();
      
      return {
        hasThinking: true,
        thinking: thinkingContent,
        main: mainContent
      };
    }
    
    // Check for [thinking] format
    const altThinkingMatch = text.match(/\[thinking\]([\s\S]*?)\[\/thinking\]/);
    
    if (altThinkingMatch) {
      const thinkingContent = altThinkingMatch[1].trim();
      const mainContent = text.replace(/\[thinking\][\s\S]*?\[\/thinking\]/, '').trim();
      
      return {
        hasThinking: true,
        thinking: thinkingContent,
        main: mainContent
      };
    }
    
    return {
      hasThinking: false,
      thinking: '',
      main: text
    };
  };
  
  const parsed = parseMessage(content);
  
  // Custom components for markdown rendering
  const markdownComponents = {
    // Style headings
    h1: ({ children, ...props }: any) => (
      <h1 className="text-2xl font-bold mb-3 mt-4" {...props}>{children}</h1>
    ),
    h2: ({ children, ...props }: any) => (
      <h2 className="text-xl font-semibold mb-2 mt-3" {...props}>{children}</h2>
    ),
    h3: ({ children, ...props }: any) => (
      <h3 className="text-lg font-semibold mb-2 mt-2" {...props}>{children}</h3>
    ),
    h4: ({ children, ...props }: any) => (
      <h4 className="text-base font-semibold mb-1 mt-2" {...props}>{children}</h4>
    ),
    // Style paragraphs
    p: ({ children, ...props }: any) => (
      <p className="mb-3 leading-relaxed" {...props}>{children}</p>
    ),
    // Style lists
    ul: ({ children, ...props }: any) => (
      <ul className="list-disc list-inside mb-3 space-y-1" {...props}>{children}</ul>
    ),
    ol: ({ children, ...props }: any) => (
      <ol className="list-decimal list-inside mb-3 space-y-1" {...props}>{children}</ol>
    ),
    li: ({ children, ...props }: any) => (
      <li className="ml-2" {...props}>{children}</li>
    ),
    // Style code blocks
    code: ({ inline, children, ...props }: any) => {
      if (inline) {
        return (
          <code className="px-1.5 py-0.5 rounded bg-muted text-sm font-mono" {...props}>
            {children}
          </code>
        );
      }
      return (
        <code className="block p-3 rounded-lg bg-muted font-mono text-sm overflow-x-auto mb-3" {...props}>
          {children}
        </code>
      );
    },
    // Style blockquotes
    blockquote: ({ children, ...props }: any) => (
      <blockquote className="border-l-4 border-muted-foreground/30 pl-4 italic mb-3" {...props}>
        {children}
      </blockquote>
    ),
    // Style tables
    table: ({ children, ...props }: any) => (
      <div className="overflow-x-auto mb-3">
        <table className="min-w-full divide-y divide-muted" {...props}>
          {children}
        </table>
      </div>
    ),
    thead: ({ children, ...props }: any) => (
      <thead className="bg-muted/50" {...props}>{children}</thead>
    ),
    tbody: ({ children, ...props }: any) => (
      <tbody className="divide-y divide-muted" {...props}>{children}</tbody>
    ),
    tr: ({ children, ...props }: any) => (
      <tr className="hover:bg-muted/30 transition-colors" {...props}>{children}</tr>
    ),
    th: ({ children, ...props }: any) => (
      <th className="px-3 py-2 text-left text-sm font-semibold" {...props}>{children}</th>
    ),
    td: ({ children, ...props }: any) => (
      <td className="px-3 py-2 text-sm" {...props}>{children}</td>
    ),
    // Style horizontal rules
    hr: ({ ...props }: any) => (
      <hr className="my-4 border-muted" {...props} />
    ),
    // Style links
    a: ({ children, href, ...props }: any) => (
      <a 
        href={href} 
        className="text-primary hover:underline" 
        target="_blank" 
        rel="noopener noreferrer"
        {...props}
      >
        {children}
      </a>
    ),
    // Style strong/bold
    strong: ({ children, ...props }: any) => (
      <strong className="font-semibold" {...props}>{children}</strong>
    ),
    // Style emphasis/italic
    em: ({ children, ...props }: any) => (
      <em className="italic" {...props}>{children}</em>
    ),
  };
  
  if (!parsed.hasThinking) {
    return (
      <div className={`prose prose-sm max-w-none ${className}`}>
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={markdownComponents}
        >
          {content}
        </ReactMarkdown>
      </div>
    );
  }
  
  return (
    <div>
      {/* Thinking Section - Collapsible */}
      <div className="mb-3 rounded-lg bg-muted/50 border border-muted">
        <button
          onClick={() => setShowThinking(!showThinking)}
          className="w-full px-3 py-2 flex items-center gap-2 text-left hover:bg-muted/70 transition-colors rounded-lg"
        >
          <Brain className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm font-medium text-muted-foreground">Agent Reasoning</span>
          {showThinking ? (
            <ChevronDown className="h-3 w-3 text-muted-foreground ml-auto" />
          ) : (
            <ChevronRight className="h-3 w-3 text-muted-foreground ml-auto" />
          )}
        </button>
        
        {showThinking && (
          <div className="px-3 pb-2">
            <p className="text-sm text-muted-foreground italic leading-relaxed">
              {parsed.thinking}
            </p>
          </div>
        )}
      </div>
      
      {/* Main Content with Markdown */}
      <div className={`prose prose-sm max-w-none ${className}`}>
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={markdownComponents}
        >
          {parsed.main}
        </ReactMarkdown>
      </div>
    </div>
  );
}