import { defineStore } from 'pinia'
import request from '@/utils/request'
import { initSocket, disconnectSocket, on, off } from '@/utils/socket'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    unreadCount: 0
  }),
  getters: {
    isLogin: (state) => !!state.user
  },
  actions: {
    _setupSocket() {
      if (!this.user) return
      initSocket(this.user.id)
      const cb = (msg) => {
        if (msg.receiver_id === this.user.id) {
          this.unreadCount++
        }
      }
      off('new_message', this._unreadCb)
      this._unreadCb = on('new_message', cb)
    },
    async restore() {
      try {
        const res = await request.get('/auth/me')
        if (res.code === 0 && res.data) {
          this.user = res.data
          this._setupSocket()
        }
      } catch (_) {
        // ignore
      }
    },
    async login(credentials) {
      const res = await request.post('/auth/login', credentials)
      this.user = res.data
      this._setupSocket()
      return res.data
    },
    async register(data) {
      const res = await request.post('/auth/register', data)
      this.user = res.data
      this._setupSocket()
      return res.data
    },
    async logout() {
      try {
        await request.post('/auth/logout')
      } catch (_) {}
      this.user = null
      this.unreadCount = 0
      if (this._unreadCb) {
        off('new_message', this._unreadCb)
        this._unreadCb = null
      }
      disconnectSocket()
      localStorage.removeItem('swap_user')
    },
    addUnread() {
      this.unreadCount++
    },
    setUnreadCount(count) {
      this.unreadCount = count
    },
    resetUnread() {
      this.unreadCount = 0
    }
  }
})
