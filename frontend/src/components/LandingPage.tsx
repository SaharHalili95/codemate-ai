import { MessageSquare, Search, Upload, Zap, Github, ArrowRight, Code2, Database, Brain } from 'lucide-react';

interface LandingPageProps {
  onLaunch: () => void;
}

const features = [
  {
    icon: Upload,
    title: 'Upload Your Code',
    description: 'Drop in any code files — Python, TypeScript, Java, Go, Rust and more. The system parses and chunks them intelligently.',
  },
  {
    icon: Brain,
    title: 'RAG-Powered Understanding',
    description: 'Your code is converted into vector embeddings via OpenAI and stored in ChromaDB for semantic retrieval.',
  },
  {
    icon: Search,
    title: 'Semantic Search',
    description: 'Search across your entire codebase in natural language. Find functions, patterns, and logic instantly.',
  },
  {
    icon: MessageSquare,
    title: 'AI Chat on Your Code',
    description: 'Ask GPT-4 anything about your codebase. It retrieves the most relevant context and gives precise answers.',
  },
];

const steps = [
  { number: '01', title: 'Upload', description: 'Upload your code files to the assistant' },
  { number: '02', title: 'Index', description: 'Code is parsed, chunked, and embedded into a vector store' },
  { number: '03', title: 'Ask', description: 'Ask questions in plain English — get answers with code context' },
];

const techStack = ['FastAPI', 'OpenAI GPT-4', 'ChromaDB', 'React', 'TypeScript', 'Tailwind CSS', 'Railway', 'Vercel'];

export default function LandingPage({ onLaunch }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white">

      {/* Nav */}
      <nav className="max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="bg-blue-500 p-1.5 rounded-lg">
            <Code2 className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-lg">CodeMate AI</span>
        </div>
        <div className="flex items-center gap-4">
          <a
            href="https://github.com/SaharHalili95/codemate-ai"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-slate-300 hover:text-white transition-colors text-sm"
          >
            <Github className="w-4 h-4" />
            GitHub
          </a>
          <button
            onClick={onLaunch}
            className="bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            Launch App
          </button>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-20 pb-24 text-center">
        <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 text-blue-300 text-sm px-4 py-1.5 rounded-full mb-6">
          <Zap className="w-3.5 h-3.5" />
          RAG-Powered Code Assistant
        </div>

        <h1 className="text-5xl sm:text-6xl font-bold leading-tight mb-6">
          Chat with your
          <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
            codebase
          </span>
        </h1>

        <p className="text-slate-400 text-lg max-w-2xl mx-auto mb-10 leading-relaxed">
          Upload code files and ask questions in plain English.
          Semantic search + GPT-4 retrieves the right context and gives precise answers — no more digging through files.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            onClick={onLaunch}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-7 py-3.5 rounded-xl transition-colors text-base"
          >
            Try It Now
            <ArrowRight className="w-4 h-4" />
          </button>
          <a
            href="https://github.com/SaharHalili95/codemate-ai"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-semibold px-7 py-3.5 rounded-xl transition-colors text-base"
          >
            <Github className="w-4 h-4" />
            View Source
          </a>
        </div>
      </section>

      {/* How it works */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-center text-2xl font-bold mb-12 text-slate-100">How it works</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          {steps.map((step) => (
            <div key={step.number} className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <div className="text-4xl font-bold text-blue-500/40 mb-3">{step.number}</div>
              <h3 className="text-lg font-semibold mb-2">{step.title}</h3>
              <p className="text-slate-400 text-sm leading-relaxed">{step.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-center text-2xl font-bold mb-12 text-slate-100">Features</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <div key={feature.title} className="bg-white/5 border border-white/10 rounded-2xl p-6 flex gap-4">
                <div className="bg-blue-500/10 p-2.5 rounded-xl h-fit">
                  <Icon className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <h3 className="font-semibold mb-1.5">{feature.title}</h3>
                  <p className="text-slate-400 text-sm leading-relaxed">{feature.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* RAG Pipeline */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <div className="bg-white/5 border border-white/10 rounded-2xl p-8">
          <div className="flex items-center gap-3 mb-6">
            <Database className="w-5 h-5 text-blue-400" />
            <h2 className="text-xl font-bold">RAG Pipeline</h2>
          </div>
          <div className="flex flex-wrap items-center gap-3 text-sm">
            {[
              'Parse Code',
              'Chunk & Tokenize',
              'OpenAI Embeddings',
              'ChromaDB Vector Store',
              'Semantic Retrieval',
              'GPT-4 Generation',
            ].map((step, i, arr) => (
              <div key={step} className="flex items-center gap-3">
                <span className="bg-blue-500/10 border border-blue-500/20 text-blue-300 px-3 py-1.5 rounded-lg">
                  {step}
                </span>
                {i < arr.length - 1 && <ArrowRight className="w-4 h-4 text-slate-600" />}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-center text-2xl font-bold mb-8 text-slate-100">Tech Stack</h2>
        <div className="flex flex-wrap justify-center gap-3">
          {techStack.map((tech) => (
            <span
              key={tech}
              className="bg-white/5 border border-white/10 text-slate-300 px-4 py-2 rounded-lg text-sm"
            >
              {tech}
            </span>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-6xl mx-auto px-6 py-16 text-center">
        <div className="bg-gradient-to-r from-blue-600/20 to-cyan-600/20 border border-blue-500/20 rounded-2xl p-12">
          <h2 className="text-3xl font-bold mb-4">Ready to explore your codebase?</h2>
          <p className="text-slate-400 mb-8">Bring your OpenAI API key and start asking questions.</p>
          <button
            onClick={onLaunch}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-8 py-4 rounded-xl transition-colors text-base mx-auto"
          >
            Launch CodeMate AI
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="max-w-6xl mx-auto px-6 py-8 border-t border-white/10 flex items-center justify-between text-sm text-slate-500">
        <span>Built by <a href="https://github.com/SaharHalili95" target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-white transition-colors">Sahar Halili</a></span>
        <a href="https://github.com/SaharHalili95/codemate-ai" target="_blank" rel="noopener noreferrer" className="flex items-center gap-1.5 hover:text-slate-300 transition-colors">
          <Github className="w-4 h-4" />
          View on GitHub
        </a>
      </footer>
    </div>
  );
}
