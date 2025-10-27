/**
 * Share Button Component
 * Allows users to share current view via social media or copy link
 */
import { useState } from 'react';
import { Share2, Copy, Check, Twitter, Linkedin, Facebook } from 'lucide-react';
import {
  generateShareUrl,
  copyToClipboard,
  shareNative,
  getTwitterShareUrl,
  getLinkedInShareUrl,
  getFacebookShareUrl,
  type ViewState,
} from '../utils/share';

interface ShareButtonProps {
  viewState: ViewState;
  className?: string;
}

function ShareButton({ viewState, className = '' }: ShareButtonProps) {
  const [showMenu, setShowMenu] = useState(false);
  const [copied, setCopied] = useState(false);

  const shareUrl = generateShareUrl(viewState);
  const shareText = `Check out this view of the Starlink constellation on Orbital Traffic Analyzer`;

  const handleCopyLink = async () => {
    const success = await copyToClipboard(shareUrl);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleNativeShare = async () => {
    const shared = await shareNative('Orbital Traffic Analyzer', shareText, shareUrl);
    if (shared) {
      setShowMenu(false);
    }
  };

  const handleSocialShare = (url: string) => {
    window.open(url, '_blank', 'width=600,height=400');
    setShowMenu(false);
  };

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setShowMenu(!showMenu)}
        className="flex items-center space-x-1.5 bg-white/5 backdrop-blur-sm hover:bg-white/10 text-white px-3 py-1.5 rounded-lg transition-all border border-white/10 text-sm"
      >
        <Share2 className="w-3.5 h-3.5" />
        <span>Share</span>
      </button>

      {showMenu && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setShowMenu(false)}
          />

          {/* Menu */}
          <div className="absolute right-0 mt-2 w-56 backdrop-blur-xl bg-black/40 border border-white/20 rounded-lg shadow-2xl z-50 animate-fade-in">
            <div className="p-2 space-y-0.5">
              {/* Copy Link */}
              <button
                onClick={handleCopyLink}
                className="w-full flex items-center space-x-2.5 px-3 py-2 hover:bg-white/10 rounded-md text-left transition-all"
              >
                {copied ? (
                  <Check className="w-3.5 h-3.5 text-green-400" />
                ) : (
                  <Copy className="w-3.5 h-3.5 text-gray-400" />
                )}
                <span className="text-xs text-white">
                  {copied ? 'Copied!' : 'Copy Link'}
                </span>
              </button>

              {/* Native Share (if available) */}
              {navigator.share && (
                <button
                  onClick={handleNativeShare}
                  className="w-full flex items-center space-x-2.5 px-3 py-2 hover:bg-white/10 rounded-md text-left transition-all"
                >
                  <Share2 className="w-3.5 h-3.5 text-gray-400" />
                  <span className="text-xs text-white">Share...</span>
                </button>
              )}

              <div className="border-t border-white/10 my-1.5" />

              {/* Social Media */}
              <button
                onClick={() => handleSocialShare(getTwitterShareUrl(shareText, shareUrl))}
                className="w-full flex items-center space-x-2.5 px-3 py-2 hover:bg-white/10 rounded-md text-left transition-all"
              >
                <Twitter className="w-3.5 h-3.5 text-[#1DA1F2]" />
                <span className="text-xs text-white">Share on Twitter</span>
              </button>

              <button
                onClick={() => handleSocialShare(getLinkedInShareUrl(shareUrl))}
                className="w-full flex items-center space-x-2.5 px-3 py-2 hover:bg-white/10 rounded-md text-left transition-all"
              >
                <Linkedin className="w-3.5 h-3.5 text-[#0077B5]" />
                <span className="text-xs text-white">Share on LinkedIn</span>
              </button>

              <button
                onClick={() => handleSocialShare(getFacebookShareUrl(shareUrl))}
                className="w-full flex items-center space-x-2.5 px-3 py-2 hover:bg-white/10 rounded-md text-left transition-all"
              >
                <Facebook className="w-3.5 h-3.5 text-[#1877F2]" />
                <span className="text-xs text-white">Share on Facebook</span>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default ShareButton;

