/**
 * VELOUR — Auth State Management
 */

const Auth = {
  TOKEN_KEY: 'velour_token',
  USER_KEY:  'velour_user',

  getToken()  { return localStorage.getItem(this.TOKEN_KEY); },
  getUser()   { try { return JSON.parse(localStorage.getItem(this.USER_KEY)); } catch { return null; } },
  isLoggedIn(){ return !!this.getToken(); },

  setSession(token, user) {
    localStorage.setItem(this.TOKEN_KEY, token);
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    window.dispatchEvent(new Event('auth:changed'));
  },

  logout() {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    window.dispatchEvent(new Event('auth:changed'));
    window.location.href = '/auth.html';
  },

  requireAuth() {
    if (!this.isLoggedIn()) {
      window.location.href = '/auth.html?next=' + encodeURIComponent(window.location.pathname);
      return false;
    }
    return true;
  }
};

window.Auth = Auth;
