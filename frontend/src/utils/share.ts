/**
 * Social sharing and URL state management utilities
 */

export interface ViewState {
  lat?: number;
  lon?: number;
  altitude?: number;
  heading?: number;
  pitch?: number;
  selectedSatellite?: number;
  showOrbit?: boolean;
  altitudeFilter?: string;
}

/**
 * Encode view state into URL parameters
 */
export function encodeViewState(state: ViewState): string {
  const params = new URLSearchParams();
  
  if (state.lat !== undefined) params.set('lat', state.lat.toFixed(4));
  if (state.lon !== undefined) params.set('lon', state.lon.toFixed(4));
  if (state.altitude !== undefined) params.set('alt', state.altitude.toFixed(0));
  if (state.heading !== undefined) params.set('h', state.heading.toFixed(2));
  if (state.pitch !== undefined) params.set('p', state.pitch.toFixed(2));
  if (state.selectedSatellite !== undefined) params.set('sat', state.selectedSatellite.toString());
  if (state.showOrbit !== undefined) params.set('orbit', state.showOrbit ? '1' : '0');
  if (state.altitudeFilter !== undefined) params.set('filter', state.altitudeFilter);
  
  return params.toString();
}

/**
 * Decode view state from URL parameters
 */
export function decodeViewState(search: string): ViewState {
  const params = new URLSearchParams(search);
  const state: ViewState = {};
  
  const lat = params.get('lat');
  const lon = params.get('lon');
  const alt = params.get('alt');
  const h = params.get('h');
  const p = params.get('p');
  const sat = params.get('sat');
  const orbit = params.get('orbit');
  const filter = params.get('filter');
  
  if (lat) state.lat = parseFloat(lat);
  if (lon) state.lon = parseFloat(lon);
  if (alt) state.altitude = parseFloat(alt);
  if (h) state.heading = parseFloat(h);
  if (p) state.pitch = parseFloat(p);
  if (sat) state.selectedSatellite = parseInt(sat);
  if (orbit) state.showOrbit = orbit === '1';
  if (filter) state.altitudeFilter = filter;
  
  return state;
}

/**
 * Generate shareable URL for current view
 */
export function generateShareUrl(state: ViewState): string {
  const baseUrl = window.location.origin + window.location.pathname;
  const params = encodeViewState(state);
  return params ? `${baseUrl}?${params}` : baseUrl;
}

/**
 * Copy text to clipboard
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    console.error('Failed to copy to clipboard:', error);
    return false;
  }
}

/**
 * Share via Web Share API (if available)
 */
export async function shareNative(title: string, text: string, url: string): Promise<boolean> {
  if (!navigator.share) {
    return false;
  }
  
  try {
    await navigator.share({ title, text, url });
    return true;
  } catch (error) {
    if ((error as Error).name === 'AbortError') {
      // User cancelled, not an error
      return false;
    }
    console.error('Failed to share:', error);
    return false;
  }
}

/**
 * Generate Twitter share URL
 */
export function getTwitterShareUrl(text: string, url: string): string {
  const params = new URLSearchParams({
    text: text,
    url: url,
  });
  return `https://twitter.com/intent/tweet?${params.toString()}`;
}

/**
 * Generate LinkedIn share URL
 */
export function getLinkedInShareUrl(url: string): string {
  const params = new URLSearchParams({
    url: url,
  });
  return `https://www.linkedin.com/sharing/share-offsite/?${params.toString()}`;
}

/**
 * Generate Facebook share URL
 */
export function getFacebookShareUrl(url: string): string {
  const params = new URLSearchParams({
    u: url,
  });
  return `https://www.facebook.com/sharer/sharer.php?${params.toString()}`;
}

/**
 * Take screenshot of canvas (for Cesium globe)
 */
export function captureScreenshot(canvas: HTMLCanvasElement): string | null {
  try {
    return canvas.toDataURL('image/png');
  } catch (error) {
    console.error('Failed to capture screenshot:', error);
    return null;
  }
}

/**
 * Download data URL as file
 */
export function downloadDataUrl(dataUrl: string, filename: string) {
  const a = document.createElement('a');
  a.href = dataUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

