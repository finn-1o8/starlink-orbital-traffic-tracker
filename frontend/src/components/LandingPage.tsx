/**
 * Landing Page Component
 * Welcome page with project selection
 */
import { useNavigate, Link } from 'react-router-dom';
import { Satellite, Rocket, Code2, Mail, Github } from 'lucide-react';
import { useState, useEffect } from 'react';

function LandingPage() {
  const navigate = useNavigate();
  const [hoveredProject, setHoveredProject] = useState<number | null>(null);
  const [radius, setRadius] = useState(160);

  useEffect(() => {
    const updateRadius = () => {
      const width = window.innerWidth;
      setRadius(Math.min(180, Math.max(120, width * 0.22)));
    };
    updateRadius();
    window.addEventListener('resize', updateRadius);
    return () => window.removeEventListener('resize', updateRadius);
  }, []);

  const projects = [
    {
      id: 1,
      title: 'Starlink Tracker',
      description: 'Real-time orbital traffic visualization',
      icon: Satellite,
      path: '/tracker',
      color: 'from-cyan-400 to-blue-600',
      available: true,
    },
    {
      id: 2,
      title: 'Project Alpha',
      description: 'Coming soon...',
      icon: Rocket,
      path: '#',
      color: 'from-purple-400 to-pink-600',
      available: false,
    },
    {
      id: 3,
      title: 'Project Beta',
      description: 'Coming soon...',
      icon: Code2,
      path: '#',
      color: 'from-green-400 to-emerald-600',
      available: false,
    },
  ];

  const handleProjectClick = (project: typeof projects[0]) => {
    if (project.available) {
      navigate(project.path);
    }
  };

  // Prevent swipe navigation and browser history gestures
  useEffect(() => {
    let touchStartX = 0;
    let touchStartY = 0;
    
    // Prevent touch-based swipe navigation
    const handleTouchStart = (e: TouchEvent) => {
      if (e.touches.length === 1) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
      }
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (e.touches.length === 1) {
        const touchX = e.touches[0].clientX;
        const touchY = e.touches[0].clientY;
        const diffX = touchX - touchStartX;
        const diffY = touchY - touchStartY;
        
        // If horizontal movement is greater than vertical, prevent it
        if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 10) {
          e.preventDefault();
        }
      }
    };

    // Prevent mouse wheel horizontal scrolling
    const handleWheel = (e: WheelEvent) => {
      if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) {
        e.preventDefault();
      }
    };

    // Prevent browser navigation gestures (Safari, Chrome)
    const handleGestureStart = (e: Event) => {
      e.preventDefault();
    };

    // Block popstate (browser back/forward)
    const handlePopState = (e: PopStateEvent) => {
      // If we're on landing page and trying to go back, prevent it
      if (window.location.pathname === '/') {
        window.history.pushState(null, '', '/');
      }
    };

    // Push initial state to prevent back navigation
    window.history.pushState(null, '', window.location.href);

    // Add all event listeners
    document.addEventListener('touchstart', handleTouchStart, { passive: false });
    document.addEventListener('touchmove', handleTouchMove, { passive: false });
    document.addEventListener('wheel', handleWheel, { passive: false });
    document.addEventListener('gesturestart', handleGestureStart, { passive: false });
    window.addEventListener('popstate', handlePopState);
    
    return () => {
      document.removeEventListener('touchstart', handleTouchStart);
      document.removeEventListener('touchmove', handleTouchMove);
      document.removeEventListener('wheel', handleWheel);
      document.removeEventListener('gesturestart', handleGestureStart);
      window.removeEventListener('popstate', handlePopState);
    };
  }, []);

  return (
    <div 
      className="min-h-screen w-screen bg-gradient-to-br from-space-900 via-space-800 to-space-900 flex flex-col items-center justify-center relative overflow-x-hidden"
      style={{ 
        touchAction: 'pan-y pinch-zoom',
        overscrollBehaviorX: 'none',
        overscrollBehavior: 'none'
      }}
    >
      {/* Animated background stars */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(50)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-white rounded-full animate-twinkle"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              opacity: Math.random() * 0.8 + 0.2,
            }}
          />
        ))}
      </div>

      {/* Main Content */}
      <div className="relative z-10 text-center px-4 w-full flex flex-col items-center justify-between h-full py-3">
        {/* Header */}
        <div className="mt-2 md:mt-4 animate-fade-in">
          <h1 className="text-3xl md:text-5xl lg:text-6xl font-bold mb-1 md:mb-2 bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
            Karman Labs
          </h1>
          <p className="text-sm md:text-lg text-gray-300 mb-0.5">
            Satellite & Geospatial Engineering
          </p>
          <p className="text-[10px] md:text-xs text-gray-400">
            Space systems, big data and ML
          </p>
        </div>

        {/* Project Selection Circle */}
        <div className="relative w-full flex-1 flex items-center justify-center max-w-2xl mx-auto my-2">
          <div className="relative w-full max-w-[500px] aspect-square">
            {/* Center orb (stays in place) */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-20 h-20 md:w-24 md:h-24 rounded-full bg-gradient-to-br from-cyan-400/20 to-blue-600/20 backdrop-blur-xl border border-white/20 flex items-center justify-center z-10">
              <div className="w-12 h-12 md:w-16 md:h-16 rounded-full bg-gradient-to-br from-cyan-400 to-blue-600 opacity-30 blur-xl animate-pulse" />
            </div>

            {/* Rotating container for projects */}
            <div className="absolute top-1/2 left-1/2 w-full h-full animate-orbit">
              {projects.map((project, index) => {
                const angle = (index * 120 - 90) * (Math.PI / 180); // 120 degrees apart
                const x = Math.cos(angle) * radius;
                const y = Math.sin(angle) * radius;
                const Icon = project.icon;
                const isHovered = hoveredProject === project.id;

                return (
                  <div
                    key={project.id}
                    className="absolute"
                    style={{
                      left: '50%',
                      top: '50%',
                      transform: `translate(calc(-50% + ${x}px), calc(-50% + ${y}px))`,
                    }}
                  >
                    <button
                      onClick={() => handleProjectClick(project)}
                      onMouseEnter={() => setHoveredProject(project.id)}
                      onMouseLeave={() => setHoveredProject(null)}
                      disabled={!project.available}
                      className={`
                        group relative w-32 h-32 md:w-40 md:h-40 rounded-full
                        backdrop-blur-xl bg-black/30 border-2
                        flex flex-col items-center justify-center
                        transition-all duration-300
                        ${project.available 
                          ? `border-white/20 hover:border-white/40 hover:scale-110 cursor-pointer ${isHovered ? 'shadow-2xl shadow-cyan-500/50' : ''}` 
                          : 'border-white/10 opacity-60 cursor-not-allowed'
                        }
                        ${isHovered ? `bg-gradient-to-br ${project.color} bg-opacity-20` : ''}
                      `}
                    >
                      {/* Glow effect */}
                      {isHovered && project.available && (
                        <div className={`absolute inset-0 rounded-full bg-gradient-to-br ${project.color} opacity-20 blur-xl`} />
                      )}

                      {/* Content wrapper with counter-rotation */}
                      <div className="animate-counter-orbit flex flex-col items-center justify-center relative z-10">
                        <Icon className={`w-7 h-7 md:w-10 md:h-10 mb-1 md:mb-2 transition-all ${project.available ? `text-cyan-400 group-hover:text-white group-hover:scale-110` : 'text-gray-500'}`} />
                        
                        <h3 className={`text-xs md:text-sm font-semibold mb-0.5 ${project.available ? 'text-white' : 'text-gray-500'}`}>
                          {project.title}
                        </h3>
                        
                        <p className={`text-[9px] md:text-[10px] ${project.available ? 'text-gray-300' : 'text-gray-600'}`}>
                          {project.description}
                        </p>
                      </div>

                      {!project.available && (
                        <div className="absolute inset-0 flex items-center justify-center z-20 animate-counter-orbit">
                          <span className="text-[9px] text-gray-500 bg-black/50 px-2 py-0.5 rounded-full">
                            Coming Soon
                          </span>
                        </div>
                      )}
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Footer Links */}
        <div className="flex items-center justify-center space-x-6 md:space-x-8 text-gray-400 mb-2 md:mb-4">
          <Link
            to="/contact"
            className="flex items-center space-x-2 hover:text-cyan-400 transition-colors text-sm md:text-base"
          >
            <Mail className="w-4 h-4 md:w-5 md:h-5" />
            <span>Contact</span>
          </Link>
          <a
            href="https://github.com/finn-1o8"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-2 hover:text-cyan-400 transition-colors text-sm md:text-base"
          >
            <Github className="w-4 h-4 md:w-5 md:h-5" />
            <span>GitHub</span>
          </a>
        </div>
      </div>

      {/* Floating particles */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-2 h-2 bg-cyan-400/30 rounded-full animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${Math.random() * 10 + 10}s`,
            }}
          />
        ))}
      </div>
    </div>
  );
}

export default LandingPage;

