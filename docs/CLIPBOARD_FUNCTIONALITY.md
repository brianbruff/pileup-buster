# Clipboard Functionality - Privacy and Security Considerations

## Overview

The Pileup Buster application now automatically copies the current active callsign to the clipboard when a callsign is moved to the "currently working" state. This feature is designed to improve operator efficiency.

## Implementation Details

### Clipboard API Usage
- **Modern browsers**: Uses the standardized `navigator.clipboard.writeText()` API
- **Older browsers**: Falls back to `document.execCommand('copy')` method
- **Secure context required**: Clipboard API only works in HTTPS or localhost environments

### When Clipboard Copy Occurs
- When a callsign transitions from no active callsign to an active callsign
- When the active callsign changes from one callsign to another
- Does **NOT** copy on initial page load
- Does **NOT** copy when a callsign becomes inactive (null)

## Privacy and Security Considerations

### Browser Permissions
- **Modern browsers**: May prompt users for clipboard access permission on first use
- **User control**: Users can deny or revoke clipboard permissions at any time
- **No persistence**: The application does not store or log clipboard data

### Data Security
- **Scope limited**: Only copies the active callsign (amateur radio call signs are public information)
- **No sensitive data**: No personal information, passwords, or private data is copied
- **Local operation**: Clipboard operations are performed locally in the browser only

### User Privacy
- **Transparent operation**: Console logs indicate when clipboard copy occurs
- **No tracking**: The application does not track or monitor clipboard usage
- **User choice**: Feature operates automatically but respects browser security restrictions

### Browser Compatibility
- **Secure contexts only**: Requires HTTPS in production or localhost in development
- **Graceful degradation**: Falls back to older methods when modern API unavailable
- **Error handling**: Failed clipboard operations are logged but do not affect application functionality

## Recommendations for Operators

1. **HTTPS deployment**: Ensure the application is served over HTTPS for full clipboard functionality
2. **Browser permissions**: Allow clipboard access when prompted for optimal experience
3. **Privacy awareness**: Be aware that the active callsign will be copied to your clipboard automatically
4. **Error monitoring**: Check browser console if clipboard functionality appears not to work

## Technical Implementation

The clipboard functionality is implemented in `/frontend/src/App.tsx` within the `handleCurrentQsoEvent` function, which processes Server-Sent Events for current QSO state changes.

```typescript
// Utility function with modern API and fallback
const copyToClipboard = async (text: string): Promise<void> => {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text)
    } else {
      // Fallback for older browsers
      // ... implementation details
    }
  } catch (err) {
    console.warn('Failed to copy callsign to clipboard:', err)
  }
}
```

This implementation ensures maximum compatibility while respecting user privacy and browser security policies.