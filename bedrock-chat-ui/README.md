# Bedrock Knowledge Base Chat UI

A modern, responsive chat interface built with Next.js and shadcn/ui components for interacting with AWS Bedrock Knowledge Bases.

## Features

- 🎨 **Multiple Themed Interfaces**:
  - **Professional UI** - Clean, modern interface for business use
  - **Terminal Mode** - Retro terminal aesthetic for developers  
  - **Bubblegum Mode** - Colorful, playful design for younger users
  - **Medieval Mode** - Dragons, castles, and sorcery themed interface
- 💬 Real-time chat interface with smooth scrolling
- 📚 Multiple knowledge base support with visual selector
- 🔄 Easy knowledge base switching
- 📱 Fully responsive design
- 🎭 Mock backend for development and testing
- 🚀 Ready for AWS Bedrock integration
- ⚡ Static export ready for AWS Amplify deployment

## Tech Stack

- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Icons**: Lucide React
- **Date Handling**: date-fns
- **TypeScript**: Full type safety

## Getting Started

### Prerequisites

- Node.js 18.19.1 or later
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd bedrock-chat-ui
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Theme Access

The application includes four distinct themed interfaces:

- **Professional UI**: `http://localhost:3000/` - Clean, modern interface
- **Terminal Mode**: `http://localhost:3000/terminal` - Retro terminal aesthetic  
- **Bubblegum Mode**: `http://localhost:3000/bubblegum` - Colorful, playful design
- **Medieval Mode**: `http://localhost:3000/medieval` - Dragons, castles, and sorcery theme

Each theme maintains the same functionality with unique visual styling and personality.

## Project Structure

```
src/
├── app/
│   ├── api/                    # API routes (ready for Bedrock integration)
│   │   ├── chat/
│   │   └── knowledge-bases/
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx               # Main chat page
├── components/
│   ├── chat/
│   │   ├── chat-interface.tsx  # Main chat component
│   │   └── knowledge-base-selector.tsx
│   └── ui/                    # shadcn/ui components
└── lib/
    ├── mock-api.ts            # Mock backend for testing
    └── utils.ts               # Utility functions
```

## Components

### ChatInterface
The main chat component that handles:
- Message display with user/assistant differentiation
- Real-time typing indicators
- Message timestamps
- Knowledge base context display

### KnowledgeBaseSelector
Component for selecting and switching between different knowledge bases:
- Grid layout for multiple knowledge bases
- Status indicators (active/inactive)
- Document count display
- Visual selection feedback

## Mock Backend

The application includes a comprehensive mock backend (`src/lib/mock-api.ts`) that simulates:
- Multiple knowledge bases with different domains
- Contextual AI responses based on selected knowledge base
- Realistic API delays
- Error handling

### Mock Knowledge Bases

1. **Product Documentation** - Technical docs and user guides
2. **Customer Support** - FAQ and troubleshooting
3. **Company Policies** - HR policies and procedures
4. **Research Papers** - Academic papers and research
5. **Legal Documents** - Contracts and legal docs
6. **Training Materials** - Educational resources

## AWS Bedrock Integration

The application is structured to easily integrate with AWS Bedrock:

### API Routes
- `/api/chat` - Ready for Bedrock chat completion
- `/api/knowledge-bases` - Ready for Bedrock KB listing

### Integration Points
Replace the mock implementations in:
1. `src/lib/mock-api.ts` - Replace with actual Bedrock SDK calls
2. `src/app/api/chat/route.ts` - Implement Bedrock chat API
3. `src/app/api/knowledge-bases/route.ts` - Implement Bedrock KB listing

### Required Environment Variables
```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
# Or use IAM roles for production
```

## Customization

### Styling
- Modify `src/app/globals.css` for global styles
- Update shadcn/ui theme in `components.json`
- Customize component styles in individual component files

### Adding New Knowledge Bases
Update the mock data in `src/lib/mock-api.ts` or integrate with your Bedrock setup.

### UI Components
Add new shadcn/ui components:
```bash
npx shadcn@latest add [component-name]
```

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Testing the UI

1. Select a knowledge base from the grid
2. Type a message in the chat input
3. Observe the mock AI response
4. Switch between different knowledge bases
5. Test responsive design on different screen sizes

## Production Deployment

1. Build the application:
```bash
npm run build
```

2. Deploy to your preferred platform:
   - Vercel (recommended for Next.js)
   - AWS Amplify
   - Docker container
   - Traditional hosting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.