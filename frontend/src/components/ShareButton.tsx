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
        className="flex items-center space-x-2 bg-space-700 hover:bg-space-600 text-white px-4 py-2 rounded-lg transition-colors"
      >
        <Share2 className="w-4 h-4" />
        <span className="text-sm">Share</span>
      </button>

      {showMenu && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setShowMenu(false)}
          />

          {/* Menu */}
          <div className="absolute right-0 mt-2 w-64 bg-space-700 border border-space-600 rounded-lg shadow-xl z-50 animate-fade-in">
            <div className="p-2 space-y-1">
              {/* Copy Link */}
              <button
                onClick={handleCopyLink}
                className="w-full flex items-center space-x-3 px-3 py-2 hover:bg-space-600 rounded text-left transition-colors"
              >
                {copied ? (
                  <Check className="w-4 h-4 text-accent-green" />
                ) : (
                  <Copy className="w-4 h-4 text-gray-400" />
                )}
                <span className="text-sm text-white">
                  {copied ? 'Copied!' : 'Copy Link'}
                </span>
              </button>

              {/* Native Share (if available) */}
              {navigator.share && (
                <button
                  onClick={handleNativeShare}
                  className="w-full flex items-center space-x-3 px-3 py-2 hover:bg-space-600 rounded text-left transition-colors"
                >
                  <Share2 className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-white">Share...</span>
                </button>
              )}

              <div className="border-t border-space-600 my-2" />

              {/* Social Media */}
              <button
                onClick={() => handleSocialShare(getTwitterShareUrl(shareText, shareUrl))}
                className="w-full flex items-center space-x-3 px-3 py-2 hover:bg-space-600 rounded text-left transition-colors"
              >
                <Twitter className="w-4 h-4 text-[#1DA1F2]" />
                <span className="text-sm text-white">Share on Twitter</span>
              </button>

              <button
                onClick={() => handleSocialShare(getLinkedInShareUrl(shareUrl))}
                className="w-full flex items-center space-x-3 px-3 py-2 hover:bg-space-600 rounded text-left transition-colors"
              >
                <Linkedin className="w-4 h-4 text-[#0077B5]" />
                <span className="text-sm text-white">Share on LinkedIn</span>
              </button>

              <button
                onClick={() => handleSocialShare(getFacebookShareUrl(shareUrl))}
                className="w-full flex items-center space-x-3 px-3 py-2 hover:bg-space-600 rounded text-left transition-colors"
              >
                <Facebook className="w-4 h-4 text-[#1877F2]" />
                <span className="text-sm text-white">Share on Facebook</span>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default ShareButton;

