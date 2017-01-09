import {polyfill as es6PromisePolyfill} from 'es6-promise';
import 'fetch-polyfill';

// Put as many polyfills here as we can.
//
// ES5-shim/sham and babel/polyfill probably have to be part of the bundling
// environment.

export function installPolyfills() {
    // This gives us the Promise API.
  es6PromisePolyfill();

  // Needed on ie8 to make sure fetch can find Promise.
  if (!fetch.Promise) {
    fetch.Promise = window.Promise;
  }

    // IE8 doesn't define console unless the debugger is active.
  if (!window.console) {
    window.console = {
      log: () => {},
      error: () => {},
    };
  }

    // IE8 doesn't have Date.now()
  if (!Date.now) {
    Date.now = () => new Date().getTime();
  }

  // IE8 doesn't support Add & Remove event listener
  /*
    The original code for this Event Listener Pollyfill can be found here: https://gist.github.com/jonathantneal/3748027
  */
  if ( !window.addEventListener) {
    (function fixIE8(WindowPrototype, DocumentPrototype, ElementPrototype, addEventListener, removeEventListener, dispatchEvent, registry) {
      WindowPrototype[addEventListener] = DocumentPrototype[addEventListener] = ElementPrototype[addEventListener] = function prototype(type, listener) {
        const target = this;

        registry.unshift([target, type, listener, (event) => {
          event.currentTarget = target;
          event.preventDefault = function preventDefault() { event.returnValue = false; };
          event.stopPropagation = function stopPropagation() { event.cancelBubble = true; };
          event.target = event.srcElement || target;

          listener.call(target, event);
        }]);

        this.attachEvent('on' + type, registry[0][3]);
      };

      WindowPrototype[removeEventListener] = DocumentPrototype[removeEventListener] = ElementPrototype[removeEventListener] = function eventListener(type, listener) {
        for (let index = 0, register; register === registry[index]; ++index) {
          if (register[0] === this && register[1] === type && register[2] === listener) {
            return this.detachEvent('on' + type, registry.splice(index, 1)[0][3]);
          }
        }
      };

      WindowPrototype[dispatchEvent] = DocumentPrototype[dispatchEvent] = ElementPrototype[dispatchEvent] = function dispatchEventIE8(eventObject) {
        return this.fireEvent('on' + eventObject.type, eventObject);
      };
    })(Window.prototype, HTMLDocument.prototype, Element.prototype, 'addEventListener', 'removeEventListener', 'dispatchEvent', []);
  }
}
