export function resolveImageUrl(url) {
  if (!url) return null;
  try {
    const str = String(url);
    return str;
  } catch (e) {
    console.warn('Error resolving image URL:', e);
    return url;
  }
}
