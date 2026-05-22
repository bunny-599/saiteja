import { Routes, Route, Link } from 'react-router-dom';
import Portal from './pages/Portal.jsx';
import Home from './pages/Home.jsx';
import Analysis from './pages/Analysis.jsx';
import Report from './pages/Report.jsx';
import { ShieldAlert } from 'lucide-react';

function App() {
  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100 selection:bg-teal-500 selection:text-slate-950">
      {/* Header */}
      <header className="border-b border-slate-900 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="p-2 bg-gradient-to-tr from-teal-500 to-blue-600 rounded-xl glow-teal group-hover:scale-105 transition-all">
              <ShieldAlert className="w-6 h-6 text-white" />
            </div>
            <div>
              <span className="font-bold text-xl tracking-tight bg-gradient-to-r from-white via-slate-200 to-teal-400 bg-clip-text text-transparent">
                SKY-SCRAPPER
              </span>
              <span className="block text-[10px] text-slate-500 font-medium uppercase tracking-widest leading-none mt-0.5">
                AI Competitor Intelligence
              </span>
            </div>
          </Link>
          <div className="flex items-center space-x-4 text-sm text-slate-400">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-teal-500/10 text-teal-400 border border-teal-500/20">
              Live Pipeline Active
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow">
        <Routes>
          <Route path="/" element={<Portal />} />
          <Route path="/analyze" element={<Home />} />
          <Route path="/marketing" element={<Home />} />
          <Route path="/future" element={<Home />} />
          <Route path="/analysis/:jobId" element={<Analysis />} />
          <Route path="/report/:jobId" element={<Report />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center text-xs text-slate-500">
          <p>© {new Date().getFullYear()} Sky-Scrapper. Fully Automated Real-time Market Research.</p>
          <p className="mt-2 md:mt-0 flex items-center space-x-4">
            <span>Powered by Claude 3.5 Sonnet</span>
            <span className="w-1 h-1 bg-slate-800 rounded-full"></span>
            <span>Real-time Scraping Engine</span>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
