# ReverseMullet

A collection of AWS Bedrock Knowledge Base chat interfaces with multiple themes and styles.

## Projects

### 🚀 Bedrock Chat UI

A modern Next.js chat application for interacting with AWS Bedrock Knowledge Bases, featuring multiple themed interfaces:

- **🎨 UI Mode** - Clean, modern interface with shadcn/ui components
- **💻 Terminal Mode** - Retro terminal-style interface for developers
- **🌈 Bubblegum Mode** - Playful, colorful interface perfect for younger users

**Location:** `bedrock-chat-ui/`

**Features:**
- TypeScript + Next.js 14
- Tailwind CSS styling
- Dark/light theme support
- Mock API for development
- Responsive design
- Real-time chat interface
- Knowledge base selection

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ReverseMullet
```

2. Navigate to the chat UI project:
```bash
cd bedrock-chat-ui
```

3. Install dependencies:
```bash
npm install
```

4. Run the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

### Available Interfaces

- **Main UI**: `http://localhost:3000` - Modern, professional interface
- **Terminal**: `http://localhost:3000/terminal` - Developer-friendly terminal theme
- **Bubblegum**: `http://localhost:3000/bubblegum` - Fun, colorful theme for kids

## Project Structure

```
ReverseMullet/
├── bedrock-chat-ui/           # Next.js chat application
│   ├── src/
│   │   ├── app/               # Next.js app router pages
│   │   │   ├── page.tsx       # Main UI interface
│   │   │   ├── terminal/      # Terminal-themed interface
│   │   │   └── bubblegum/     # Bubblegum-themed interface
│   │   ├── components/        # React components
│   │   │   ├── chat/          # Chat-specific components
│   │   │   └── ui/            # shadcn/ui components
│   │   └── lib/               # Utilities and mock API
│   ├── public/                # Static assets
│   └── README.md              # Project-specific documentation
└── README.md                  # This file
```

## Technologies Used

- **Frontend**: Next.js 14, React, TypeScript
- **Styling**: Tailwind CSS, shadcn/ui
- **Icons**: Lucide React
- **Development**: Mock API for testing

## Features

### Chat Interface
- Real-time messaging simulation
- Message history
- Typing indicators
- Responsive design
- Multiple themes

### Knowledge Base Management
- Visual knowledge base selector
- Status indicators (active/inactive)
- Document count display
- Easy switching between knowledge bases

### Theming
- **UI Mode**: Professional, clean design with green accent colors
- **Terminal Mode**: Retro terminal aesthetic with monospace fonts
- **Bubblegum Mode**: Playful design with gradients, emojis, and animations

## Development

### Mock API

The application includes a mock API (`src/lib/mock-api.ts`) that simulates:
- Knowledge base retrieval
- Message sending and responses
- Contextual AI responses based on selected knowledge base

### Adding New Themes

To add a new theme:

1. Create new components in `src/components/chat/`:
   - `[theme]-chat-interface.tsx`
   - `[theme]-knowledge-base-selector.tsx`

2. Create a new page in `src/app/[theme]/page.tsx`

3. Add navigation links to the main page

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test across all themes
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Future Enhancements

- [ ] Real AWS Bedrock integration
- [ ] User authentication
- [ ] Message persistence
- [ ] File upload support
- [ ] Additional themes
- [ ] Mobile app version
- [ ] Voice input/output
- [ ] Multi-language support

## Support

For questions or issues, please open a GitHub issue or contact the development team.