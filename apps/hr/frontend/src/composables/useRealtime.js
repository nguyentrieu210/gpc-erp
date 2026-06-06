import { onMounted, onUnmounted } from 'vue'
import { io } from 'socket.io-client'

export function useRealtime(doctypes, onEvent) {
  let socket = null

  function connect() {
    const port = 9000
    socket = io(`http://${window.location.hostname}:${port}`, {
      transports: ['polling', 'websocket'],
      reconnection: true,
      reconnectionDelay: 3000,
      reconnectionAttempts: 10,
    })

    socket.on('connect', () => {
      console.log('[realtime] connected to', port)
      // Subscribe to specific doctypes
      if (doctypes && doctypes.length) {
        socket.emit('doc_subscribe', doctypes)
      }
    })

    // Frappe publishes events as: { doctype, docname, ... }
    const events = ['doc_update', 'doc_insert', 'doc_delete', 'doc_submit', 'doc_cancel']
    for (const evt of events) {
      socket.on(evt, (data) => {
        if (!doctypes || doctypes.includes(data?.doctype)) {
          console.log('[realtime]', evt, data?.doctype, data?.docname)
          onEvent && onEvent(evt, data)
        }
      })
    }

    // Also listen for frappe-style events
    socket.on('event', (data) => {
      if (data?.doctype && (!doctypes || doctypes.includes(data.doctype))) {
        onEvent && onEvent('event', data)
      }
    })

    socket.on('disconnect', (reason) => {
      console.log('[realtime] disconnected:', reason)
    })

    socket.on('connect_error', (e) => {
      console.warn('[realtime] connect error:', e.message)
    })
  }

  function disconnect() {
    socket && socket.close()
    socket = null
  }

  onMounted(() => connect())
  onUnmounted(() => disconnect())

  return { connect, disconnect }
}
