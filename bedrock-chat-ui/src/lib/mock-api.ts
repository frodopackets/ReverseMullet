import { KnowledgeBase } from '@/components/chat/knowledge-base-selector'
import { Message } from '@/components/chat/chat-interface'

// Mock knowledge bases
export const mockKnowledgeBases: KnowledgeBase[] = [
  {
    id: 'kb-1',
    name: 'Product Documentation',
    description: 'Technical documentation and user guides for our products',
    status: 'active',
    documentCount: 156
  },
  {
    id: 'kb-2',
    name: 'Customer Support',
    description: 'FAQ, troubleshooting guides, and support procedures',
    status: 'active',
    documentCount: 89
  },
  {
    id: 'kb-3',
    name: 'Company Policies',
    description: 'HR policies, procedures, and company guidelines',
    status: 'active',
    documentCount: 42
  },
  {
    id: 'kb-4',
    name: 'Research Papers',
    description: 'Academic papers and research documents',
    status: 'inactive',
    documentCount: 234
  },
  {
    id: 'kb-5',
    name: 'Legal Documents',
    description: 'Contracts, agreements, and legal documentation',
    status: 'active',
    documentCount: 67
  },
  {
    id: 'kb-6',
    name: 'Training Materials',
    description: 'Employee training content and educational resources',
    status: 'active',
    documentCount: 123
  }
]

// Mock responses for different knowledge bases
const mockResponses: Record<string, string[]> = {
  'kb-1': [
    "Based on our product documentation, here's what I found...",
    "According to the technical specifications, this feature works by...",
    "The user guide indicates that you should follow these steps...",
    "Our API documentation shows that this endpoint requires...",
    "The troubleshooting section suggests checking these components..."
  ],
  'kb-2': [
    "From our customer support knowledge base, the most common solution is...",
    "This is a frequently asked question. The recommended approach is...",
    "Our support team typically resolves this by...",
    "Based on similar customer cases, you should try...",
    "The support documentation recommends these troubleshooting steps..."
  ],
  'kb-3': [
    "According to company policy, the procedure for this is...",
    "Our HR guidelines state that employees should...",
    "The company handbook specifies that...",
    "Based on our organizational policies, the correct process is...",
    "The employee manual indicates that..."
  ],
  'kb-4': [
    "The research literature suggests that...",
    "According to recent academic studies...",
    "The peer-reviewed papers in our database indicate...",
    "Research findings show that...",
    "Academic consensus points to..."
  ],
  'kb-5': [
    "From a legal perspective, the relevant regulations state...",
    "The contract terms specify that...",
    "Legal precedent suggests that...",
    "According to the applicable laws...",
    "The legal documentation indicates..."
  ],
  'kb-6': [
    "Our training materials recommend that you...",
    "The educational resources suggest starting with...",
    "Based on our learning modules, the best practice is...",
    "The training curriculum covers this topic by...",
    "Our instructional content indicates that..."
  ]
}

// Simulate API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

export async function sendMessage(
  message: string, 
  knowledgeBaseId: string
): Promise<Message> {
  // Simulate API call delay
  await delay(1000 + Math.random() * 2000)
  
  const knowledgeBase = mockKnowledgeBases.find(kb => kb.id === knowledgeBaseId)
  const responses = mockResponses[knowledgeBaseId] || mockResponses['kb-1']
  
  // Generate a contextual response
  let response = responses[Math.floor(Math.random() * responses.length)]
  
  // Add some context based on the user's message
  if (message.toLowerCase().includes('how')) {
    response += " Here's a step-by-step approach:\n\n1. First, identify the key requirements\n2. Then, review the relevant documentation\n3. Finally, implement the recommended solution"
  } else if (message.toLowerCase().includes('what')) {
    response += " This involves several key components that work together to provide the functionality you're looking for."
  } else if (message.toLowerCase().includes('why')) {
    response += " This is designed this way to ensure optimal performance and user experience."
  } else {
    response += " Let me know if you need more specific information about any aspect of this topic."
  }

  return {
    id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    content: response,
    role: 'assistant',
    timestamp: new Date(),
    knowledgeBase: knowledgeBase?.name
  }
}

export async function getKnowledgeBases(): Promise<KnowledgeBase[]> {
  // Simulate API call delay
  await delay(500)
  return mockKnowledgeBases
}