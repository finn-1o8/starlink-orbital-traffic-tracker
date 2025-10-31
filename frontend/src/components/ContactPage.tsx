/**
 * Contact Page Component
 */
import { Link } from 'react-router-dom';
import { ArrowLeft, Mail, Github, MapPin, Briefcase, GraduationCap } from 'lucide-react';

function ContactPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-space-900 via-space-800 to-space-900 flex items-center justify-center p-6">
      <div className="max-w-3xl w-full backdrop-blur-xl bg-black/20 border border-white/10 rounded-2xl p-8 md:p-12 shadow-2xl">
        {/* Back Button */}
        <Link
          to="/"
          className="inline-flex items-center space-x-2 text-gray-400 hover:text-cyan-400 transition-colors mb-8"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Home</span>
        </Link>

        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
            Let's Connect
          </h1>
          <p className="text-gray-300">
            Satellite & Geospatial Software Engineer
          </p>
        </div>

        {/* Contact Info Cards */}
        <div className="space-y-6 mb-12">
          {/* Email */}
          <a
            href="mailto:finanwmkl@gmail.com"
            className="flex items-center space-x-4 p-6 backdrop-blur-sm bg-white/5 rounded-lg border border-white/10 hover:border-cyan-400/50 hover:bg-white/10 transition-all group"
          >
            <div className="w-12 h-12 rounded-lg bg-cyan-400/20 flex items-center justify-center group-hover:bg-cyan-400/30 transition-colors">
              <Mail className="w-6 h-6 text-cyan-400" />
            </div>
            <div className="flex-1">
              <p className="text-sm text-gray-400 mb-1">Email</p>
              <p className="text-lg font-medium text-white">finanwmkl@gmail.com</p>
            </div>
          </a>

          {/* GitHub */}
          <a
            href="https://github.com/finn-1o8"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-4 p-6 backdrop-blur-sm bg-white/5 rounded-lg border border-white/10 hover:border-cyan-400/50 hover:bg-white/10 transition-all group"
          >
            <div className="w-12 h-12 rounded-lg bg-cyan-400/20 flex items-center justify-center group-hover:bg-cyan-400/30 transition-colors">
              <Github className="w-6 h-6 text-cyan-400" />
            </div>
            <div className="flex-1">
              <p className="text-sm text-gray-400 mb-1">GitHub</p>
              <p className="text-lg font-medium text-white">github.com/finn-1o8</p>
            </div>
          </a>

          {/* Location */}
          <div className="flex items-center space-x-4 p-6 backdrop-blur-sm bg-white/5 rounded-lg border border-white/10">
            <div className="w-12 h-12 rounded-lg bg-cyan-400/20 flex items-center justify-center">
              <MapPin className="w-6 h-6 text-cyan-400" />
            </div>
            <div className="flex-1">
              <p className="text-sm text-gray-400 mb-1">Location</p>
              <p className="text-lg font-medium text-white">London, UK</p>
            </div>
          </div>
        </div>

        {/* About Section */}
        <div className="border-t border-white/10 pt-8">
          <h2 className="text-2xl font-semibold text-white mb-6">About</h2>
          
          <div className="space-y-6 text-gray-300">
            <div className="flex items-start space-x-4">
              <Briefcase className="w-5 h-5 text-cyan-400 mt-1 flex-shrink-0" />
              <div>
                <p className="font-medium text-white mb-1">Expertise</p>
                <p className="text-sm">
                  Satellite Systems Engineering | RF/DSP | Applied AI in Remote Sensing | 
                  Cloud-native geospatial pipelines | Software Engineering
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <GraduationCap className="w-5 h-5 text-cyan-400 mt-1 flex-shrink-0" />
              <div>
                <p className="font-medium text-white mb-1">Education</p>
                <p className="text-sm">
                  MSc Satellite Systems Engineering (University of Bradford, UK) | 
                  BEng Computer Engineering
                </p>
              </div>
            </div>

            <p className="text-sm leading-relaxed pt-4">
              I bridge advanced software engineering with satellite systems and AI-driven geospatial analysis. 
              From RF front-ends and link budgets to cloud-native raster pipelines and remote sensing ML, 
              I build systems that scale — both in orbit and on the ground.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ContactPage;

