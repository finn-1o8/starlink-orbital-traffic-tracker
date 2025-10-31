/**
 * Coming Soon Component
 * Placeholder for future projects
 */
import { Link } from 'react-router-dom';
import { ArrowLeft, Rocket } from 'lucide-react';

interface ComingSoonProps {
  projectName?: string;
}

function ComingSoon({ projectName = 'Project' }: ComingSoonProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-space-900 via-space-800 to-space-900 flex items-center justify-center p-6">
      <div className="max-w-2xl w-full text-center">
        {/* Back Button */}
        <Link
          to="/"
          className="inline-flex items-center space-x-2 text-gray-400 hover:text-cyan-400 transition-colors mb-12"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Home</span>
        </Link>

        {/* Coming Soon Content */}
        <div className="backdrop-blur-xl bg-black/20 border border-white/10 rounded-2xl p-12 shadow-2xl">
          <div className="relative mb-8">
            <Rocket className="w-24 h-24 mx-auto text-cyan-400 mb-6 animate-pulse" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-32 h-32 rounded-full bg-cyan-400/20 blur-2xl animate-pulse" />
            </div>
          </div>

          <h1 className="text-4xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
            Coming Soon
          </h1>
          
          <p className="text-xl text-gray-300 mb-8">
            {projectName} is currently in development
          </p>
          
          <p className="text-gray-400 mb-8">
            This project is being crafted with precision and attention to detail.
            <br />
            Check back soon for updates!
          </p>

          <Link
            to="/"
            className="inline-flex items-center space-x-2 px-6 py-3 bg-cyan-400/20 hover:bg-cyan-400/30 text-cyan-300 rounded-lg border border-cyan-400/30 transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Return Home</span>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default ComingSoon;

