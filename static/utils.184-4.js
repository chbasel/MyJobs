/**
 * A hodge podge of useful utility functions used across site. This is imported
 * in base.html before anything else to ensure that it is globally available.
 **/
var utils = {};
var timer;

/**
 * Returns the value of the cookie. Returns null if that cookie is not found.
 * cookie: The name of the cookie to retreive.
 **/
utils.readCookie = function readCookie(cookie) {
  var nameEQ = cookie + '=';
  var ca = document.cookie.split(';');
  var i;
  var c;
  for (i = 0; i < ca.length; i++) {
    c = ca[i];
    while (c.charAt(0) === ' ') {
      c = c.substring(1, c.length);
    }
    if (c.indexOf(nameEQ) === 0) {
      return c.substring(nameEQ.length, c.length);
    }
  }
  return null;
};

/**
 * Creates a new timer which redirects the user if the `loggedout` cookie is
 * set.
 *
 * url: The url to redirect to.
 **/
utils.logoutTimer = function readCookie(url) {
  if (!timer) {
    if (loggedin) {
      // We were logged in when this was called. Set up our logout timer.
      timer = window.setInterval(function redirect() {
        // if we are logged out and not already on the home page
        // If the loggedout cookie is set, a log out was initiated by the
        // user via.
        // If the exp cookie is missing, the user's session has expired.
        if ((utils.readCookie('loggedout') && window.location.pathname !== url) ||
            ((!utils.readCookie('exp')) && (window.location.pathname !== url))) {
          window.location.assign(url);
        }

      }, 500);
    }
  } else {
    window.clearInterval(timer);
  }
};

utils.setCookie = function(name, value, days) {
  var expires;
  if (days) {
    var date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    expires = '; expires=' + date.toGMTString();
  } else {
    expires = '';
  }

  document.cookie = name + '=' + value + expires + '; path=/';
};
