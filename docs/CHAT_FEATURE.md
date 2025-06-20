# Chat Feature Documentation

## Overview

The Pileup Buster application now includes a real-time chat feature that allows ham radio operators to communicate with each other directly within the platform. This feature leverages the existing Server-Sent Events (SSE) infrastructure for real-time messaging.

## Features

### Core Functionality
- **Real-time messaging**: Messages appear instantly for all users using SSE
- **Multiple chat rooms**: Support for different channels (general, pileup, etc.)
- **Callsign integration**: Automatic callsign setting when joining the queue
- **Mobile responsive**: Chat interface works on all device sizes

### User Features
- Send and receive messages in real-time
- Switch between different chat rooms
- Set custom callsign for chat (if different from queue registration)
- View message history
- See timestamp for each message

### Admin Features (Requires Admin Login)
- Create new chat rooms
- Delete individual messages
- Clear entire chat rooms
- Moderate chat content

## Technical Implementation

### Backend Architecture

#### Database Collections
- **chat_messages**: Stores individual chat messages
  - `room_name`: The chat room name
  - `callsign`: User's callsign
  - `message`: Message content
  - `message_type`: Type of message (message, join, leave, system)
  - `timestamp`: When the message was sent
  - `deleted`: Soft delete flag for moderation

- **chat_rooms**: Stores chat room information
  - `name`: Room name (unique identifier)
  - `description`: Room description
  - `created_by`: Who created the room
  - `created_at`: Creation timestamp
  - `active`: Whether the room is active
  - `message_count`: Total number of messages

#### API Endpoints

**Public Endpoints:**
- `GET /api/chat/rooms` - Get list of available chat rooms
- `GET /api/chat/rooms/{room_name}/messages` - Get messages from a room
- `POST /api/chat/messages` - Send a message to a room

**Admin Endpoints (require authentication):**
- `POST /api/chat/rooms` - Create a new chat room
- `DELETE /api/chat/messages` - Delete a specific message
- `DELETE /api/chat/rooms/{room_name}/clear` - Clear all messages in a room

#### Real-time Events
The chat system extends the existing SSE event system with two new event types:
- `chat_message`: Broadcast when a new message is sent
- `chat_room_update`: Broadcast when rooms are created/modified

### Frontend Components

#### Chat Component (`/src/components/Chat.tsx`)
Main chat container that manages:
- Room selection and display
- User callsign setting
- Admin functions
- Error handling

#### ChatRoom Component (`/src/components/ChatRoom.tsx`)
Individual chat room interface:
- Message display with auto-scroll
- Message input form
- Real-time message updates via SSE
- Admin moderation controls

#### ChatMessage Component (`/src/components/ChatMessage.tsx`)
Individual message display:
- Formatted timestamp
- System message styling
- Admin delete button
- Deleted message handling

### Validation and Security

#### Input Validation
- **Callsigns**: Must match ITU amateur radio standards
- **Messages**: Maximum 500 characters, cannot be empty
- **Room names**: Alphanumeric + hyphens/underscores only, max 50 characters

#### Security Measures
- Admin authentication required for moderation actions
- Input sanitization and validation
- Soft deletion for message moderation
- Room access control

## Usage Guide

### For Operators

1. **Setting Your Callsign**
   - Register in the queue to automatically set your chat callsign
   - Or click "Set Callsign for Chat" to manually enter your callsign

2. **Sending Messages**
   - Select a chat room from the sidebar
   - Type your message in the input field
   - Press Enter or click Send

3. **Changing Rooms**
   - Click on any room in the sidebar to switch
   - Message history loads automatically

### For Administrators

1. **Creating Chat Rooms**
   - Log in as admin
   - Click the "+" button in the chat sidebar
   - Enter room name and description

2. **Moderating Content**
   - Click the "×" button next to any message to delete it
   - Use "Clear Room" to remove all messages from a room

## Default Chat Rooms

The system automatically creates two default chat rooms:

- **general**: General chat for all operators
- **pileup**: Chat room specifically for operators in the queue

## Integration with Existing Features

The chat feature integrates seamlessly with the existing application:

- **Queue Registration**: Automatically sets chat callsign
- **Admin System**: Uses existing authentication for moderation
- **SSE Infrastructure**: Extends current real-time event system
- **UI Theme**: Matches existing light/dark theme support
- **Mobile Layout**: Responsive design consistent with existing components

## API Examples

### Send a Message
```bash
curl -X POST http://localhost:8000/api/chat/messages \
  -H "Content-Type: application/json" \
  -d '{
    "callsign": "W1AW",
    "message": "Hello from the pileup!",
    "room_name": "general"
  }'
```

### Get Messages
```bash
curl http://localhost:8000/api/chat/rooms/general/messages?limit=20
```

### Create Room (Admin)
```bash
curl -X POST http://localhost:8000/api/chat/rooms \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic <base64-credentials>" \
  -d '{
    "name": "dx-chat",
    "description": "Chat for DX operators"
  }'
```

## Testing

The chat feature includes comprehensive tests:
- Endpoint functionality tests
- Input validation tests
- Event broadcasting tests
- Integration tests with existing system

Run tests with:
```bash
cd backend
python -m pytest tests/test_chat.py -v
```

## Performance Considerations

- Message history is limited to prevent excessive memory usage
- SSE connections are efficiently managed
- Database queries are optimized with proper indexing
- Frontend components use React best practices for performance

## Future Enhancements

Potential improvements for future versions:
- Private messaging between users
- Message search functionality
- File/image sharing
- Message reactions/emojis
- User status indicators (online/offline)
- Message persistence settings
- Enhanced moderation tools