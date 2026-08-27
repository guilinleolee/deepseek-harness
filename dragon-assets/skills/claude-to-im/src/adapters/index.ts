/**
 * Local adapter index — supplements the npm package's adapters.
 * Side-effect import triggers each adapter's self-registration.
 */

// Weixin adapter must come first so its registerAdapterFactory call runs before
// the bridge manager starts scanning for adapters.
import './weixin-adapter.js';
