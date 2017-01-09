import {debounce} from 'lodash-compat/function';

export function typingDebounce(fn) {
  return debounce(fn, 300, {leading: false, trailing: true});
}
