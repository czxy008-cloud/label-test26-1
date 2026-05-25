import { io } from 'socket.io-client'

let socket = null
let currentUserId = null
const listeners = {}

export function initSocket(userId) {
  if (socket && currentUserId === userId) return socket
  if (socket) {
    try { socket.disconnect() } catch (_) {}
    socket = null
  }
  currentUserId = userId
  socket = io({
    path: '/socket.io',
    transports: ['websocket', 'polling'],
    withCredentials: true,
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: 10
  })
  socket.on('connect', () => {
    if (currentUserId) {
      socket.emit('join_user', { user_id: currentUserId })
    }
  })
  socket.on('new_message', (msg) => {
    const cbs = listeners['new_message'] || []
    cbs.forEach((cb) => {
      try { cb(msg) } catch (e) { console.error('socket listener error', e) }
    })
  })
  socket.on('disconnect', () => {
    // socket.io 会自动重连，无需手动处理
  })
  return socket
}

export function disconnectSocket() {
  if (socket) {
    try { socket.disconnect() } catch (_) {}
    socket = null
    currentUserId = null
  }
}

export function on(event, cb) {
  if (!listeners[event]) listeners[event] = []
  listeners[event].push(cb)
  return cb
}

export function off(event, cb) {
  if (!listeners[event]) return
  if (!cb) {
    delete listeners[event]
    return
  }
  listeners[event] = listeners[event].filter((fn) => fn !== cb)
  if (listeners[event].length === 0) delete listeners[event]
}

export function getSocket() {
  return socket
}

export function isConnected() {
  return !!(socket && socket.connected)
}
