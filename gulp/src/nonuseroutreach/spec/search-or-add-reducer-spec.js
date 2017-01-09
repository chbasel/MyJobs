import reducer, {defaultState} from '../reducers/search-or-add-reducer';

import {
  resetSearchOrAddAction,
  searchUpdateAction,
  searchSettledAction,
  searchResultsReceivedAction,
  searchResultSelectedAction,
  addToActiveIndexAction,
  setActiveIndexAction,
} from '../actions/search-or-add-actions';

describe('searchOrAddReducer', () => {
  describe('handling resetSearchOrAddAction', () => {
    const result = reducer({}, resetSearchOrAddAction('a'));

    it('should set the default state.', () => {
      expect(result).toDiffEqual({a: {state: 'RESET'}});
    });
  });

  describe('handling searchUpdateAction', () => {
    const result = reducer({}, searchUpdateAction('a', 'asdf'));

    it('should mark state as preloading.', () => {
      expect(result.a.state).toEqual('PRELOADING');
    });

    it('should include the new text', () => {
      expect(result.a.searchString).toEqual('asdf');
    });
  });

  describe('handling searchSettledAction', () => {
    const result = reducer({}, searchSettledAction('a', 4));

    it('should mark state as loading.', () => {
      expect(result.a.state).toEqual('LOADING');
    });

    it('should note the loading id.', () => {
      expect(result.a.loadingId).toEqual(4);
    });
  });

  describe('handling searchResultsReceived', () => {
    const searchResults = [
      {value: 'a', display: 'A'},
      {value: 'b', display: 'B'},
    ];
    const result = reducer({
      a: {loadingId: 2},
    }, searchResultsReceivedAction('a', searchResults, 2));

    it('should mark state as received.', () => {
      expect(result.a.state).toEqual('RECEIVED');
    });

    it('should contain the search results', () => {
      expect(result.a.results).toEqual(searchResults);
    });

    it('should reset activeIndex', () => {
      expect(result.a.activeIndex).toEqual(0);
    });
  });

  describe('handling a stale searchResultsReceived', () => {
    const searchResults = [
      {value: 'a', display: 'A'},
      {value: 'b', display: 'B'},
    ];
    const result = reducer({
      a: {loadingId: 2},
    }, searchResultsReceivedAction('a', searchResults, 1));

    it('should leave state alone.', () => {
      expect(result.state).not.toBeDefined();
    });

    it('should not contain the search results', () => {
      expect(result.results).not.toBeDefined();
    });
  });

  describe('handling searchResultSelectedAction', () => {
    const selected = {value: 'a', display: 'A'};
    const result = reducer({}, searchResultSelectedAction('a', selected));

    it('should mark state as selected.', () => {
      expect(result.a.state).toEqual('SELECTED');
    });

    it('should contain the selected result', () => {
      expect(result.a.selected).toEqual(selected);
    });
  });

  describe('activeIndex', () => {
    describe('moving', () => {
      const state = {
        a: {
          results: [null, null, null],
          activeIndex: 1,
        },
      };

      it('should increment the index', () => {
        const result = reducer(state, addToActiveIndexAction('a', 1));
        expect(result.a.activeIndex).toEqual(2);
      });

      it('should increment the index from zero', () => {
        const state = {
          a: {
            results: [null, null, null],
            activeIndex: 0,
          },
        };
        const result = reducer(state, addToActiveIndexAction('a', 1));
        expect(result.a.activeIndex).toEqual(1);
      });

      it('should decrement the index', () => {
        const result = reducer(state, addToActiveIndexAction('a', -1));
        expect(result.a.activeIndex).toEqual(0);
      });

      describe('should constrain the index to valid result indicies', () => {
        it('up', () => {
          const result = reducer(state, addToActiveIndexAction('a', 100));
          expect(result.a.activeIndex).toEqual(2);
        });

        it('down', () => {
          const result = reducer(state, addToActiveIndexAction('a', -100));
          expect(result.a.activeIndex).toEqual(0);
        });
      });

      it('should handle missing activeIndex', () => {
        const state = {
          a: {
            results: [null, null, null],
          },
        };
        const result = reducer(state, addToActiveIndexAction('a', -1));
        expect(result.a.activeIndex).toEqual(0);
      });

      it('should become null when results are empty', () => {
        const state = {
          a: {
            results: [],
            activeIndex: 0,
          },
        };
        const result = reducer(state, addToActiveIndexAction('a', -1));
        expect(result.a.activeIndex).toBeNull();
      });

      it('should become null when results are missing', () => {
        const state = {
          a: {
            activeIndex: 0,
          },
        };
        const result = reducer(state, addToActiveIndexAction('a', -1));
        expect(result.a.activeIndex).toBeNull();
      });
    });

    describe('setting', () => {
      const state = {
        a: {
          results: [null, null, null],
          activeIndex: 1,
        },
      };

      it('should set the index', () => {
        const result = reducer(state, setActiveIndexAction('a', 1));
        expect(result.a.activeIndex).toEqual(1);
      });

      describe('should constrain the index to valid result indicies', () => {
        it('up', () => {
          const result = reducer(state, setActiveIndexAction('a', 100));
          expect(result.a.activeIndex).toEqual(2);
        });

        it('down', () => {
          const result = reducer(state, setActiveIndexAction('a', -100));
          expect(result.a.activeIndex).toEqual(0);
        });
      });

      it('should handle missing activeIndex', () => {
        const state = {
          a: {
            results: [null, null, null],
          },
        };
        const result = reducer(state, setActiveIndexAction('a', 2));
        expect(result.a.activeIndex).toEqual(2);
      });

      it('should become null when results are empty', () => {
        const state = {
          a: {
            results: [],
            activeIndex: 0,
          },
        };
        const result = reducer(state, setActiveIndexAction('a', 0));
        expect(result.a.activeIndex).toBeNull();
      });

      it('should become null when results are missing', () => {
        const state = {
          a: {
            activeIndex: 0,
          },
        };
        const result = reducer(state, setActiveIndexAction('a', 0));
        expect(result.a.activeIndex).toBeNull();
      });
    });
  });
});

