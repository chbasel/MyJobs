// Defined in a Django template.
const staticUrlBase = window.staticUrl;

/**
 * Return the correct static url for a static asset given a relative path.
 *
 * relativePath: a string like 'images/ajax-loader.gif'
 */
export function expandStaticUrl(relativePath) {
  return staticUrlBase + '/' + relativePath;
}
