import {isEqual} from 'lodash-compat/lang';
import {map, filter} from 'lodash-compat/collection';
import {diffLines} from 'diff';


/**
 * Compare two objects deeply for equality.
 *
 * If the objects are different, fail with a message highlighting
 * the differences between the two objects.
 */
function toDiffEqual(util, customEqualityTesters) {
  return {
    compare: (actual, expected) => {
      if (isEqual(actual, expected)) {
        return {pass: true};
      }

      function stringify(object) {
        if (typeof object === 'undefined') {
          return 'undefined';
        }
        // JSON.stringify censors keys with undefined values by default.
        // This behavior results in isEqual returning false, but the json
        // diff not having any differences. This function puts a placeholder
        // string in those keys.
        function replacer(key, value) {
          if (typeof value === 'undefined') {
            return '--undefined--';
          } else {
            return value;
          }
        }
        return JSON.stringify(object, replacer, 2);
      }

      const expectedString = stringify(expected);
      const actualString = stringify(actual);
      const diff = diffLines(
        actualString, expectedString,
        {newLineIsToken: true});

      function prefixLines(prefix, string) {
        const lines = string.split('\n');
        return map(lines, l => prefix + l + "\n");
      }

      const message = "Differences found:\n" +
        map(diff, (part) =>
          prefixLines(
            part.added ? '-' : part.removed ? '+' : ' ',
            part.value).join('')).join('');
      return {pass: false, message};
    },
  };
}

beforeEach(() => {
  jasmine.addMatchers({toDiffEqual});
});

